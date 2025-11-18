#!/usr/bin/env python3
"""Enhanced CLI console for DSPy-Agent-Framework with SSE streaming support."""

# Standard library imports
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Local imports
from .dspy_modules.supervisor import DSPySupervisor
from .evaluation import Evaluator
from .utils.compiler import compile_supervisor
from .utils.config_loader import get_agent_model, load_config
from .utils.logger import setup_logger
from .utils.tool_registry import ToolRegistry
from .workflows.supervisor_workflow import SupervisorWorkflow, WorkflowConfig

# Allow running as a script (python src/agentic_fleet/console.py) by configuring package context
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    __package__ = "agentic_fleet"


# Suppress OpenTelemetry OTLP log export errors early (before any imports trigger setup)
logging.getLogger("opentelemetry.exporter.otlp.proto.grpc.exporter").setLevel(logging.CRITICAL)
logging.getLogger("opentelemetry.sdk._logs._internal").setLevel(logging.CRITICAL)

# Load environment variables
load_dotenv()

# Initialize Rich console and Typer
console = Console()
app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="DSPy-Agent-Framework CLI - Intelligent Multi-Agent Workflows",
)
logger = logging.getLogger(__name__)


def _init_tracing() -> dict[str, Any]:
    """Initialize tracing (idempotent). Returns loaded config."""
    cfg = load_config()
    try:
        from .utils.tracing import initialize_tracing

        initialize_tracing(cfg)
    except Exception as exc:  # pragma: no cover - tracing optional
        logger.debug(f"Tracing initialization skipped: {exc}")
    return cfg


class WorkflowRunner:
    """Manages workflow execution and display."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.workflow: Optional[SupervisorWorkflow] = None
        self.console = Console()
        self.current_agents: List[str] = []

    async def initialize_workflow(
        self,
        compile_dspy: bool = True,
        max_rounds: int = 15,
        model: Optional[str] = None,
        enable_handoffs: Optional[bool] = None,
    ) -> SupervisorWorkflow:
        """Initialize the workflow with configuration."""

        # Load config from YAML
        yaml_config = load_config()

        opt_cfg = yaml_config.get("dspy", {}).get("optimization", {})
        examples_path = opt_cfg.get("examples_path", "data/supervisor_examples.json")
        use_gepa = opt_cfg.get("use_gepa", False)
        # --- GEPA exclusivity resolution ---
        auto_choice = opt_cfg.get("gepa_auto")
        full_evals_choice = opt_cfg.get("gepa_max_full_evals")
        metric_calls_choice = opt_cfg.get("gepa_max_metric_calls")
        # If auto is defined prefer it and nullify others; else prefer whichever
        # explicit limit is set
        if auto_choice:
            full_evals_choice = None
            metric_calls_choice = None
        elif full_evals_choice is not None:
            auto_choice = None
            metric_calls_choice = None
        elif metric_calls_choice is not None:
            auto_choice = None
            full_evals_choice = None
        # Determine effective model early (needed for reflection fallback)
        effective_model = model or yaml_config.get("dspy", {}).get("model", "gpt-5-mini")
        # Build final optimization options
        reflection_model_value = (
            opt_cfg.get("gepa_reflection_model") or effective_model if use_gepa else None
        )
        # Determine final auto value respecting exclusivity and avoiding implicit 'light'
        if auto_choice is not None:
            final_auto = auto_choice
        elif full_evals_choice is not None or metric_calls_choice is not None:
            final_auto = None  # numeric limit chosen
        else:
            final_auto = "light"  # safe default when nothing provided

        optimization_options: Dict[str, Any] = {
            "auto": final_auto,
            "max_full_evals": full_evals_choice,
            "max_metric_calls": metric_calls_choice,
            "reflection_model": reflection_model_value,
            "log_dir": opt_cfg.get("gepa_log_dir", "logs/gepa"),
            "perfect_score": opt_cfg.get("gepa_perfect_score", 1.0),
            "use_history_examples": opt_cfg.get("gepa_use_history_examples", False),
            "history_min_quality": opt_cfg.get("gepa_history_min_quality", 8.0),
            "history_limit": opt_cfg.get("gepa_history_limit", 200),
            "val_split": opt_cfg.get("gepa_val_split", 0.2),
            "seed": opt_cfg.get("gepa_seed", 13),
            "max_bootstrapped_demos": opt_cfg.get("max_bootstrapped_demos", 4),
        }
        if optimization_options.get("reflection_model") is None:
            optimization_options.pop("reflection_model", None)

        # effective_model already determined above

        # Build WorkflowConfig from YAML and CLI arguments
        history_file = yaml_config.get("logging", {}).get(
            "history_file", "logs/execution_history.jsonl"
        )
        history_format = "jsonl" if str(history_file).endswith(".jsonl") else "json"

        handoffs_cfg = (
            yaml_config.get("workflow", {}).get("handoffs", {})
            if isinstance(yaml_config.get("workflow"), dict)
            else {}
        )
        handoffs_enabled = (
            enable_handoffs if enable_handoffs is not None else handoffs_cfg.get("enabled", True)
        )

        config = WorkflowConfig(
            max_rounds=max_rounds,
            max_stalls=yaml_config.get("workflow", {}).get("supervisor", {}).get("max_stalls", 3),
            max_resets=yaml_config.get("workflow", {}).get("supervisor", {}).get("max_resets", 2),
            enable_streaming=yaml_config.get("workflow", {})
            .get("supervisor", {})
            .get("enable_streaming", True),
            parallel_threshold=yaml_config.get("workflow", {})
            .get("execution", {})
            .get("parallel_threshold", 3),
            dspy_model=effective_model,
            compile_dspy=compile_dspy,
            refinement_threshold=yaml_config.get("workflow", {})
            .get("quality", {})
            .get("refinement_threshold", 8.0),
            enable_refinement=yaml_config.get("workflow", {})
            .get("quality", {})
            .get("enable_refinement", True),
            judge_threshold=yaml_config.get("workflow", {})
            .get("quality", {})
            .get("judge_threshold", 7.0),
            enable_judge=yaml_config.get("workflow", {})
            .get("quality", {})
            .get("enable_judge", True),
            max_refinement_rounds=yaml_config.get("workflow", {})
            .get("quality", {})
            .get("max_refinement_rounds", 2),
            judge_model=yaml_config.get("workflow", {}).get("quality", {}).get("judge_model"),
            judge_reasoning_effort=yaml_config.get("workflow", {})
            .get("quality", {})
            .get("judge_reasoning_effort", "medium"),
            enable_completion_storage=yaml_config.get("openai", {}).get(
                "enable_completion_storage", False
            ),
            agent_models={
                agent_name.lower(): get_agent_model(yaml_config, agent_name, effective_model)
                for agent_name in ["researcher", "analyst", "writer", "reviewer"]
            },
            agent_temperatures={
                agent_name.lower(): yaml_config.get("agents", {})
                .get(agent_name.lower(), {})
                .get("temperature")
                for agent_name in ["researcher", "analyst", "writer", "reviewer"]
            },
            history_format=history_format,
            examples_path=examples_path,
            dspy_optimizer="gepa" if use_gepa else "bootstrap",
            gepa_options=optimization_options,
            enable_handoffs=handoffs_enabled,
        )

        with self.console.status("[bold green]Initializing DSPy-Enhanced Workflow..."):
            workflow = SupervisorWorkflow(config)
            await workflow.initialize(compile_dspy=compile_dspy)

        self.workflow = workflow
        return workflow

    async def run_with_streaming(self, message: str) -> None:
        """Run workflow with streaming display."""

        if not self.workflow:
            await self.initialize_workflow()

        assert self.workflow is not None, "Workflow initialization failed"

        # Track execution
        start_time = datetime.now()
        current_agent = None
        agent_outputs = {}

        # Display task
        self.console.print(
            Panel(
                Markdown(f"**Task:** {message}"),
                title="[bold blue]Processing Request",
                border_style="blue",
            )
        )

        # Stream events
        with Live(console=self.console, refresh_per_second=4) as live:
            # Use Any to avoid static type conflict when switching between Text and Panel
            from typing import Any as _Any

            status_text: _Any = Text()

            try:
                async for event in self.workflow.run_stream(message):
                    event_type = type(event).__name__

                    # Handle different event types based on agent-framework
                    if hasattr(event, "agent_id"):
                        current_agent = event.agent_id  # type: ignore[attr-defined]
                        if current_agent not in agent_outputs:
                            agent_outputs[current_agent] = ""

                    if hasattr(event, "text"):
                        # Streaming text from agent
                        if current_agent:
                            # type: ignore[attr-defined]
                            agent_outputs[current_agent] += event.text or ""
                            status_text = self._format_agent_output(
                                current_agent,
                                agent_outputs[current_agent],
                            )
                            live.update(status_text)

                    elif hasattr(event, "message"):
                        # Complete message from agent
                        if event.message and hasattr(event.message, "text"):  # type: ignore[attr-defined]
                            # Show full output without truncation
                            self.console.print(
                                Panel(
                                    event.message.text,  # type: ignore[attr-defined]
                                    title=f"[bold green]{current_agent}",
                                    border_style="green",
                                )
                            )

                    elif hasattr(event, "data"):
                        # Final result
                        if self.verbose:
                            self.console.print(
                                f"[dim]Event: {event_type}[/dim]",
                                style="dim",
                            )

            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/bold red]")
                if self.verbose:
                    logger.exception("Workflow error")

        # Display execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        self.console.print(f"\n[dim]Execution time: {execution_time:.2f}s[/dim]")

    async def run_without_streaming(self, message: str) -> Dict[str, Any]:
        """Run workflow without streaming and return complete result."""

        if not self.workflow:
            await self.initialize_workflow()

        assert self.workflow is not None, "Workflow initialization failed"

        with self.console.status("[bold green]Processing..."):
            result = await self.workflow.run(message)

        return result

    def _format_agent_output(self, agent: str, text: str) -> Panel:
        """Format agent output for display."""
        # Show full output without truncation
        return Panel(
            Text(text),
            title=f"[bold yellow]{agent} (streaming...)",
            border_style="yellow",
        )


@app.command()
def handoff(
    interactive: bool = typer.Option(False, "--interactive", help="Interactive handoff session"),
    compile_dspy: bool = typer.Option(True, "--compile", help="Compile DSPy modules"),
    model: Optional[str] = typer.Option(None, "--model", help="Override model ID"),
) -> None:
    """Handoff-centric workflow mode.

    Explore and create agent-to-agent handoffs with the HandoffManager.

    Examples:
      console.py handoff            # start interactive session
      console.py handoff --no-interactive  # just initialize (useful for smoke tests)
    """

    setup_logger("dspy_agent_framework", "INFO")
    _init_tracing()

    async def start_session():
        runner = WorkflowRunner(verbose=False)
        await runner.initialize_workflow(
            compile_dspy=compile_dspy, model=model, enable_handoffs=True
        )

        wf = runner.workflow
        assert wf is not None
        wf.enable_handoffs = True  # ensure on regardless of defaults

        if not wf.handoff_manager:
            console.print("[red]HandoffManager not available[/red]")
            return

        # Show agents and quick help
        agents_list = ", ".join(wf.agents.keys())
        console.print(
            Panel(
                f"[bold]Handoff Mode[/bold]\nAgents: {agents_list}\n\n"
                "Enter 'exit' to quit, 'help' for available agents.\n"
                "Press enter on any prompt to skip.",
                title="Handoff Session",
                border_style="blue",
            )
        )

        if not interactive:
            return

        # Create case-insensitive agent lookup
        agent_lookup = {name.lower(): name for name in wf.agents.keys()}

        while True:
            from_agent_input = console.input("From agent> ").strip()

            # Check for exit
            if from_agent_input.lower() in {"exit", "quit"}:
                break

            # Check for help
            if from_agent_input.lower() == "help":
                console.print(f"[cyan]Available agents: {agents_list}[/cyan]")
                continue

            # Skip empty input
            if not from_agent_input:
                continue

            # Case-insensitive agent lookup
            from_agent = agent_lookup.get(from_agent_input.lower())

            if not from_agent:
                console.print(
                    f"[yellow]Unknown agent '{from_agent_input}'. "
                    f"Available agents: {agents_list}[/yellow]"
                )
                continue

            remaining_work = console.input("Describe remaining work> ").strip()
            work_completed = console.input("Summarize completed work> ").strip()

            # Available agents map (exclude current)
            available = {
                name: getattr(wf.agents[name], "description", name)
                for name in wf.agents
                if name != from_agent
            }

            next_agent = await wf.handoff_manager.evaluate_handoff(
                current_agent=from_agent,
                work_completed=work_completed,
                remaining_work=remaining_work,
                available_agents=available,
            )

            if next_agent:
                console.print(f"[green]Recommended → {next_agent}[/green]")
                do_pkg = console.input("Create handoff package? [y/N]> ").strip().lower()
                if do_pkg in {"y", "yes"}:
                    raw_objectives = console.input("Objectives (semicolon-separated)> ").strip()
                    remaining_objectives = [
                        o.strip() for o in raw_objectives.split(";") if o.strip()
                    ] or [remaining_work]

                    pkg = await wf.handoff_manager.create_handoff_package(
                        from_agent=from_agent,
                        to_agent=next_agent,
                        work_completed=work_completed,
                        artifacts={},
                        remaining_objectives=remaining_objectives,
                        task=remaining_work or "User task",
                        handoff_reason="manual handoff via console",
                    )

                    preview = wf._format_handoff_input(pkg)  # re-use formatter
                    console.print(Panel(preview, title="Handoff Package", border_style="green"))
            else:
                console.print("[yellow]No handoff recommended.[/yellow]")

    asyncio.run(start_session())


@app.command()
def run(
    message: str = typer.Option("", "--message", "-m", help="Message to process"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Enable streaming output"),
    compile_dspy: bool = typer.Option(True, "--compile/--no-compile", help="Compile DSPy module"),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="Model to use (gpt-4.1, gpt-5-mini, gpt-5). Defaults to config.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    interactive: bool = typer.Option(True, "--interactive", "-i", help="Interactive mode"),
    handoffs: Optional[bool] = typer.Option(
        None,
        "--handoffs/--no-handoffs",
        help="Force enable/disable structured handoffs (defaults to config)",
    ),
) -> None:
    """
    Run the DSPy-enhanced workflow with a message.

    Examples:
        console.py run -m "Analyze renewable energy trends"
        console.py run --no-stream -m "Write a blog post"
        console.py run --model gpt-5-mini
    """

    # Setup logging
    setup_logger("dspy_agent_framework", "DEBUG" if verbose else "INFO")

    # Tracing (optional) - call early so agent creation is instrumented
    _init_tracing()

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error: OPENAI_API_KEY not found in environment[/bold red]")
        console.print("Please set it in .env file or export it")
        raise typer.Exit(1)

    runner = WorkflowRunner(verbose=verbose)

    async def process_message(msg: str):
        """Process a single message."""
        if stream:
            await runner.run_with_streaming(msg)
        else:
            result = await runner.run_without_streaming(msg)
            display_result(result)

    # Initialize workflow with model parameter
    async def init_runner():
        await runner.initialize_workflow(
            compile_dspy=compile_dspy,
            model=model,
            max_rounds=15,
            enable_handoffs=handoffs,
        )

    try:
        if message:
            # Single message mode
            asyncio.run(init_runner())
            asyncio.run(process_message(message))
        elif interactive:
            # Interactive mode
            console.print(
                Panel(
                    "[bold green]DSPy-Agent-Framework Interactive Console[/bold green]\n"
                    "Type your messages below. Commands:\n"
                    "  • 'exit' or 'quit' - Exit the console\n"
                    "  • 'clear' - Clear the screen\n"
                    "  • 'help' - Show this help\n"
                    "  • 'status' - Show workflow status",
                    title="Welcome",
                    border_style="green",
                )
            )

            asyncio.run(init_runner())
            asyncio.run(interactive_loop(runner, stream))
        else:
            console.print("[yellow]No message provided and interactive mode disabled[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        if verbose:
            logger.exception("Workflow error")
        raise typer.Exit(1) from e


async def interactive_loop(runner: WorkflowRunner, stream: bool) -> None:
    """Run interactive message loop."""

    console.print("\n[dim]Ready for input. Type 'help' for commands.[/dim]\n")

    while True:
        try:
            # Get user input
            user_input = console.input("[bold blue]You>[/bold blue] ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ("exit", "quit"):
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() == "clear":
                console.clear()
                continue
            elif user_input.lower() == "help":
                show_help()
                continue
            elif user_input.lower() == "status":
                show_status(runner)
                continue

            # Process as task
            console.print()
            if stream:
                await runner.run_with_streaming(user_input)
            else:
                result = await runner.run_without_streaming(user_input)
                display_result(result)
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")


@app.command()
def analyze(
    task: str = typer.Argument(..., help="Task to analyze"),
    show_routing: bool = typer.Option(True, "--routing/--no-routing", help="Show routing decision"),
    compile_dspy: bool = typer.Option(True, "--compile/--no-compile", help="Compile DSPy module"),
) -> None:
    """
    Analyze a task using DSPy supervisor without execution.

    Shows how the task would be routed and processed.
    """

    async def analyze_task():
        _init_tracing()
        runner = WorkflowRunner()
        await runner.initialize_workflow(compile_dspy=compile_dspy)

        assert runner.workflow is not None, "Workflow not initialized"

        # Analyze task
        analysis = runner.workflow.dspy_supervisor.analyze_task(task)

        # Get routing decision
        routing = runner.workflow.dspy_supervisor.forward(
            task=task,
            team_capabilities="Researcher: Web research, Analyst: Data analysis, Writer: Content creation, Reviewer: Quality check",
        )

        # Display analysis
        table = Table(title="Task Analysis", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Complexity", analysis["complexity"])
        table.add_row("Estimated Steps", str(analysis["steps"]))
        table.add_row("Required Capabilities", ", ".join(analysis["capabilities"]))

        console.print(table)

        if show_routing:
            # Display routing
            routing_table = Table(
                title="Routing Decision", show_header=True, header_style="bold blue"
            )
            routing_table.add_column("Property", style="cyan")
            routing_table.add_column("Value", style="green")

            routing_table.add_row("Execution Mode", routing.mode)
            routing_table.add_row("Assigned Agents", ", ".join(routing.assigned_to))
            routing_table.add_row("Confidence", f"{routing.confidence:.2f}")

            if routing.subtasks:
                routing_table.add_row("Subtasks", "\n".join(routing.subtasks[:3]))

            console.print("\n")
            console.print(routing_table)

    asyncio.run(analyze_task())


@app.command()
def benchmark(
    task: str = typer.Option(
        "Write a blog post about AI", "--task", "-t", help="Task to benchmark"
    ),
    iterations: int = typer.Option(3, "--iterations", "-n", help="Number of iterations"),
    compile_dspy: bool = typer.Option(True, "--compile/--no-compile", help="Compile DSPy module"),
) -> None:
    """
    Benchmark workflow performance with and without DSPy compilation.
    """

    async def run_benchmark():
        _init_tracing()
        results = {"compiled": [], "uncompiled": []}

        # Test with compilation
        if compile_dspy:
            console.print("[bold blue]Testing with DSPy compilation...[/bold blue]")
            runner_compiled = WorkflowRunner()
            await runner_compiled.initialize_workflow(compile_dspy=True)

            for i in range(iterations):
                start = datetime.now()
                await runner_compiled.run_without_streaming(task)
                elapsed = (datetime.now() - start).total_seconds()
                results["compiled"].append(elapsed)
                console.print(f"  Iteration {i + 1}: {elapsed:.2f}s")

        # Test without compilation
        console.print("\n[bold blue]Testing without DSPy compilation...[/bold blue]")
        runner_uncompiled = WorkflowRunner()
        await runner_uncompiled.initialize_workflow(compile_dspy=False)

        for i in range(iterations):
            start = datetime.now()
            await runner_uncompiled.run_without_streaming(task)
            elapsed = (datetime.now() - start).total_seconds()
            results["uncompiled"].append(elapsed)
            console.print(f"  Iteration {i + 1}: {elapsed:.2f}s")

        # Display results
        table = Table(title="Benchmark Results", show_header=True)
        table.add_column("Mode", style="cyan")
        table.add_column("Avg Time (s)", style="yellow")
        table.add_column("Min Time (s)", style="green")
        table.add_column("Max Time (s)", style="red")

        avg_compiled = None
        if results["compiled"]:
            avg_compiled = sum(results["compiled"]) / len(results["compiled"])
            table.add_row(
                "Compiled",
                f"{avg_compiled:.2f}",
                f"{min(results['compiled']):.2f}",
                f"{max(results['compiled']):.2f}",
            )

        avg_uncompiled = sum(results["uncompiled"]) / len(results["uncompiled"])
        table.add_row(
            "Uncompiled",
            f"{avg_uncompiled:.2f}",
            f"{min(results['uncompiled']):.2f}",
            f"{max(results['uncompiled']):.2f}",
        )

        console.print("\n")
        console.print(table)

        if results["compiled"] and avg_compiled is not None:
            improvement = ((avg_uncompiled - avg_compiled) / avg_uncompiled) * 100
            console.print(
                f"\n[bold green]Compilation improved performance by {improvement:.1f}%[/bold green]"
            )

    asyncio.run(run_benchmark())


@app.command()
def list_agents() -> None:
    """List all available agents and their capabilities."""

    # Check tool availability
    import os

    tavily_available = bool(os.getenv("TAVILY_API_KEY"))

    agents_info = [
        {
            "name": "Researcher",
            "description": "Information gathering and web research specialist",
            "tools": [
                f"TavilySearchTool {'(enabled)' if tavily_available else '(missing TAVILY_API_KEY)'}"
            ],
            "best_for": "Finding information, fact-checking, research",
        },
        {
            "name": "Analyst",
            "description": "Data analysis and computation specialist",
            "tools": ["HostedCodeInterpreterTool"],
            "best_for": "Data analysis, calculations, visualizations",
        },
        {
            "name": "Writer",
            "description": "Content creation and report writing specialist",
            "tools": ["None"],
            "best_for": "Writing, documentation, content creation",
        },
        {
            "name": "Reviewer",
            "description": "Quality assurance and validation specialist",
            "tools": ["None"],
            "best_for": "Review, validation, quality checks",
        },
    ]

    table = Table(title="Available Agents", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan", width=12)
    table.add_column("Description", style="yellow", width=40)
    table.add_column("Tools", style="green", width=30)
    table.add_column("Best For", style="blue", width=30)

    for agent in agents_info:
        tools_str = ", ".join(agent["tools"])
        # Cast explicitly to str for static type check friendliness
        table.add_row(
            str(agent["name"]),  # type: ignore[arg-type]
            str(agent["description"]),  # type: ignore[arg-type]
            str(tools_str),  # type: ignore[arg-type]
            str(agent["best_for"]),  # type: ignore[arg-type]
        )

    console.print(table)


@app.command()
def export_history(
    output: Path = typer.Option("workflow_history.json", "--output", "-o", help="Output file path"),
    task: str = typer.Option("", "--task", "-t", help="Task to run before export"),
    model: str = typer.Option("gpt-4.1", "--model", help="Model to use for task execution"),
) -> None:
    """Export workflow execution history to a file."""

    async def export():
        _init_tracing()
        runner = WorkflowRunner()
        await runner.initialize_workflow(model=model)

        if task:
            console.print(f"[bold blue]Running task: {task}[/bold blue]")
            await runner.run_without_streaming(task)

        assert runner.workflow is not None, "Workflow not initialized"

        # Get execution summary
        summary = runner.workflow.dspy_supervisor.get_execution_summary()

        # Add metadata
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "execution_summary": summary,
            "config": {
                "model": runner.workflow.config.dspy_model,
                "compiled": runner.workflow.config.compile_dspy,
                "completion_storage": runner.workflow.config.enable_completion_storage,
                "refinement_threshold": runner.workflow.config.refinement_threshold,
            },
        }

        # Write to file
        with open(output, "w") as f:
            json.dump(export_data, f, indent=2)

        console.print(f"[bold green]✓ Exported history to {output}[/bold green]")

    asyncio.run(export())


def display_result(result: Dict[str, Any]) -> None:
    """Display workflow result in formatted output."""

    # Main result
    console.print(
        Panel(
            str(result.get("result", "No result"))[:1000],
            title="[bold green]Result",
            border_style="green",
        )
    )

    # Metadata
    if "metadata" in result:
        meta = result["metadata"]

        # Quality and progress
        if "quality" in meta:
            quality_text = f"Score: {meta['quality']['score']:.1f}/10"
            if meta["quality"].get("improvements"):
                quality_text += f"\nSuggestions: {meta['quality']['improvements'][:200]}"

            console.print(
                Panel(
                    quality_text,
                    title="[bold yellow]Quality Assessment",
                    border_style="yellow",
                )
            )

        # Execution details
        if "routing" in meta:
            routing = meta["routing"]
            exec_text = (
                f"Mode: {routing['mode']}\n"
                f"Agents: {', '.join(routing['agents'])}\n"
                f"Confidence: {routing['confidence']:.2f}"
            )

            if "execution_time" in meta:
                exec_text += f"\nTime: {meta['execution_time']:.2f}s"

            console.print(
                Panel(
                    exec_text,
                    title="[bold blue]Execution Details",
                    border_style="blue",
                )
            )


def show_help() -> None:
    """Show interactive mode help."""

    help_text = """
[bold]Available Commands:[/bold]
  • exit, quit - Exit the console
  • clear - Clear the screen
  • help - Show this help message
  • status - Show workflow status

[bold]Example Tasks:[/bold]
  • "Analyze the impact of AI on healthcare"
  • "Write a blog post about quantum computing"
  • "Research and compare cloud providers"
  • "Create a financial analysis of Tesla stock"

[bold]Tips:[/bold]
  • Be specific in your requests for better results
  • Complex tasks will be automatically broken down
  • Use streaming mode to see real-time progress
    """

    console.print(Panel(help_text, title="Help", border_style="cyan"))


def show_status(runner: WorkflowRunner) -> None:
    """Show current workflow status."""

    if not runner.workflow:
        console.print("[yellow]No workflow initialized yet[/yellow]")
        return

    summary = runner.workflow.dspy_supervisor.get_execution_summary()

    status_text = f"""
[bold]Workflow Status:[/bold]
  • Model: {runner.workflow.config.dspy_model}
  • DSPy Compiled: {runner.workflow.config.compile_dspy}
  • Completion Storage: {runner.workflow.config.enable_completion_storage}
  • Total Routings: {summary["total_routings"]}
  • Max Rounds: {runner.workflow.config.max_rounds}
  • Refinement Threshold: {runner.workflow.config.refinement_threshold}
    """

    if summary["routing_history"]:
        status_text += "\n\n[bold]Recent Routings:[/bold]\n"
        for routing in summary["routing_history"][-3:]:
            status_text += f"  • {routing['mode']} → {', '.join(routing['assigned_to'])}\n"

    console.print(Panel(status_text, title="Status", border_style="blue"))


@app.command()
def gepa_optimize(
    examples: Path = typer.Option(
        Path("data/supervisor_examples.json"),
        "--examples",
        "-e",
        help="Training dataset path",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Model for DSPy LM (defaults to config dspy.model)",
    ),
    auto: Optional[str] = typer.Option(
        None,
        "--auto",
        help="GEPA auto configuration (light|medium|heavy). Mutually exclusive with --max-full-evals / --max-metric-calls. If omitted, you MUST provide one numeric limit.",
        case_sensitive=False,
    ),
    max_full_evals: Optional[int] = typer.Option(
        None,
        "--max-full-evals",
        help="Explicit full GEPA evaluation budget (exclusive with --auto / --max-metric-calls)",
    ),
    max_metric_calls: Optional[int] = typer.Option(
        None,
        "--max-metric-calls",
        help="Explicit metric call budget (exclusive with --auto / --max-full-evals)",
    ),
    reflection_model: Optional[str] = typer.Option(
        None,
        "--reflection-model",
        help="Optional LM for reflections (defaults to main LM)",
    ),
    val_split: float = typer.Option(0.2, "--val-split", help="Validation split (0.0-0.5)"),
    use_history: bool = typer.Option(
        False,
        "--use-history/--no-history",
        help="Augment training data with high-quality execution history",
    ),
    history_min_quality: float = typer.Option(
        8.0, "--history-min-quality", help="Minimum quality score for harvested history"
    ),
    history_limit: int = typer.Option(200, "--history-limit", help="History lookback size"),
    log_dir: Path = typer.Option(Path("logs/gepa"), "--log-dir", help="Directory for GEPA logs"),
    seed: int = typer.Option(13, "--seed", help="Random seed for dataset shuffle"),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Do not read/write compiled module cache (always recompile)",
    ),
) -> None:
    """
    Compile the DSPy supervisor using dspy.GEPA for prompt evolution.
    """
    from rich.progress import Progress

    yaml_config = load_config()
    effective_model = model or yaml_config.get("dspy", {}).get("model", "gpt-5-mini")

    # Initialize tracing prior to GEPA to capture compilation spans if supported
    _init_tracing()

    console.print(
        Panel(
            f"[bold]Running GEPA[/bold]\nModel: {effective_model}\nDataset: {examples}",
            title="dspy.GEPA Optimization",
            border_style="magenta",
        )
    )

    auto_choice = auto.lower() if auto else None
    if auto_choice and auto_choice not in {"light", "medium", "heavy"}:
        raise typer.BadParameter("--auto must be one of: light, medium, heavy")
    if not 0.0 <= val_split <= 0.5:
        raise typer.BadParameter("--val-split must be between 0.0 and 0.5")
    if not 0.0 <= history_min_quality <= 10.0:
        raise typer.BadParameter("--history-min-quality must be between 0 and 10")

    # Enforce exclusivity: exactly ONE of auto_choice, max_full_evals, max_metric_calls
    chosen = [c for c in [auto_choice, max_full_evals, max_metric_calls] if c is not None]
    if len(chosen) == 0:
        raise typer.BadParameter(
            "You must specify exactly one of: --auto OR --max-full-evals OR --max-metric-calls."
        )
    if len(chosen) > 1:
        raise typer.BadParameter(
            "Exactly one of --auto, --max-full-evals, --max-metric-calls must be specified (not multiple)."
        )
    # If numeric limit chosen ensure auto_choice cleared
    if (max_full_evals is not None or max_metric_calls is not None) and auto_choice:
        auto_choice = None

    try:
        import dspy  # type: ignore  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise typer.Exit(code=1) from exc

    # Use centralized DSPy manager (aligns with agent-framework patterns)
    from .utils.dspy_manager import configure_dspy_settings  # type: ignore

    configure_dspy_settings(model=effective_model, enable_cache=True)

    supervisor = DSPySupervisor()
    supervisor.set_tool_registry(ToolRegistry())

    reflection_model_value = reflection_model or effective_model
    gepa_options = {
        "auto": auto_choice,
        "max_full_evals": max_full_evals,
        "max_metric_calls": max_metric_calls,
        "reflection_model": reflection_model_value,
        "log_dir": str(log_dir),
        "perfect_score": 1.0,
        "use_history_examples": use_history,
        "history_min_quality": history_min_quality,
        "history_limit": history_limit,
        "val_split": val_split,
        "seed": seed,
    }

    with Progress() as progress:
        task_id = progress.add_task("[cyan]Optimizing with GEPA...", start=False)
        progress.start_task(task_id)

        compiled = compile_supervisor(
            supervisor,
            examples_path=str(examples),
            use_cache=not no_cache,
            optimizer="gepa",
            gepa_options=gepa_options,
        )

        progress.update(task_id, completed=100)
    compiled_name = compiled.__class__.__name__ if compiled else "DSPySupervisor"

    console.print(
        Panel(
            "[green]GEPA optimization complete![/green]\n"
            f"Cache: logs/compiled_supervisor.pkl\n"
            f"Log dir: {log_dir}\n"
            f"Optimizer model: {effective_model}\n"
            f"Compiled module: {compiled_name}",
            title="Success",
            border_style="green",
        )
    )


@app.command()
def self_improve(
    min_quality: float = typer.Option(
        8.0, "--min-quality", "-q", help="Minimum quality score (0-10)"
    ),
    max_examples: int = typer.Option(20, "--max-examples", "-n", help="Maximum examples to add"),
    stats_only: bool = typer.Option(
        False, "--stats-only", help="Show stats without adding examples"
    ),
) -> None:
    """Automatically improve routing from high-quality execution history."""
    from rich.table import Table

    from .utils.self_improvement import SelfImprovementEngine

    engine = SelfImprovementEngine(
        min_quality_score=min_quality,
        max_examples_to_add=max_examples,
        history_lookback=100,
    )

    # Tracing initialization (optional)
    _init_tracing()

    # Show stats
    stats = engine.get_improvement_stats()

    console.print("\n[bold cyan]📊 Self-Improvement Analysis[/bold cyan]\n")

    stats_table = Table()
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")

    stats_table.add_row("Total Executions", str(stats["total_executions"]))
    stats_table.add_row("High-Quality Executions", str(stats["high_quality_executions"]))
    stats_table.add_row("Average Quality Score", f"{stats['average_quality_score']:.2f}/10")

    console.print(stats_table)

    if stats_only:
        return

    if stats["high_quality_executions"] == 0:
        console.print("\n[yellow]⚠ No high-quality executions to learn from[/yellow]")
        return

    # Perform improvement
    added, status = engine.auto_improve()

    if added > 0:
        console.print(f"\n[green]✓ {status}[/green]")
        console.print("[dim]Next execution will use improved routing model[/dim]")
    else:
        console.print(f"\n[yellow]{status}[/yellow]")


@app.command()
def evaluate(
    dataset: Optional[Path] = typer.Option(
        None, "--dataset", "-d", help="Override dataset path (defaults to config)"
    ),
    max_tasks: int = typer.Option(0, "--max-tasks", help="Limit number of tasks (0 = all)"),
    metrics: Optional[str] = typer.Option(
        None,
        "--metrics",
        help="Comma-separated metric list overriding config (quality_score,keyword_success,latency_seconds,routing_efficiency,refinement_triggered)",
    ),
    stop_on_failure: bool = typer.Option(
        False, "--stop-on-failure", help="Stop when a *success* metric returns 0/None"
    ),
) -> None:
    """Run batch evaluation over a dataset using configured metrics."""

    cfg = load_config()
    eval_cfg = cfg.get("evaluation", {})
    if not eval_cfg.get("enabled", True):
        console.print(
            "[yellow]Evaluation disabled in config. Enable 'evaluation.enabled'.[/yellow]"
        )
        raise typer.Exit(1)

    dataset_path = str(dataset or eval_cfg.get("dataset_path", "data/evaluation_tasks.jsonl"))
    metric_list = (
        [m.strip() for m in metrics.split(",") if m.strip()]
        if metrics
        else eval_cfg.get("metrics", [])
    )
    out_dir = eval_cfg.get("output_dir", "logs/evaluation")
    max_tasks_effective = max_tasks if max_tasks else int(eval_cfg.get("max_tasks", 0))
    stop = stop_on_failure or bool(eval_cfg.get("stop_on_failure", False))

    async def wf_factory():
        runner = WorkflowRunner(verbose=False)
        await runner.initialize_workflow(
            compile_dspy=cfg.get("dspy", {}).get("optimization", {}).get("enabled", True)
        )
        assert runner.workflow is not None
        return runner.workflow

    evaluator = Evaluator(
        workflow_factory=wf_factory,
        dataset_path=dataset_path,
        output_dir=out_dir,
        metrics=metric_list,
        max_tasks=max_tasks_effective,
        stop_on_failure=stop,
    )

    console.print(
        Panel(
            f"[bold]Starting Evaluation[/bold]\nDataset: {dataset_path}\nMetrics: {
                ', '.join(metric_list) if metric_list else 'None'
            }",
            title="Evaluation",
            border_style="magenta",
        )
    )

    async def run_eval():
        summary = await evaluator.run()
        console.print(
            Panel(
                f"Total Tasks: {summary['total_tasks']}\nMetric Means: "
                + ", ".join(
                    f"{k}={v['mean']:.2f}"
                    for k, v in summary.get("metrics", {}).items()
                    if v.get("mean") is not None
                ),
                title="Evaluation Summary",
                border_style="green",
            )
        )
        console.print(
            f"[dim]Report: {out_dir}/evaluation_report.jsonl | Summary: {out_dir}/evaluation_summary.json[/dim]"
        )

    asyncio.run(run_eval())


if __name__ == "__main__":
    app()
