"""
Main supervisor workflow implementation with DSPy enhancement.
"""

# Standard library imports
import asyncio
import re
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
)

# dspy lacks type hints / py.typed marker; provide safe import and minimal stubs for type checking.
import dspy  # noqa: F401

# Third-party imports
import openai
from agent_framework import (
    ChatAgent,
    ChatMessage,
    HostedCodeInterpreterTool,
    MagenticAgentMessageEvent,
    MagenticBuilder,
    Role,
    WorkflowOutputEvent,
)
from agent_framework.openai import OpenAIChatClient

from ..dspy_modules.supervisor import DSPySupervisor  # type: ignore
from ..tools import (
    BrowserTool,  # type: ignore
    TavilyMCPTool,
)
from ..utils.cache import TTLCache  # type: ignore
from ..utils.compiler import compile_supervisor  # type: ignore
from ..utils.dspy_manager import configure_dspy_settings  # type: ignore
from ..utils.history_manager import HistoryManager  # type: ignore
from ..utils.logger import setup_logger  # type: ignore
from ..utils.models import ExecutionMode, RoutingDecision, ensure_routing_decision
from ..utils.tool_registry import ToolRegistry  # type: ignore
from .exceptions import AgentExecutionError, RoutingError
from .handoff_manager import (
    HandoffContext,  # type: ignore
    HandoffManager,
)

if TYPE_CHECKING:

    class DSPySettings:
        def configure(self, **kwargs: Any) -> None: ...

    class DSPyModule:
        class OpenAI:
            def __init__(self, model: str, temperature: float = 0.0): ...


logger = setup_logger(__name__)

T = TypeVar("T")


# Use ChatMessage (from agent_framework) for all workflow events. Avoid lightweight
# wrappers to ensure compatibility with Magentic event types which expect
# agent_framework.ChatMessage instances.


def _validate_task(task: str, *, max_length: int = 10000) -> str:
    """Validate and sanitize task input.

    Args:
        task: The task string to validate
        max_length: Maximum allowed task length

    Returns:
        Sanitized task string

    Raises:
        ValueError: If task is empty or exceeds maximum length
    """
    if not task or not task.strip():
        raise ValueError("Task cannot be empty")
    if len(task) > max_length:  # Reasonable limit for API calls
        raise ValueError(
            f"Task exceeds maximum length of {max_length} characters (got {len(task)})"
        )
    return task.strip()


def _create_openai_client_with_store(
    enable_storage: bool = False,
    reasoning_effort: Optional[str] = None,
) -> openai.AsyncOpenAI:
    """Create AsyncOpenAI client configured to optionally store completions and set reasoning effort.

    Args:
        enable_storage: Whether to enable completion storage
        reasoning_effort: Optional reasoning effort level ("minimal", "medium", "maximal") for GPT-5 models

    Returns:
        AsyncOpenAI client with default_query set to include store=true if enabled
    """
    import os

    kwargs: Dict[str, Any] = {}

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        kwargs["api_key"] = api_key

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url

    default_query: Dict[str, Any] = {}
    if enable_storage:
        default_query["store"] = "true"

    # Reasoning effort is passed in the request body, not query params
    # We'll need to handle this via extra_body in the actual request
    # For now, we store it as a client attribute for later use
    client = openai.AsyncOpenAI(**kwargs)
    if reasoning_effort is not None:
        # Store reasoning effort as client attribute for use in requests
        client._reasoning_effort = reasoning_effort  # type: ignore[attr-defined]

    if default_query:
        # Note: default_query might not support nested dicts for reasoning
        # Reasoning effort needs to be in request body, not query params
        pass

    return client


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""

    max_rounds: int = 15
    max_stalls: int = 3
    max_resets: int = 2
    enable_streaming: bool = True
    parallel_threshold: int = 3
    dspy_model: str = "gpt-5-mini"
    compile_dspy: bool = True
    refinement_threshold: float = 8.0
    enable_refinement: bool = True
    enable_completion_storage: bool = False
    agent_models: Optional[Dict[str, str]] = None
    agent_temperatures: Optional[Dict[str, float]] = None
    history_format: str = "jsonl"
    examples_path: str = "data/supervisor_examples.json"
    dspy_optimizer: str = "bootstrap"
    gepa_options: Optional[Dict[str, Any]] = None
    enable_handoffs: bool = True
    max_task_length: int = 10000
    quality_threshold: float = 8.0
    dspy_retry_attempts: int = 3
    dspy_retry_backoff_seconds: float = 1.0
    analysis_cache_ttl_seconds: int = 3600
    judge_threshold: float = 7.0
    max_refinement_rounds: int = 2
    enable_judge: bool = True
    judge_model: Optional[str] = None
    judge_reasoning_effort: str = "medium"


class SupervisorWorkflow:
    """
    Main workflow class combining DSPy supervisor with agent-framework.
    """

    def __init__(self, config: Optional[WorkflowConfig] = None):
        self.config = config or WorkflowConfig()
        self.dspy_supervisor: DSPySupervisor = DSPySupervisor()
        self.agents: Dict[str, Any] = {}
        self.workflow: Any = None
        self.execution_history: List[Dict[str, Any]] = []
        self.current_execution: Dict[str, Any] = {}
        self.verbose_logging: bool = True
        self.tool_registry: ToolRegistry = ToolRegistry()
        self.history_manager: HistoryManager = HistoryManager(
            history_format=self.config.history_format
        )
        self.handoff_manager: Optional[HandoffManager] = None
        # Handoffs are core to the app now; respect config toggle
        self.enable_handoffs: bool = self.config.enable_handoffs
        # Shared OpenAI client (created once in initialize, reused for all agents)
        self._openai_client: Optional[openai.AsyncOpenAI] = None
        self._analysis_cache: Optional[TTLCache[str, Dict[str, Any]]] = (
            TTLCache[str, Dict[str, Any]](self.config.analysis_cache_ttl_seconds)
            if self.config.analysis_cache_ttl_seconds > 0
            else None
        )
        self._latest_phase_timings: Dict[str, float] = {}
        self._latest_phase_status: Dict[str, str] = {}

        # Lazy compilation state
        self._compiled_supervisor: Optional[DSPySupervisor] = None
        self._compilation_status: str = "pending"  # pending, compiling, completed, failed
        self._compilation_task: Optional[asyncio.Task] = None
        self._compilation_lock = asyncio.Lock() if hasattr(asyncio, "Lock") else None

        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)

    async def initialize(self, compile_dspy: bool = True):
        """Initialize the workflow with agents and DSPy."""

        init_start = datetime.now()
        logger.info("=" * 80)
        logger.info("Initializing DSPy-Enhanced Agent Framework")
        logger.info("=" * 80)

        # Create shared OpenAI client once (reused for all agents and supervisor)
        self._openai_client = _create_openai_client_with_store(
            self.config.enable_completion_storage
        )
        logger.info("Created shared OpenAI client for all agents")

        # Initialize DSPy using centralized manager (aligns with agent-framework
        # shared client pattern)
        logger.info(f"Configuring DSPy with OpenAI LM ({self.config.dspy_model})")
        configure_dspy_settings(
            model=self.config.dspy_model,
            enable_cache=True,
            force_reconfigure=False,
        )

        # Create specialized agents BEFORE compilation if tool-aware DSPy signatures need visibility
        logger.info("Creating specialized agents...")
        self.agents = self._create_agents()
        logger.info(f"Created {len(self.agents)} agents: {', '.join(self.agents.keys())}")

        # Register tools in registry early so supervisor sees them during compilation / analysis
        # We track tools during agent creation and register them here
        logger.info("Registering tools in tool registry (pre-compilation)...")
        for agent_name, agent in self.agents.items():
            registered_count = 0
            failed_count = 0
            # Primary path: agent_framework ChatAgent stores tools in chat_options.tools (list)
            # Note: MCP tools may not appear in chat_options.tools but are still valid
            try:
                raw_tools = []
                if hasattr(agent, "chat_options") and getattr(agent.chat_options, "tools", None):
                    raw_tools = agent.chat_options.tools or []
                elif hasattr(agent, "tools") and getattr(
                    agent, "tools", None
                ):  # fallback for stub agents/tests
                    raw = agent.tools
                    raw_tools = raw if isinstance(raw, list) else [raw]

                for t in raw_tools:
                    if t is None:
                        continue
                    try:
                        # Validate tool before registration
                        if not self._validate_tool(t):
                            tool_name = getattr(t, "name", t.__class__.__name__)
                            logger.warning(
                                f"Skipping invalid tool '{tool_name}' for {agent_name}. "
                                "Tool does not match agent-framework requirements."
                            )
                            failed_count += 1
                            continue

                        self.tool_registry.register_tool_by_agent(agent_name, t)
                        registered_count += 1
                        tool_name = getattr(t, "name", t.__class__.__name__)
                        logger.info(
                            f"Registered tool for {agent_name}: {tool_name} "
                            f"(type: {type(t).__name__})"
                        )
                    except Exception as tool_error:
                        tool_name = getattr(t, "name", t.__class__.__name__)
                        logger.warning(
                            f"Failed to register tool '{tool_name}' for {agent_name}: {tool_error}",
                            exc_info=True,
                        )
                        failed_count += 1

            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to register tools for {agent_name}: {e}", exc_info=True)

            if registered_count > 0:
                logger.debug(f"{agent_name}: {registered_count} tool(s) registered successfully")
            if failed_count > 0:
                logger.warning(f"{agent_name}: {failed_count} tool(s) failed to register")

        total_tools = len(self.tool_registry.get_available_tools())
        logger.info(
            f"Tool registry initialized with {total_tools} tool(s) across {len(self.agents)} agent(s)"
        )

        # Attach tool registry to supervisor
        self.dspy_supervisor.set_tool_registry(self.tool_registry)

        # Initialize handoff manager (after supervisor and tools are ready)
        self.handoff_manager = HandoffManager(self.dspy_supervisor)

        # Optionally compile with examples (now tool-aware)
        # Use lazy compilation: compile in background or on first use
        if compile_dspy and self.config.compile_dspy:
            logger.info("Setting up DSPy compilation (lazy/background mode)...")
            # Start background compilation task (non-blocking)
            self._compilation_task = asyncio.create_task(self._compile_supervisor_async())
            logger.info("DSPy compilation started in background (workflow can start immediately)")
        else:
            logger.info("Skipping DSPy compilation (using base prompts)")
            self._compilation_status = "skipped"

        # Build workflow (can proceed even if compilation is still running)
        logger.info("Building Magentic workflow...")
        self.workflow = self._build_workflow()

        init_time = (datetime.now() - init_start).total_seconds()
        logger.info(f"Workflow initialized successfully in {init_time:.2f}s")
        logger.info("=" * 80)

    async def _compile_supervisor_async(self) -> None:
        """
        Async compilation method that runs in background.

        This allows the workflow to start immediately while compilation
        happens in the background, aligning with Agent Framework's async patterns.
        """
        if self._compilation_status in ("completed", "compiling"):
            return

        self._compilation_status = "compiling"
        logger.info("Starting DSPy compilation in background...")

        try:
            # Extract agent config for cache invalidation
            agent_config = {}
            for agent_name, agent in self.agents.items():
                agent_config[agent_name] = {
                    "description": getattr(agent, "description", ""),
                    "tools": [
                        tool.__class__.__name__
                        for tool in (getattr(agent.chat_options, "tools", []) or [])
                    ],
                }

            # Run compilation in executor to avoid blocking event loop
            import concurrent.futures  # noqa: F401

            loop = asyncio.get_event_loop()

            def compile_sync():
                return compile_supervisor(
                    self.dspy_supervisor,
                    examples_path=self.config.examples_path,
                    optimizer=self.config.dspy_optimizer,
                    gepa_options=self.config.gepa_options,
                    dspy_model=self.config.dspy_model,
                    agent_config=agent_config,
                )

            compiled = await loop.run_in_executor(None, compile_sync)
            self._compiled_supervisor = compiled
            self._compilation_status = "completed"
            logger.info("✓ DSPy compilation completed in background")
        except Exception as e:
            self._compilation_status = "failed"
            logger.error(f"DSPy compilation failed: {e}")
            # Fall back to uncompiled supervisor
            self._compiled_supervisor = self.dspy_supervisor

    @property
    def compiled_supervisor(self) -> DSPySupervisor:
        """
        Lazy compilation property: ensures supervisor is compiled before use.

        If compilation is still running, waits for it to complete.
        If compilation hasn't started, triggers it synchronously.
        This ensures the supervisor is always compiled when needed.
        """
        # If already compiled, return it
        if self._compiled_supervisor is not None:
            return self._compiled_supervisor

        # If compilation is in progress, wait for it
        if self._compilation_task and not self._compilation_task.done():
            logger.debug("Waiting for background compilation to complete...")
            # Run the task synchronously if needed (for sync contexts)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # In async context, we can't block - return uncompiled for now
                    # The compilation will complete in background
                    logger.warning("Compilation still in progress, using uncompiled supervisor")
                    return self.dspy_supervisor
                else:
                    # In sync context, we can wait
                    loop.run_until_complete(self._compilation_task)
            except RuntimeError:
                # No event loop - compilation will happen on next access
                logger.warning("No event loop available, using uncompiled supervisor")
                return self.dspy_supervisor

        # If compilation completed, use compiled version
        if self._compiled_supervisor is not None:
            return self._compiled_supervisor

        # If compilation failed or was skipped, use uncompiled
        if self._compilation_status in ("failed", "skipped"):
            return self.dspy_supervisor

        # If compilation hasn't started, trigger it synchronously
        if self._compilation_status == "pending":
            logger.info("Triggering synchronous DSPy compilation...")
            try:
                agent_config = {}
                for agent_name, agent in self.agents.items():
                    agent_config[agent_name] = {
                        "description": getattr(agent, "description", ""),
                        "tools": [
                            tool.__class__.__name__
                            for tool in (getattr(agent.chat_options, "tools", []) or [])
                        ],
                    }

                compiled = compile_supervisor(
                    self.dspy_supervisor,
                    examples_path=self.config.examples_path,
                    optimizer=self.config.dspy_optimizer,
                    gepa_options=self.config.gepa_options,
                    dspy_model=self.config.dspy_model,
                    agent_config=agent_config,
                )
                self._compiled_supervisor = compiled
                self._compilation_status = "completed"
                return compiled
            except Exception as e:
                logger.error(f"Synchronous compilation failed: {e}")
                self._compilation_status = "failed"
                return self.dspy_supervisor

        # Fallback to uncompiled
        return self.dspy_supervisor

    async def _call_with_retry(
        self,
        fn: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Invoke a DSPy function with retry and exponential backoff."""

        attempts = max(1, int(self.config.dspy_retry_attempts))
        backoff = max(0.0, float(self.config.dspy_retry_backoff_seconds))
        last_exc: Optional[Exception] = None

        for attempt in range(1, attempts + 1):
            try:
                result = fn(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    result = await result  # type: ignore[assignment]
                return result  # type: ignore[return-value]
            except Exception as exc:  # pragma: no cover - defensive logging
                last_exc = exc
                logger.warning(
                    "DSPy call %s failed on attempt %d/%d: %s",
                    getattr(fn, "__name__", repr(fn)),
                    attempt,
                    attempts,
                    exc,
                )
                if attempt < attempts:
                    await asyncio.sleep(backoff * attempt)

        if last_exc:
            raise last_exc
        raise RuntimeError("DSPy call failed without raising an exception")

    def _fallback_analysis(self, task: str) -> Dict[str, Any]:
        """Return a safe default analysis when DSPy is unavailable."""

        logger.error("Falling back to heuristic task analysis for task: %s", task[:100])
        word_count = len(task.split())
        complexity = "simple"
        if word_count > 150:
            complexity = "complex"
        elif word_count > 40:
            complexity = "moderate"

        return {
            "complexity": complexity,
            "capabilities": ["general_reasoning"],
            "tool_requirements": [],
            "steps": max(3, min(6, word_count // 40 + 1)),
            "search_context": "",
            "needs_web_search": False,
            "search_query": "",
        }

    def _fallback_routing_decision(self, task: str) -> RoutingDecision:
        """Fallback routing that delegates to the first available agent."""

        logger.error("Falling back to heuristic routing for task: %s", task[:100])
        fallback_agent = next(iter(self.agents.keys()), None)
        if fallback_agent is None:
            raise RoutingError(
                "DSPy routing failed and no agents are registered.",
                {"task": task},
            )

        subtasks: Tuple[str, ...] = (task,)

        return RoutingDecision(
            task=task,
            assigned_to=(fallback_agent,),
            mode=ExecutionMode.DELEGATED,
            subtasks=subtasks,
            tool_requirements=tuple(),
            confidence=0.0,
        )

    def _fallback_progress(self) -> Dict[str, Any]:
        """Provide default progress evaluation when DSPy fails."""

        return {
            "action": "continue",
            "feedback": "Unable to evaluate progress with DSPy; continuing with heuristic execution.",
        }

    def _fallback_quality(self, task: str, result: str) -> Dict[str, Any]:
        """Provide default quality assessment when DSPy fails."""

        return {
            "score": float(self.config.quality_threshold),
            "missing": "",
            "improvements": f"Manually review the result for task: {task[:100]}",
        }

    @staticmethod
    def _get_value(source: Any, key: str, default: Any = None) -> Any:
        """Helper to extract a value from an object or mapping."""

        if isinstance(source, Mapping):
            return source.get(key, default)
        return getattr(source, key, default)

    def _normalize_analysis_result(self, analysis: Any, task: str) -> Dict[str, Any]:
        """Normalize DSPy analysis output into a canonical dictionary."""

        if analysis is None:
            return self._fallback_analysis(task)

        complexity = str(self._get_value(analysis, "complexity", "moderate") or "moderate")
        capabilities_raw = self._get_value(analysis, "required_capabilities", [])
        if isinstance(capabilities_raw, str):
            capabilities = [cap.strip() for cap in capabilities_raw.split(",") if cap.strip()]
        elif isinstance(capabilities_raw, list):
            capabilities = [str(cap).strip() for cap in capabilities_raw if str(cap).strip()]
        else:
            capabilities = ["general_reasoning"]

        tool_requirements_raw = self._get_value(analysis, "tool_requirements", [])
        if isinstance(tool_requirements_raw, str):
            tool_requirements = [
                tool.strip()
                for tool in tool_requirements_raw.replace("\n", ",").split(",")
                if tool.strip()
            ]
        elif isinstance(tool_requirements_raw, list):
            tool_requirements = [
                str(tool).strip() for tool in tool_requirements_raw if str(tool).strip()
            ]
        else:
            tool_requirements = []

        estimated_steps = self._get_value(analysis, "estimated_steps", 3)
        try:
            steps = int(estimated_steps)
        except (TypeError, ValueError):
            steps = 3

        search_context = str(self._get_value(analysis, "search_context", "") or "")
        needs_web_search_raw = self._get_value(analysis, "needs_web_search", False)
        needs_web_search = (
            str(needs_web_search_raw).strip().lower() in {"yes", "true", "1", "y"}
            if isinstance(needs_web_search_raw, str)
            else bool(needs_web_search_raw)
        )
        search_query = str(self._get_value(analysis, "search_query", "") or "")

        return {
            "complexity": complexity,
            "capabilities": capabilities or ["general_reasoning"],
            "tool_requirements": tool_requirements,
            "steps": steps if steps > 0 else 3,
            "search_context": search_context,
            "needs_web_search": needs_web_search,
            "search_query": search_query,
        }

    def _validate_routing_prediction(self, prediction: Any, task: str) -> RoutingDecision:
        """Validate routing output and fallback when invalid."""

        if prediction is None:
            return self._fallback_routing_decision(task)

        try:
            if isinstance(prediction, RoutingDecision):
                decision = prediction
            elif isinstance(prediction, Mapping):
                decision = ensure_routing_decision(prediction)
            else:
                payload = {
                    "task": getattr(prediction, "task", task),
                    "assigned_to": getattr(prediction, "assigned_to", ""),
                    "mode": getattr(prediction, "execution_mode", getattr(prediction, "mode", "")),
                    "subtasks": getattr(prediction, "subtasks", ""),
                    "tool_requirements": getattr(
                        prediction, "tool_requirements", getattr(prediction, "tools", [])
                    ),
                    "confidence": getattr(
                        prediction,
                        "confidence",
                        getattr(
                            prediction,
                            "routing_confidence",
                            getattr(prediction, "decision_confidence", None),
                        ),
                    ),
                }
                decision = ensure_routing_decision(payload)

            if not decision.assigned_to:
                raise ValueError("Routing decision did not include any agents.")

            return decision
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Invalid routing decision from DSPy: %s", exc)
            return self._fallback_routing_decision(task)

    def _normalize_progress_evaluation(self, evaluation: Any) -> Dict[str, Any]:
        """Normalize DSPy progress evaluation."""

        if evaluation is None:
            return self._fallback_progress()

        action = self._get_value(evaluation, "action", None) or self._get_value(
            evaluation, "next_action", "continue"
        )
        feedback = self._get_value(evaluation, "feedback", "")

        action_str = str(action).strip().lower() if isinstance(action, str) else "continue"
        if action_str not in {"continue", "refine", "complete", "escalate"}:
            action_str = "continue"

        return {"action": action_str, "feedback": str(feedback or "")}

    def _normalize_quality_assessment(
        self, assessment: Any, task: str, result: str
    ) -> Dict[str, Any]:
        """Normalize DSPy quality output."""

        if assessment is None:
            return self._fallback_quality(task, result)

        score_raw = self._get_value(assessment, "score", None) or self._get_value(
            assessment, "quality_score", None
        )
        try:
            if isinstance(score_raw, str) and "/" in score_raw:
                score = float(score_raw.split("/")[0])
            else:
                score = float(score_raw)
        except (TypeError, ValueError):
            score = self.config.quality_threshold

        missing = self._get_value(assessment, "missing", None) or self._get_value(
            assessment, "missing_elements", ""
        )
        improvements = self._get_value(assessment, "improvements", None) or self._get_value(
            assessment, "improvement_suggestions", ""
        )

        return {
            "score": score,
            "missing": missing,
            "improvements": improvements,
        }

    async def _analysis_phase(self, task: str) -> Dict[str, Any]:
        """Run DSPy analysis with caching and optional tool execution."""

        cache_key = task.strip()
        if self._analysis_cache:
            cached = self._analysis_cache.get(cache_key)
            if cached:
                logger.info("Cache hit: reusing DSPy task analysis for task hash.")
                self._record_phase_status("analysis", "cached")
                return dict(cached)

        used_fallback = False

        try:
            raw_analysis = await self._call_with_retry(
                self.compiled_supervisor.analyze_task,
                task,
                perform_search=False,
            )
            analysis = self._normalize_analysis_result(raw_analysis, task)
        except Exception as exc:
            logger.exception("DSPy task analysis failed; using fallback: %s", exc)
            analysis = self._fallback_analysis(task)
            used_fallback = True

        if (
            analysis.get("needs_web_search")
            and analysis.get("search_query")
            and not analysis.get("search_context")
        ):
            try:
                search_context = await self._call_with_retry(
                    self.dspy_supervisor.perform_web_search_async,
                    analysis["search_query"],
                )
                if search_context:
                    analysis["search_context"] = search_context
            except Exception as exc:
                logger.warning("Async web search failed: %s", exc)

        if self._analysis_cache:
            self._analysis_cache.set(cache_key, dict(analysis))

        self._record_phase_status("analysis", "fallback" if used_fallback else "success")
        return analysis

    async def _routing_phase(
        self,
        task: str,
        analysis: Dict[str, Any],
    ) -> RoutingDecision:
        """Run DSPy routing with validation and fallback."""

        team_descriptions = {name: agent.description for name, agent in self.agents.items()}

        used_fallback = False

        try:
            raw_routing = await self._call_with_retry(
                self.compiled_supervisor.route_task,
                task=task,
                team=team_descriptions,
                context=analysis.get("search_context", "") or "",
            )
            routing = self._normalize_routing_decision(
                self._validate_routing_prediction(raw_routing, task),
                task,
            )
        except Exception as exc:
            logger.exception("DSPy routing failed; using fallback: %s", exc)
            routing = self._normalize_routing_decision(
                self._fallback_routing_decision(task),
                task,
            )
            used_fallback = True

        # Detect and log edge cases in routing decision
        edge_cases = self._detect_routing_edge_cases(task, routing)
        if edge_cases:
            logger.info(
                f"Edge cases detected in routing for task '{task[:50]}...': {', '.join(edge_cases)}"
            )
            # Store edge cases in current execution for learning
            if "edge_cases" not in self.current_execution:
                self.current_execution["edge_cases"] = []
            self.current_execution["edge_cases"].extend(edge_cases)

        self._record_phase_status("routing", "fallback" if used_fallback else "success")
        return routing

    async def _execution_phase(
        self,
        routing: RoutingDecision,
        task: str,
    ) -> str:
        """Execute task based on routing decision."""

        assigned_agents = list(routing.assigned_to)
        subtasks = list(routing.subtasks)

        if routing.mode is ExecutionMode.PARALLEL:
            return await self._execute_parallel(assigned_agents, subtasks)
        elif routing.mode is ExecutionMode.SEQUENTIAL:
            return await self._execute_sequential(assigned_agents, task)
        else:
            return await self._execute_delegated(assigned_agents[0], task)

    async def _progress_phase(self, task: str, result: str) -> Dict[str, Any]:
        """Evaluate progress and provide next-step guidance."""

        used_fallback = False
        try:
            raw_progress = await self._call_with_retry(
                self.dspy_supervisor.evaluate_progress,
                original_task=task,
                completed=result,
                status="completion",
            )
            progress = self._normalize_progress_evaluation(raw_progress)
        except Exception as exc:
            logger.exception("DSPy progress evaluation failed; using fallback: %s", exc)
            progress = self._fallback_progress()
            used_fallback = True

        self._record_phase_status("progress", "fallback" if used_fallback else "success")
        return progress

    async def _quality_phase(self, task: str, result: str) -> Dict[str, Any]:
        """Assess final output quality."""

        used_fallback = False
        try:
            raw_quality = await self._call_with_retry(
                self.compiled_supervisor.assess_quality,
                requirements=task,
                results=result,
            )
            quality = self._normalize_quality_assessment(raw_quality, task, result)
        except Exception as exc:
            logger.exception("DSPy quality assessment failed; using fallback: %s", exc)
            quality = self._fallback_quality(task, result)
            used_fallback = True

        self._record_phase_status("quality", "fallback" if used_fallback else "success")
        return quality

    async def _call_judge_with_reasoning(self, judge_agent: ChatAgent, prompt: str) -> Any:
        """Call Judge agent with reasoning effort if configured.

        Uses the Responses API format for reasoning effort: {"reasoning": {"effort": "medium"}}
        This is passed in the request body via extra_body parameter.

        Args:
            judge_agent: The Judge ChatAgent instance
            prompt: The prompt to send to the judge

        Returns:
            Response from the judge agent
        """
        reasoning_effort = self.config.judge_reasoning_effort

        # Pass reasoning effort in request body using Responses API format
        # Format: {"reasoning": {"effort": "medium"}}
        if reasoning_effort and hasattr(judge_agent, "chat_client"):
            chat_client = judge_agent.chat_client

            try:
                # Try to set reasoning effort via extra_body (standard OpenAI SDK approach)
                # extra_body is merged into the request body
                if hasattr(chat_client, "extra_body"):
                    existing_extra_body = getattr(chat_client, "extra_body", None)
                    if not isinstance(existing_extra_body, dict):
                        existing_extra_body = {}
                    existing_extra_body["reasoning"] = {"effort": reasoning_effort}
                    setattr(chat_client, "extra_body", existing_extra_body)
                    logger.debug(f"Set reasoning effort via extra_body: {reasoning_effort}")
                elif hasattr(chat_client, "_default_extra_body"):
                    default_body = getattr(chat_client, "_default_extra_body", None)
                    if not isinstance(default_body, dict):
                        default_body = {}
                    default_body["reasoning"] = {"effort": reasoning_effort}
                    setattr(chat_client, "_default_extra_body", default_body)
                    logger.debug(
                        f"Set reasoning effort via _default_extra_body: {reasoning_effort}"
                    )
                else:
                    # Try to set on underlying async_client if available
                    async_client = getattr(chat_client, "async_client", None)
                    if async_client is not None:
                        setattr(chat_client, "_reasoning_effort", reasoning_effort)
                        logger.debug(f"Stored reasoning effort on chat client: {reasoning_effort}")
            except Exception as e:
                logger.warning(
                    f"Could not set reasoning effort directly: {e}. May need framework support."
                )

        # Call the agent's run method
        # The reasoning effort should be included in the request body if extra_body is supported
        return await judge_agent.run(prompt)

    async def _get_quality_criteria(self, task: str) -> str:
        """Generate task-specific quality criteria using Judge agent.

        Args:
            task: The task to generate criteria for

        Returns:
            Task-specific quality criteria string
        """
        if "Judge" not in self.agents:
            # Fallback to generic criteria if Judge not available
            return """Quality Criteria Checklist:
1. Accuracy: Is the information correct and factual?
2. Completeness: Does the response fully address the task?
3. Clarity: Is the response clear and well-structured?
4. Relevance: Is the response relevant to the task?"""

        try:
            judge_agent = self.agents["Judge"]

            # Ask Judge to generate task-specific criteria
            criteria_prompt = f"""Analyze the following task and generate appropriate quality criteria for evaluating responses to it.

Task: {task}

Generate 3-5 specific quality criteria that are relevant to this task type. Consider:
- For math/calculation tasks: focus on accuracy, correctness, step-by-step explanation
- For research tasks: focus on citations, dates, authoritative sources, factual accuracy
- For writing tasks: focus on clarity, structure, completeness, coherence
- For factual questions: focus on accuracy, sources, verification
- For simple questions: focus on correctness and clarity (don't require citations for basic facts)

Output ONLY the criteria list in this format:
1. Criterion name: Description of what to check
2. Criterion name: Description of what to check
...

Do not include any other text, just the numbered list of criteria."""

            criteria_response = await self._call_judge_with_reasoning(judge_agent, criteria_prompt)
            criteria_text = str(criteria_response) if criteria_response else ""

            # Clean up the response - extract just the criteria list
            if criteria_text.strip():
                # Remove any prefix/suffix text and keep just the numbered list
                lines = criteria_text.strip().split("\n")
                criteria_lines = []
                for line in lines:
                    line = line.strip()
                    # Keep lines that look like criteria (start with number or bullet)
                    if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                        criteria_lines.append(line)

                if criteria_lines:
                    return "Quality Criteria Checklist:\n" + "\n".join(criteria_lines)

            # Fallback if parsing fails
            logger.warning("Failed to parse generated criteria, using fallback")
            return """Quality Criteria Checklist:
1. Accuracy: Is the information correct and factual?
2. Completeness: Does the response fully address the task?
3. Clarity: Is the response clear and well-structured?"""

        except Exception as exc:
            logger.exception(f"Failed to generate dynamic criteria: {exc}, using fallback")
            # Fallback to generic criteria
            return """Quality Criteria Checklist:
1. Accuracy: Is the information correct and factual?
2. Completeness: Does the response fully address the task?
3. Clarity: Is the response clear and well-structured?
4. Relevance: Is the response relevant to the task?"""

    async def _judge_phase(self, task: str, result: str) -> Dict[str, Any]:
        """Judge evaluation phase using Judge ChatAgent from agent-framework."""
        if not self.config.enable_judge:
            logger.debug("Judge evaluation disabled, skipping")
            return {
                "score": 10.0,
                "missing_elements": "",
                "refinement_needed": "no",
                "refinement_agent": None,
                "required_improvements": "",
            }

        if "Judge" not in self.agents:
            logger.warning("Judge agent not available, skipping judge phase")
            return {
                "score": 10.0,
                "missing_elements": "",
                "refinement_needed": "no",
                "refinement_agent": None,
                "required_improvements": "",
            }

        try:
            judge_agent = self.agents["Judge"]

            # Generate task-specific quality criteria dynamically
            quality_criteria = await self._get_quality_criteria(task)
            logger.debug(f"Generated quality criteria for task: {quality_criteria[:200]}...")

            # Build evaluation prompt
            evaluation_prompt = f"""Evaluate the following response based on the task-specific quality criteria:

Task: {task}

Quality Criteria:
{quality_criteria}

Response to Evaluate:
{result}

Please provide your evaluation in the specified format:
Score: X/10 (where X reflects how well the response meets the task-specific criteria)
Missing elements: List what's missing based on the criteria above (comma-separated)
Refinement agent: Agent name that should handle improvements (Researcher, Analyst, or Writer)
Refinement needed: yes/no
Required improvements: Specific instructions for the refinement agent"""

            # Use agent-framework's agent.run() for judge evaluation with reasoning effort
            judge_response = await self._call_judge_with_reasoning(judge_agent, evaluation_prompt)
            judge_text = str(judge_response) if judge_response else ""

            # Parse judge's response to extract structured evaluation
            judge_eval = self._parse_judge_response(judge_text, task, result, quality_criteria)

            self._record_phase_status("judge", "success")
            logger.info(
                f"Judge evaluation: score={judge_eval['score']}/10, refinement_needed={
                    judge_eval['refinement_needed']
                }"
            )
            return judge_eval

        except Exception as exc:
            logger.exception("Judge evaluation failed: %s", exc)
            self._record_phase_status("judge", "failed")
            # Return default evaluation that doesn't trigger refinement
            return {
                "score": 10.0,
                "missing_elements": "",
                "refinement_needed": "no",
                "refinement_agent": None,
                "required_improvements": "",
            }

    def _parse_judge_response(
        self, response: str, task: str, result: str, quality_criteria: str
    ) -> Dict[str, Any]:
        """Parse judge's response to extract structured evaluation data."""
        # Default values
        score = 10.0
        missing_elements = ""
        refinement_needed = "no"
        refinement_agent = None
        required_improvements = ""

        response_lower = response.lower()

        # Extract score (look for "Score: X/10" or "X/10")
        score_match = re.search(r"score:\s*(\d+(?:\.\d+)?)/10", response_lower, re.IGNORECASE)
        if not score_match:
            score_match = re.search(r"(\d+(?:\.\d+)?)/10", response_lower)
        if score_match:
            try:
                score = float(score_match.group(1))
            except ValueError:
                pass

        # Extract missing elements
        missing_match = re.search(r"missing elements?:\s*([^\n]+)", response_lower, re.IGNORECASE)
        if missing_match:
            missing_elements = missing_match.group(1).strip()

        # Extract refinement needed
        refinement_match = re.search(
            r"refinement needed:\s*(yes|no)", response_lower, re.IGNORECASE
        )
        if refinement_match:
            refinement_needed = refinement_match.group(1).lower()

        # Extract refinement agent
        agent_match = re.search(r"refinement agent:\s*([^\n]+)", response_lower, re.IGNORECASE)
        if agent_match:
            refinement_agent = agent_match.group(1).strip()

        # Extract required improvements
        improvements_match = re.search(
            r"required improvements?:\s*([^\n]+(?:\n[^\n]+)*)", response_lower, re.IGNORECASE
        )
        if improvements_match:
            required_improvements = improvements_match.group(1).strip()

        # If score is below threshold, mark refinement as needed
        if score < self.config.judge_threshold and refinement_needed == "no":
            refinement_needed = "yes"
            if not refinement_agent:
                # Determine refinement agent based on missing elements
                refinement_agent = self._determine_refinement_agent(missing_elements)

        return {
            "score": score,
            "missing_elements": missing_elements,
            "refinement_needed": refinement_needed,
            "refinement_agent": refinement_agent,
            "required_improvements": required_improvements,
        }

    def _determine_refinement_agent(self, missing_elements: str) -> str:
        """Determine which agent should handle refinement based on missing elements."""
        missing_lower = missing_elements.lower() if missing_elements else ""

        # Map missing elements to appropriate agents
        if (
            "citation" in missing_lower
            or "source" in missing_lower
            or "link" in missing_lower
            or "url" in missing_lower
        ):
            return "Researcher"  # Researcher has TavilyMCPTool for citations
        elif (
            "vote" in missing_lower
            or "total" in missing_lower
            or "percentage" in missing_lower
            or "data" in missing_lower
        ):
            return "Researcher"  # Researcher can find data, or Analyst if calculation needed
        elif (
            "date" in missing_lower
            or "certification" in missing_lower
            or "context" in missing_lower
        ):
            return "Researcher"  # Researcher can find dates and context
        elif (
            "format" in missing_lower or "structure" in missing_lower or "writing" in missing_lower
        ):
            return "Writer"  # Writer handles formatting and structure
        else:
            return "Researcher"  # Default to Researcher

    def _build_refinement_task(self, current_result: str, judge_eval: Dict[str, Any]) -> str:
        """Build a refinement task based on judge evaluation."""
        missing_elements = judge_eval.get("missing_elements", "")
        required_improvements = judge_eval.get("required_improvements", "")

        refinement_task = f"""Improve the following response based on the judge's evaluation:

Missing elements: {missing_elements}
Required improvements: {required_improvements}

Current response:
{current_result}

Please enhance the response by addressing the missing elements and required improvements."""

        return refinement_task

    async def _timed_phase_call(
        self,
        phase: str,
        coro: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute a coroutine while recording execution time."""

        start = time.perf_counter()
        result = await coro(*args, **kwargs)
        elapsed = time.perf_counter() - start
        self._latest_phase_timings[phase] = elapsed
        return result

    def _record_phase_status(self, phase: str, status: str) -> None:
        """Record the status of a workflow phase.

        Args:
            phase: Phase name (e.g., "analysis", "routing", "execution", "quality")
            status: Status string (e.g., "success", "fallback", "cached", "failed")
        """
        self._latest_phase_status[phase] = status

    def _detect_routing_edge_cases(self, task: str, routing: RoutingDecision) -> List[str]:
        """
        Detect edge cases in routing decisions for logging and learning.

        Returns list of edge case descriptions.
        """
        edge_cases = []
        task_lower = task.lower()

        # Detect ambiguous tasks
        ambiguous_keywords = ["maybe", "possibly", "could", "might", "perhaps", "either", "or"]
        if any(kw in task_lower for kw in ambiguous_keywords):
            edge_cases.append("ambiguous_task")

        # Detect time-sensitive queries without web search tool
        time_keywords = [
            "latest",
            "current",
            "recent",
            "today",
            "now",
            "2025",
            "2026",
            "2027",
            "future",
        ]
        has_time_keyword = any(kw in task_lower for kw in time_keywords)
        has_web_search = "TavilySearchTool" in [
            t.lower() for t in routing.tool_requirements
        ] or "tavily" in [t.lower() for t in routing.tool_requirements]
        if has_time_keyword and not has_web_search:
            edge_cases.append("missing_web_search_for_time_sensitive")

        # Detect mode edge cases
        assigned_count = len(routing.assigned_to)
        if routing.mode == ExecutionMode.PARALLEL and assigned_count == 1:
            edge_cases.append("parallel_mode_single_agent")
        elif routing.mode == ExecutionMode.SEQUENTIAL and assigned_count == 1:
            edge_cases.append("sequential_mode_single_agent")
        elif routing.mode == ExecutionMode.DELEGATED and assigned_count > 1:
            edge_cases.append("delegated_mode_multiple_agents")

        # Detect tool conflicts
        if routing.tool_requirements:
            # Check if tools match assigned agents' capabilities
            for tool in routing.tool_requirements:
                tool_lower = tool.lower()
                if "tavily" in tool_lower and "Researcher" not in routing.assigned_to:
                    edge_cases.append("tool_agent_mismatch_tavily")
                if "codeinterpreter" in tool_lower or "hostedcode" in tool_lower:
                    if "Analyst" not in routing.assigned_to:
                        edge_cases.append("tool_agent_mismatch_code")

        return edge_cases

    def _validate_tool(self, tool: Any) -> bool:
        """Validate that a tool can be parsed by agent-framework.

        Args:
            tool: Tool instance to validate

        Returns:
            True if tool is valid, False otherwise
        """
        if tool is None:
            return False

        try:
            # Check if tool is a SerializationMixin (has to_dict method)
            from agent_framework._serialization import SerializationMixin

            if isinstance(tool, SerializationMixin):
                if not hasattr(tool, "to_dict"):
                    logger.warning(
                        f"Tool {type(tool).__name__} is SerializationMixin but missing to_dict()"
                    )
                    return False
                # Try calling to_dict to ensure it works
                tool_dict = tool.to_dict()
                if not isinstance(tool_dict, dict):
                    logger.warning(
                        f"Tool {type(tool).__name__}.to_dict() returned non-dict: {type(tool_dict)}"
                    )
                    return False
                return True

            # Check if tool is a dict
            if isinstance(tool, dict):
                return True

            # Check if tool is callable (function)
            if callable(tool):
                return True

            # Check if tool has required ToolProtocol attributes
            if hasattr(tool, "name") and hasattr(tool, "description"):
                # Tool implements ToolProtocol but not SerializationMixin
                # This will cause warnings, but we'll log it
                logger.debug(
                    f"Tool {type(tool).__name__} implements ToolProtocol but not SerializationMixin. "
                    "Consider adding SerializationMixin to avoid parsing warnings."
                )
                return True

            logger.warning(f"Tool {type(tool).__name__} does not match any recognized tool format")
            return False
        except Exception as e:
            logger.warning(f"Error validating tool {type(tool).__name__}: {e}")
            return False

    def _create_agent(
        self,
        name: str,
        description: str,
        instructions: str,
        tools: Optional[Any] = None,
        model_override: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
    ) -> ChatAgent:
        """Factory method for creating agents.

        Args:
            name: Agent name
            description: Agent description
            instructions: Agent instructions
            tools: Optional tool instance or list of tools
            model_override: Optional model ID override

        Returns:
            Configured ChatAgent instance
        """
        # Use shared OpenAI client (created once in initialize)
        if self._openai_client is None:
            self._openai_client = _create_openai_client_with_store(
                self.config.enable_completion_storage
            )
            logger.warning("OpenAI client created lazily - should be created in initialize()")

        agent_models = self.config.agent_models or {}
        model_id = model_override or agent_models.get(name.lower(), self.config.dspy_model)

        # Get agent-specific temperature if configured
        agent_temperatures = self.config.agent_temperatures or {}
        temperature = agent_temperatures.get(name.lower())

        # Create chat client with optional temperature and reasoning effort
        # Reasoning effort is passed in request body using Responses API format:
        # {"reasoning": {"effort": "medium"}}
        async_client = self._openai_client

        chat_client_kwargs: Dict[str, Any] = {
            "model_id": model_id,
            "async_client": async_client,
        }

        # Note: OpenAIChatClient may not support temperature directly in constructor
        # This is a placeholder for when the API supports it
        # For now, temperature is typically set via model parameters or chat options
        if temperature is not None:
            # Store temperature for potential future use or pass via chat_options
            # The actual implementation depends on agent-framework's OpenAIChatClient API
            logger.debug(f"Agent {name} temperature configured: {temperature}")

        # Validate and filter tools before passing to ChatAgent
        validated_tools = None
        if tools is not None:
            if isinstance(tools, list):
                # Validate each tool in the list
                validated_tools = [tool for tool in tools if self._validate_tool(tool)]
                invalid_count = len(tools) - len(validated_tools)
                if invalid_count > 0:
                    logger.warning(
                        f"Filtered out {invalid_count} invalid tool(s) for agent {name}. "
                        f"Valid tools: {len(validated_tools)}"
                    )
                # Convert to single tool if only one, or None if empty
                if len(validated_tools) == 0:
                    validated_tools = None
                elif len(validated_tools) == 1:
                    validated_tools = validated_tools[0]
            else:
                # Single tool
                if self._validate_tool(tools):
                    validated_tools = tools
                else:
                    logger.warning(f"Invalid tool for agent {name}, skipping tool assignment")
                    validated_tools = None

        # Create the chat client
        chat_client = OpenAIChatClient(**chat_client_kwargs)

        # For Judge agent with reasoning effort, set extra_body after creation
        # Reasoning effort is passed in request body using Responses API format:
        # {"reasoning": {"effort": "medium"}}
        # extra_body is merged into the request body by OpenAI SDK
        if reasoning_effort is not None and name == "Judge":
            # Set extra_body to include reasoning effort in Responses API format
            # Try to set it on the chat client if it supports extra_body
            try:
                if hasattr(chat_client, "extra_body"):
                    setattr(chat_client, "extra_body", {"reasoning": {"effort": reasoning_effort}})
                    logger.debug(
                        f"Judge agent configured with reasoning effort via extra_body: {reasoning_effort}"
                    )
                else:
                    # Store as attribute for potential use in _call_judge_with_reasoning
                    chat_client._reasoning_effort = reasoning_effort  # type: ignore[attr-defined]
                    logger.debug(
                        f"Judge agent reasoning effort stored: {reasoning_effort} (will be applied in request)"
                    )
            except Exception as e:
                logger.warning(f"Could not set reasoning effort on chat client: {e}")

        return ChatAgent(
            name=name,
            description=description,
            instructions=instructions,
            chat_client=chat_client,
            tools=validated_tools,
        )

    def _create_agents(self) -> Dict[str, ChatAgent]:
        """Create specialized agents for the workflow."""

        agents = {}

        # Researcher with Tavily (optional) and BrowserTool
        researcher_tools = []
        tavily_mcp_tool = None
        try:
            import os

            # Add Tavily if available (via MCP)
            if os.getenv("TAVILY_API_KEY"):
                tavily_mcp_tool = TavilyMCPTool()  # type: ignore[abstract]
                researcher_tools.append(tavily_mcp_tool)
                logger.info("TavilyMCPTool enabled for Researcher")
            else:
                logger.warning(
                    "TAVILY_API_KEY not set - Researcher will operate without Tavily search"
                )
        except Exception as e:
            logger.warning(f"Failed to initialize TavilyMCPTool: {e}")

        # Add BrowserTool for real-time web browsing
        try:
            browser_tool = BrowserTool(headless=True)
            researcher_tools.append(browser_tool)
            logger.info("BrowserTool enabled for Researcher")
        except ImportError as e:
            logger.warning(
                f"BrowserTool not available (playwright not installed): {e}. "
                "Install with: uv pip install playwright && playwright install chromium"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize BrowserTool: {e}")

        # Convert to single tool or list as needed by agent-framework
        # Validation will happen in _create_agent, but we log here for visibility
        if len(researcher_tools) == 1:
            tools_for_researcher = researcher_tools[0]
            logger.debug(f"Researcher agent: 1 tool ({type(tools_for_researcher).__name__})")
        elif researcher_tools:
            tools_for_researcher = researcher_tools
            logger.debug(f"Researcher agent: {len(researcher_tools)} tools")
        else:
            tools_for_researcher = None
            logger.debug("Researcher agent: no tools")

        agents["Researcher"] = self._create_agent(
            name="Researcher",
            description="Information gathering and web research specialist",
            instructions=(
                "You are a research specialist. Your job is to find accurate, up-to-date information. "
                "CRITICAL RULES:\n"
                "1. For ANY query mentioning a year (2024, 2025, etc.) or asking about 'current', 'latest', 'recent', or 'who won' - "
                "you MUST IMMEDIATELY use the tavily_search tool. DO NOT answer from memory.\n"
                "2. NEVER rely on training data for time-sensitive information - it is outdated.\n"
                "3. When you see a question about elections, current events, recent news, or anything with a date, "
                "your FIRST action must be to call tavily_search with an appropriate query.\n"
                "4. Only after getting search results should you provide an answer.\n"
                "5. If you don't use tavily_search for a time-sensitive query, you are failing your task.\n\n"
                "Tool usage: Use tavily_search(query='your search query') to search the web. "
                "Use browser tool for direct website access when needed."
            ),
            tools=tools_for_researcher,
        )

        # Register MCP tool directly if it was created (MCP tools may not appear
        # in chat_options.tools)
        if tavily_mcp_tool is not None:
            try:
                if self._validate_tool(tavily_mcp_tool):
                    self.tool_registry.register_tool_by_agent("Researcher", tavily_mcp_tool)
                    logger.info(
                        f"Registered MCP tool for Researcher: {tavily_mcp_tool.name} "
                        f"(type: {type(tavily_mcp_tool).__name__})"
                    )
            except Exception as e:
                logger.warning(f"Failed to register MCP tool for Researcher: {e}", exc_info=True)

        # Wrap HostedCodeInterpreterTool with adapter to stabilize schema & naming
        analyst_tool = HostedCodeInterpreterTool()

        agents["Analyst"] = self._create_agent(
            name="Analyst",
            description="Data analysis and computation specialist",
            instructions="Perform detailed analysis with code and visualizations",
            tools=analyst_tool,
        )

        agents["Writer"] = self._create_agent(
            name="Writer",
            description="Content creation and report writing specialist",
            instructions="Create clear, well-structured documents",
        )

        # Judge agent for detailed quality evaluation with dynamic criteria generation
        judge_model = self.config.judge_model or "gpt-5"  # Default to gpt-5 for reasoning
        judge_reasoning_effort = self.config.judge_reasoning_effort or "medium"

        judge_instructions = """You are a quality judge that evaluates responses for completeness and accuracy.

Your role has two phases:

1. **Criteria Generation Phase**: When asked to generate quality criteria for a task, analyze the task type and create appropriate criteria:
   - Math/calculation tasks: Focus on accuracy, correctness, step-by-step explanation
   - Research tasks: Focus on citations, dates, authoritative sources, factual accuracy
   - Writing tasks: Focus on clarity, structure, completeness, coherence
   - Factual questions: Focus on accuracy, sources, verification
   - Simple questions (like "2+2"): Focus on correctness and clarity (DO NOT require citations for basic facts)

2. **Evaluation Phase**: When evaluating a response, use the provided task-specific criteria to assess:
   - How well the response meets each criterion
   - What's missing if the response is incomplete
   - Which agent should handle refinement (Researcher for citations/sources, Analyst for calculations/data, Writer for clarity/structure)
   - Specific improvement instructions

Always adapt your evaluation to the task type - don't require citations for simple math problems, and don't require calculations for research questions.

Output your evaluation in this format:
Score: X/10 (where X reflects how well the response meets the task-specific criteria)
Missing elements: List what's missing based on the criteria (comma-separated)
Refinement agent: Agent name that should handle improvements (Researcher, Analyst, or Writer)
Refinement needed: yes/no
Required improvements: Specific instructions for the refinement agent"""

        agents["Judge"] = self._create_agent(
            name="Judge",
            description="Quality evaluation specialist with dynamic task-aware criteria assessment",
            instructions=judge_instructions,
            model_override=judge_model,
            reasoning_effort=judge_reasoning_effort,
        )

        # Keep Reviewer for backward compatibility, but it's now a simpler version
        agents["Reviewer"] = self._create_agent(
            name="Reviewer",
            description="Quality assurance and validation specialist",
            instructions="Ensure accuracy, completeness, and quality",
        )

        return agents

    def _build_workflow(self):
        """Build the Magentic workflow."""

        # Use shared OpenAI client (created in initialize)
        if self._openai_client is None:
            self._openai_client = _create_openai_client_with_store(
                self.config.enable_completion_storage
            )
            logger.warning(
                "OpenAI client created lazily in _build_workflow - should be created in initialize()"
            )

        # Create supervisor agent
        supervisor = ChatAgent(
            name="Supervisor",
            description="Intelligent workflow orchestrator powered by DSPy",
            instructions=self._get_supervisor_instructions(),
            chat_client=OpenAIChatClient(
                model_id=self.config.dspy_model, async_client=self._openai_client
            ),
        )

        # Build workflow with all agents
        workflow = (
            MagenticBuilder()
            .participants(supervisor=supervisor, **self.agents)
            .with_standard_manager(
                chat_client=OpenAIChatClient(
                    model_id=self.config.dspy_model,
                    async_client=self._openai_client,
                ),
                max_round_count=self.config.max_rounds,
                max_stall_count=self.config.max_stalls,
                max_reset_count=self.config.max_resets,
            )
            .build()
        )

        return workflow

    def _get_supervisor_instructions(self) -> str:
        """Get supervisor agent instructions including tool catalog."""

        team_desc = "\n".join(
            [f"- {name}: {agent.description}" for name, agent in self.agents.items()]
        )

        # Provide tool catalog for richer initial context (helps model propose
        # tool usage even before DSPy analysis)
        tool_catalog = (
            self.tool_registry.get_tool_descriptions()
            if self.tool_registry
            else "No tools registered yet."
        )

        return f"""You are an intelligent supervisor using DSPy optimization.

        Your approach:
        1. Analyze tasks using DSPy routing intelligence (prefer tool-aware analysis when tools are available)
        2. Delegate to appropriate team members
        3. Monitor progress and provide feedback
        4. Ensure quality standards are met

        Team members:
        {team_desc}

        Available tools:
        {tool_catalog}

        Guidance:
        - When tools match task needs, include them in routing rationale
        - Only invoke code execution for computation or data transformation tasks
        - Use web search when current, external info is required
        - Prefer minimal tool invocations necessary to achieve objectives

        Use DSPy-based decisions for optimal task routing and workflow management.
        """

    async def run(self, task: str) -> Dict[str, Any]:
        """Execute the workflow for a given task."""

        # Validate task input
        task = _validate_task(task, max_length=self.config.max_task_length)

        logger.info(f"Starting workflow for task: {task[:100]}...")
        self._latest_phase_timings = {}
        self._latest_phase_status = {}

        # Analyze task with DSPy
        task_analysis = await self._timed_phase_call("analysis", self._analysis_phase, task)
        logger.info(f"Task complexity: {task_analysis['complexity']}")

        # Route task
        routing = await self._timed_phase_call("routing", self._routing_phase, task, task_analysis)

        logger.info(
            "Routing decision: %s to %s (confidence=%s)",
            routing.mode.value,
            list(routing.assigned_to),
            f"{routing.confidence:.2f}" if routing.confidence is not None else "n/a",
        )

        assigned_agents = list(routing.assigned_to)  # noqa: F841
        subtasks = list(routing.subtasks)  # noqa: F841

        # Execute based on routing mode
        result = await self._timed_phase_call("execution", self._execution_phase, routing, task)

        # Evaluate progress
        progress = await self._timed_phase_call("progress", self._progress_phase, task, str(result))

        # Quality assessment
        quality = await self._timed_phase_call("quality", self._quality_phase, task, str(result))

        logger.info(f"Quality score: {quality['score']}/10")

        # Judge evaluation phase (if enabled)
        judge_evaluations = []
        if self.config.enable_judge:
            judge_eval = await self._timed_phase_call("judge", self._judge_phase, task, str(result))
            judge_evaluations.append(judge_eval)
            logger.info(
                f"Judge evaluation: score={judge_eval['score']}/10, refinement_needed={
                    judge_eval['refinement_needed']
                }"
            )

            # Refinement loop using agent-framework
            refinement_rounds = 0
            while (
                refinement_rounds < self.config.max_refinement_rounds
                and judge_eval.get("refinement_needed", "no").lower() == "yes"
                and judge_eval.get("score", 0.0) < self.config.judge_threshold
            ):
                refinement_rounds += 1
                logger.info(
                    f"Starting refinement round {refinement_rounds}/{self.config.max_refinement_rounds}"
                )

                # Determine refinement agent
                refinement_agent_name = judge_eval.get("refinement_agent")
                if not refinement_agent_name or refinement_agent_name not in self.agents:
                    refinement_agent_name = self._determine_refinement_agent(
                        judge_eval.get("missing_elements", "")
                    )

                if refinement_agent_name not in self.agents:
                    logger.warning(
                        f"Refinement agent '{refinement_agent_name}' not available, skipping refinement"
                    )
                    break

                # Build refinement task
                refinement_task = self._build_refinement_task(str(result), judge_eval)

                # Execute refinement using agent-framework's agent.run()
                try:
                    refinement_agent = self.agents[refinement_agent_name]
                    refined_result = await refinement_agent.run(refinement_task)
                    result = str(refined_result) if refined_result else result
                    logger.info(f"Refinement completed by {refinement_agent_name}")
                except Exception as exc:
                    logger.exception(f"Refinement failed: {exc}")
                    break

                # Re-evaluate with judge
                judge_eval = await self._timed_phase_call(
                    "judge", self._judge_phase, task, str(result)
                )
                judge_evaluations.append(judge_eval)
                logger.info(
                    f"Judge re-evaluation (round {refinement_rounds}): score={judge_eval['score']}/10, "
                    f"refinement_needed={judge_eval['refinement_needed']}"
                )

                # Stop refinement if threshold is met or judge says no more needed
                judge_score = judge_eval.get("score", 0.0)
                if judge_score >= self.config.judge_threshold:
                    logger.info(
                        f"Quality threshold met ({judge_score} >= {
                            self.config.judge_threshold
                        }), stopping refinement"
                    )
                    break
                elif judge_eval.get("refinement_needed", "no").lower() == "no":
                    logger.info("Judge determined no further refinement needed")
                    break

        # Legacy refinement (if enabled and judge is disabled)
        elif (
            self.config.enable_refinement
            and quality["score"] < self.config.refinement_threshold
            and progress["action"] == "refine"
        ):
            logger.info(
                f"Quality below threshold ({self.config.refinement_threshold}), refining results..."
            )
            result = await self._refine_results(result, quality["improvements"])

        # Update quality assessment with final judge evaluation if available
        if judge_evaluations:
            last_judge = judge_evaluations[-1]
            # Update quality with final judge score for better accuracy
            quality["score"] = last_judge.get("score", quality["score"])
            quality["judge_score"] = last_judge.get("score")
            quality["final_evaluation"] = last_judge

        return {
            "result": result,
            "routing": routing.to_dict(),
            "quality": quality,
            "judge_evaluations": judge_evaluations,
            "execution_summary": self.dspy_supervisor.get_execution_summary(),
            "phase_timings": dict(self._latest_phase_timings),
            "phase_status": dict(self._latest_phase_status),
        }

    def _normalize_routing_decision(
        self, routing: RoutingDecision | Dict[str, Any], task: str
    ) -> RoutingDecision:
        """Ensure routing output has valid agents, mode, and subtasks."""

        decision = ensure_routing_decision(routing)

        valid_agents = tuple(agent for agent in decision.assigned_to if agent in self.agents)
        if not valid_agents:
            fallback = next(iter(self.agents.keys()), None)
            if fallback is None:
                raise RoutingError("No agents are registered in the workflow.", decision.to_dict())
            valid_agents = (fallback,)

        mode = decision.mode
        if mode not in {
            ExecutionMode.PARALLEL,
            ExecutionMode.SEQUENTIAL,
            ExecutionMode.DELEGATED,
        }:
            mode = ExecutionMode.DELEGATED

        if len(valid_agents) == 1 and mode is ExecutionMode.PARALLEL:
            logger.info("Switching from parallel to delegated mode (only one agent)")
            mode = ExecutionMode.DELEGATED

        subtasks = tuple(self._prepare_subtasks(list(valid_agents), list(decision.subtasks), task))

        return decision.update(
            assigned_to=valid_agents,
            mode=mode,
            subtasks=subtasks,
        )

    def _prepare_subtasks(
        self, agents: List[str], subtasks: Optional[List[str]], fallback_task: str
    ) -> List[str]:
        """Normalize DSPy-provided subtasks to align with assigned agents."""
        if not agents:
            return []

        normalized: List[str]
        if not subtasks:
            normalized = [fallback_task for _ in agents]
        else:
            normalized = [str(task) for task in subtasks]

        if len(normalized) < len(agents):
            normalized.extend([fallback_task] * (len(agents) - len(normalized)))
        elif len(normalized) > len(agents):
            normalized = normalized[: len(agents)]

        return normalized

    async def _execute_parallel(self, agents: List[str], subtasks: List[str]) -> str:
        """Execute subtasks in parallel without streaming."""
        tasks = []
        agent_names = []

        for agent_name, subtask in zip(agents, subtasks):
            agent = self.agents.get(agent_name)
            if not agent:
                logger.warning("Skipping unknown agent '%s' during parallel execution", agent_name)
                continue
            tasks.append(agent.run(subtask))
            agent_names.append(agent_name)

        if not tasks:
            raise AgentExecutionError(
                agent_name="unknown",
                task="parallel execution",
                original_error=RuntimeError("No valid agents available"),
            )

        # Execute with exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        successful_results = []
        for agent_name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                logger.error(f"Agent '{agent_name}' failed: {result}")
                successful_results.append(f"[{agent_name} failed: {str(result)}]")
            else:
                successful_results.append(str(result))

        return self._synthesize_results(successful_results)

    async def _execute_sequential(self, agents: List[str], task: str) -> str:
        """Execute a task sequentially across agents without streaming."""
        if not agents:
            raise AgentExecutionError(
                agent_name="unknown",
                task="sequential execution",
                original_error=RuntimeError("Sequential execution requires at least one agent"),
            )

        # Use handoff-enabled execution if available
        if self.enable_handoffs and self.handoff_manager:
            return await self._execute_sequential_with_handoffs(agents, task)

        # Standard sequential execution (original behavior)
        result: Any = task
        for agent_name in agents:
            agent = self.agents.get(agent_name)
            if not agent:
                logger.warning(
                    "Skipping unknown agent '%s' during sequential execution",
                    agent_name,
                )
                continue
            result = await agent.run(str(result))

        return str(result)

    async def _execute_sequential_with_handoffs(self, agents: List[str], task: str) -> str:
        """Execute sequential workflow with intelligent handoffs.

        This method uses the HandoffManager to create structured handoffs
        between agents with rich context, artifacts, and quality criteria.
        """
        if not self.handoff_manager:
            logger.warning("HandoffManager not initialized, falling back to standard sequential")
            return await self._execute_sequential(agents, task)

        result = task
        artifacts: Dict[str, Any] = {}

        for i, current_agent_name in enumerate(agents):
            agent = self.agents.get(current_agent_name)
            if not agent:
                logger.warning(f"Skipping unknown agent '{current_agent_name}'")
                continue

            # Execute current agent's work
            logger.info(f"Agent {current_agent_name} starting work")
            agent_result = await agent.run(str(result))

            # Extract artifacts from result (simplified - could be more sophisticated)
            current_artifacts = self._extract_artifacts(agent_result)
            artifacts.update(current_artifacts)

            # Check if handoff is needed (before last agent)
            if i < len(agents) - 1:
                next_agent_name = agents[i + 1]
                remaining_work = self._estimate_remaining_work(task, str(agent_result))

                # Evaluate if handoff should proceed
                handoff_decision = await self.handoff_manager.evaluate_handoff(
                    current_agent=current_agent_name,
                    work_completed=str(agent_result),
                    remaining_work=remaining_work,
                    available_agents={
                        name: self.agents[name].description
                        for name in agents[i + 1 :]
                        if name in self.agents
                    },
                )

                # Create handoff package if recommended
                if handoff_decision == next_agent_name:
                    remaining_objectives = self._derive_objectives(remaining_work)

                    handoff_context = await self.handoff_manager.create_handoff_package(
                        from_agent=current_agent_name,
                        to_agent=next_agent_name,
                        work_completed=str(agent_result),
                        artifacts=artifacts,
                        remaining_objectives=remaining_objectives,
                        task=task,
                        handoff_reason=f"Sequential workflow: {current_agent_name} completed, passing to {next_agent_name}",
                    )

                    # Format handoff as structured input for next agent
                    result = self._format_handoff_input(handoff_context)

                    logger.info(f"✓ Handoff created: {current_agent_name} → {next_agent_name}")
                    logger.info(f"  Estimated effort: {handoff_context.estimated_effort}")
                else:
                    # Simple pass-through (current behavior)
                    result = str(agent_result)
            else:
                # Last agent - no handoff needed
                result = str(agent_result)

        return str(result)

    def _extract_artifacts(self, result: Any) -> Dict[str, Any]:
        """Extract artifacts from agent result.

        In a real implementation, this would parse structured output,
        identify files/data produced, etc. For now, it's a placeholder.
        """
        # Placeholder - could be enhanced to extract structured data
        return {"result_summary": str(result)[:200]}

    def _estimate_remaining_work(self, original_task: str, work_done: str) -> str:
        """Estimate what work remains based on original task and progress."""
        # Simple heuristic - in practice, could use DSPy for this
        return f"Continue working on: {original_task}. Already completed: {work_done[:100]}..."

    def _derive_objectives(self, remaining_work: str) -> List[str]:
        """Derive specific objectives from remaining work description."""
        # Simple extraction - could use NLP or DSPy
        objectives = [remaining_work]
        return objectives

    def _format_handoff_input(self, handoff: HandoffContext) -> str:
        """Format handoff context as structured input for next agent."""
        return f"""
# HANDOFF FROM {handoff.from_agent}

## Work Completed
{handoff.work_completed}

## Your Objectives
{chr(10).join(f"- {obj}" for obj in handoff.remaining_objectives)}

## Success Criteria
{chr(10).join(f"- {crit}" for crit in handoff.success_criteria)}

## Available Artifacts
{chr(10).join(f"- {k}: {v}" for k, v in handoff.artifacts.items())}

## Quality Checklist
{chr(10).join(f"- [ ] {item}" for item in handoff.quality_checklist)}

## Required Tools
{", ".join(handoff.tool_requirements) if handoff.tool_requirements else "None"}

---
Please continue the work based on the above context.
"""

    async def _execute_delegated(self, agent_name: str, task: str) -> str:
        """Delegate the task to a single agent without streaming."""
        agent = self.agents.get(agent_name)
        if not agent:
            raise AgentExecutionError(
                agent_name=agent_name,
                task=task,
                original_error=RuntimeError(f"Agent '{agent_name}' not found"),
            )

        response = await agent.run(task)
        return str(response)

    async def _execute_parallel_streaming(self, agents: List[str], subtasks: List[str]):
        """Execute subtasks in parallel with streaming."""

        tasks = []
        agent_names = []
        for agent_name, subtask in zip(agents, subtasks):
            if agent_name in self.agents:
                tasks.append(self.agents[agent_name].run(subtask))
                agent_names.append(agent_name)

        # Yield start events for each agent
        for agent_name in agent_names:
            yield MagenticAgentMessageEvent(
                agent_id=agent_name,
                message=ChatMessage(role=Role.ASSISTANT, text="Starting parallel execution..."),
            )

        # Execute with exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Yield completion events and handle exceptions
        successful_results = []
        for agent_name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                logger.error(f"Agent '{agent_name}' failed: {result}")
                error_msg = f"[{agent_name} failed: {str(result)}]"
                yield MagenticAgentMessageEvent(
                    agent_id=agent_name,
                    message=ChatMessage(role=Role.ASSISTANT, text=f"Failed: {str(result)}"),
                )
                successful_results.append(error_msg)
            else:
                yield MagenticAgentMessageEvent(
                    agent_id=agent_name,
                    message=ChatMessage(role=Role.ASSISTANT, text=f"Completed: {str(result)}"),
                )
                successful_results.append(str(result))

        # Yield final synthesized result
        final_result = self._synthesize_results(successful_results)
        yield WorkflowOutputEvent(
            data={"result": final_result},
            source_executor_id="parallel_execution",
        )

    async def _execute_sequential_streaming(self, agents: List[str], task: str):
        """Execute task sequentially through agents with streaming."""

        result = task
        for agent_name in agents:
            if agent_name in self.agents:
                yield MagenticAgentMessageEvent(
                    agent_id=agent_name,
                    message=ChatMessage(role=Role.ASSISTANT, text="Processing task..."),
                )

                response = await self.agents[agent_name].run(result)

                yield MagenticAgentMessageEvent(
                    agent_id=agent_name,
                    message=ChatMessage(role=Role.ASSISTANT, text=f"Completed: {str(response)}"),
                )

                result = str(response)

        # Yield final result
        yield WorkflowOutputEvent(
            data={"result": result},
            source_executor_id="sequential_execution",
        )

    async def _execute_delegated_streaming(self, agent_name: str, task: str):
        """Delegate task to single agent with streaming."""

        if agent_name in self.agents:
            yield MagenticAgentMessageEvent(
                agent_id=agent_name,
                message=ChatMessage(role=Role.ASSISTANT, text="Processing task..."),
            )

            response = await self.agents[agent_name].run(task)

            yield MagenticAgentMessageEvent(
                agent_id=agent_name,
                message=ChatMessage(role=Role.ASSISTANT, text=f"Completed: {str(response)}"),
            )

            # Yield final result
            yield WorkflowOutputEvent(
                data={"result": str(response)},
                source_executor_id="delegated_execution",
            )

    def _synthesize_results(self, results: List[Any]) -> str:
        """Combine parallel results."""
        return "\n\n".join([str(r) for r in results])

    async def _refine_results(self, results: Any, improvements: str) -> Any:
        """Refine results based on quality assessment."""

        refinement_task = f"Refine these results based on improvements needed:\n{results}\n\nImprovements: {improvements}"
        response = await self.agents["Writer"].run(refinement_task)
        return str(response)

    async def run_stream(self, task: str):
        """Run workflow with streaming output using DSPy-enhanced execution."""

        task = _validate_task(task, max_length=self.config.max_task_length)

        execution_start = datetime.now()
        self._latest_phase_timings = {}
        self._latest_phase_status = {}
        self.current_execution = {
            "task": task,
            "start_time": execution_start.isoformat(),
            "events": [],
            "dspy_analysis": {},
            "routing": {},
            "progress": {},
            "agent_executions": [],
            "quality": {},
            "result": None,
            "phase_timings": {},
            "phase_status": {},
        }

        logger.info("\n" + "=" * 80)
        logger.info("STARTING NEW WORKFLOW EXECUTION")
        logger.info(f"Task: {task}")
        logger.info(f"Start Time: {execution_start.isoformat()}")
        logger.info("=" * 80)

        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(
                role=Role.ASSISTANT,
                text=f"Starting DSPy-enhanced workflow for task: {task[:100]}...",
            ),  # type: ignore[arg-type]
        )

        # Analysis phase
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(role=Role.ASSISTANT, text="Analyzing task with DSPy..."),  # type: ignore[arg-type]
        )
        analysis = await self._timed_phase_call("analysis", self._analysis_phase, task)
        self.current_execution["dspy_analysis"] = {
            "complexity": analysis["complexity"],
            "capabilities": analysis["capabilities"],
            "tool_requirements": analysis.get("tool_requirements", []),
            "steps": analysis["steps"],
            "needs_web_search": analysis.get("needs_web_search", False),
            "search_query": analysis.get("search_query", ""),
            "search_context": analysis.get("search_context", ""),
        }
        logger.info(
            "Analysis complete: complexity=%s, steps=%s",
            analysis["complexity"],
            analysis["steps"],
        )
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(
                role=Role.ASSISTANT,
                text=(
                    f"Task complexity: {analysis['complexity']} | Required: {', '.join(analysis['capabilities'][:3])}"
                ),
            ),  # type: ignore[arg-type]
        )

        # Routing phase
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(role=Role.ASSISTANT, text="Routing task to agents..."),  # type: ignore[arg-type]
        )
        routing = await self._timed_phase_call("routing", self._routing_phase, task, analysis)
        self.current_execution["routing"] = {
            "mode": routing.mode.value,
            "assigned_to": list(routing.assigned_to),
            "subtasks": list(routing.subtasks),
            "tool_requirements": list(routing.tool_requirements),
            "confidence": routing.confidence,
        }
        logger.info(
            "Routing decision: mode=%s, agents=%s, confidence=%s",
            routing.mode.value,
            ", ".join(routing.assigned_to),
            f"{routing.confidence:.2f}" if routing.confidence is not None else "n/a",
        )
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(
                role=Role.ASSISTANT,
                text=f"Routing decision: {routing.mode.value} to {list(routing.assigned_to)}",
            ),  # type: ignore[arg-type]
        )

        # Execution phase with streaming
        assigned_agents = list(routing.assigned_to)
        subtasks = list(routing.subtasks)
        exec_start = time.perf_counter()
        result: Optional[str] = None

        if routing.mode is ExecutionMode.PARALLEL:
            logger.info("Executing in PARALLEL mode with %d agents", len(assigned_agents))
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    text=f"Executing {len(assigned_agents)} subtasks in parallel...",
                ),  # type: ignore[arg-type]
            )
            async for event in self._execute_parallel_streaming(assigned_agents, subtasks):
                if (
                    hasattr(event, "data")
                    and isinstance(event.data, dict)
                    and "result" in event.data
                ):
                    result = str(event.data["result"])
                else:
                    yield event
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(role=Role.ASSISTANT, text="Parallel execution completed."),  # type: ignore[arg-type]
            )
        elif routing.mode is ExecutionMode.SEQUENTIAL:
            logger.info("Executing in SEQUENTIAL mode through %d agents", len(assigned_agents))
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    text=f"Executing task sequentially through {len(assigned_agents)} agents...",
                ),  # type: ignore[arg-type]
            )
            async for event in self._execute_sequential_streaming(assigned_agents, task):
                if (
                    hasattr(event, "data")
                    and isinstance(event.data, dict)
                    and "result" in event.data
                ):
                    result = str(event.data["result"])
                else:
                    yield event
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(role=Role.ASSISTANT, text="Sequential execution completed."),  # type: ignore[arg-type]
            )
        else:
            logger.info("Executing in DELEGATED mode with agent: %s", assigned_agents[0])
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(
                    role=Role.ASSISTANT, text=f"Delegating task to {assigned_agents[0]}..."
                ),
                # type: ignore[arg-type]
            )
            async for event in self._execute_delegated_streaming(assigned_agents[0], task):
                if (
                    hasattr(event, "data")
                    and isinstance(event.data, dict)
                    and "result" in event.data
                ):
                    result = str(event.data["result"])
                else:
                    yield event
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(role=Role.ASSISTANT, text="Delegation completed."),  # type: ignore[arg-type]
            )

        self._latest_phase_timings["execution"] = time.perf_counter() - exec_start
        self._record_phase_status("execution", "success")

        if result is None:
            result = ""

        # Progress phase
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(role=Role.ASSISTANT, text="Evaluating progress..."),  # type: ignore[arg-type]
        )
        progress = await self._timed_phase_call("progress", self._progress_phase, task, result)
        self.current_execution["progress"] = progress
        logger.info("Progress evaluation: action=%s", progress["action"])

        # Quality phase
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(role=Role.ASSISTANT, text="Assessing quality..."),  # type: ignore[arg-type]
        )
        quality = await self._timed_phase_call("quality", self._quality_phase, task, result)
        self.current_execution["quality"] = quality
        logger.info("Quality assessment score: %s", quality["score"])
        yield MagenticAgentMessageEvent(
            agent_id="supervisor",
            message=ChatMessage(role=Role.ASSISTANT, text=f"Quality score: {quality['score']}/10"),  # type: ignore[arg-type]
        )

        # Judge evaluation phase (if enabled)
        judge_evaluations = []
        if self.config.enable_judge:
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(role=Role.ASSISTANT, text="Judge evaluating response..."),  # type: ignore[arg-type]
            )
            judge_eval = await self._timed_phase_call("judge", self._judge_phase, task, str(result))
            judge_evaluations.append(judge_eval)
            logger.info(
                f"Judge evaluation: score={judge_eval['score']}/10, refinement_needed={
                    judge_eval['refinement_needed']
                }"
            )
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(
                    role=Role.ASSISTANT, text=f"Judge score: {judge_eval['score']}/10"
                ),
                # type: ignore[arg-type]
            )

            # Refinement loop using agent-framework
            refinement_rounds = 0
            while (
                refinement_rounds < self.config.max_refinement_rounds
                and judge_eval.get("refinement_needed", "no").lower() == "yes"
                and judge_eval.get("score", 0.0) < self.config.judge_threshold
            ):
                refinement_rounds += 1
                logger.info(
                    f"Starting refinement round {refinement_rounds}/{self.config.max_refinement_rounds}"
                )
                yield MagenticAgentMessageEvent(
                    agent_id="supervisor",
                    # type: ignore[arg-type]
                    message=ChatMessage(
                        role=Role.ASSISTANT,
                        text=f"Refining answer (round {refinement_rounds}/{self.config.max_refinement_rounds})...",
                    ),
                )

                # Determine refinement agent
                refinement_agent_name = judge_eval.get("refinement_agent")
                if not refinement_agent_name or refinement_agent_name not in self.agents:
                    refinement_agent_name = self._determine_refinement_agent(
                        judge_eval.get("missing_elements", "")
                    )

                if refinement_agent_name not in self.agents:
                    logger.warning(
                        f"Refinement agent '{refinement_agent_name}' not available, skipping refinement"
                    )
                    break

                # Build refinement task
                refinement_task = self._build_refinement_task(str(result), judge_eval)

                # Execute refinement using agent-framework's agent.run()
                try:
                    refinement_agent = self.agents[refinement_agent_name]
                    yield MagenticAgentMessageEvent(
                        agent_id="supervisor",
                        message=ChatMessage(
                            role=Role.ASSISTANT, text=f"{refinement_agent_name} refining answer..."
                        ),
                        # type: ignore[arg-type]
                    )
                    refined_result = await refinement_agent.run(refinement_task)
                    result = str(refined_result) if refined_result else result
                    logger.info(f"Refinement completed by {refinement_agent_name}")
                    yield MagenticAgentMessageEvent(
                        agent_id=refinement_agent_name,
                        message=ChatMessage(role=Role.ASSISTANT, text="Refinement completed"),  # type: ignore[arg-type]
                    )
                except Exception as exc:
                    logger.exception(f"Refinement failed: {exc}")
                    break

                # Re-evaluate with judge
                yield MagenticAgentMessageEvent(
                    agent_id="supervisor",
                    # type: ignore[arg-type]
                    message=ChatMessage(
                        role=Role.ASSISTANT, text="Re-evaluating refined answer..."
                    ),
                )
                judge_eval = await self._timed_phase_call(
                    "judge", self._judge_phase, task, str(result)
                )
                judge_evaluations.append(judge_eval)
                logger.info(
                    f"Judge re-evaluation (round {refinement_rounds}): score={judge_eval['score']}/10, "
                    f"refinement_needed={judge_eval['refinement_needed']}"
                )
                yield MagenticAgentMessageEvent(
                    agent_id="supervisor",
                    # type: ignore[arg-type]
                    message=ChatMessage(
                        role=Role.ASSISTANT, text=f"Judge re-evaluation: {judge_eval['score']}/10"
                    ),
                )

                # Stop refinement if threshold is met or judge says no more needed
                judge_score = judge_eval.get("score", 0.0)
                if judge_score >= self.config.judge_threshold:
                    logger.info(
                        f"Quality threshold met ({judge_score} >= {
                            self.config.judge_threshold
                        }), stopping refinement"
                    )
                    yield MagenticAgentMessageEvent(
                        agent_id="supervisor",
                        message=ChatMessage(
                            role=Role.ASSISTANT,
                            text=f"Quality threshold met ({judge_score}/10 >= {self.config.judge_threshold}/10), refinement complete",
                        ),
                        # type: ignore[arg-type]
                    )
                    break
                elif judge_eval.get("refinement_needed", "no").lower() == "no":
                    logger.info("Judge determined no further refinement needed")
                    yield MagenticAgentMessageEvent(
                        agent_id="supervisor",
                        # type: ignore[arg-type]
                        message=ChatMessage(
                            role=Role.ASSISTANT,
                            text="Judge determined no further refinement needed",
                        ),
                    )
                    break

        # Legacy refinement (if enabled and judge is disabled)
        elif (
            self.config.enable_refinement
            and quality["score"] < self.config.refinement_threshold
            and progress["action"] == "refine"
        ):
            logger.info(
                f"Quality below threshold ({self.config.refinement_threshold}), refining results..."
            )
            yield MagenticAgentMessageEvent(
                agent_id="supervisor",
                message=ChatMessage(role=Role.ASSISTANT, text="Refining results..."),  # type: ignore[arg-type]
            )
            result = await self._refine_results(result, quality["improvements"])

        # Update quality assessment with final judge evaluation if available
        if judge_evaluations:
            last_judge = judge_evaluations[-1]
            # Update quality with final judge score for better accuracy
            quality["score"] = last_judge.get("score", quality["score"])
            quality["judge_score"] = last_judge.get("score")
            quality["final_evaluation"] = last_judge

        # Update current_execution with final result and judge evaluations
        self.current_execution["result"] = result[:500] if result else ""
        self.current_execution["judge_evaluations"] = judge_evaluations
        self.current_execution["quality"] = quality  # Update with final quality

        # Finalize execution tracking
        execution_end = datetime.now()
        total_time = (execution_end - execution_start).total_seconds()
        self.current_execution["end_time"] = execution_end.isoformat()
        self.current_execution["total_time_seconds"] = total_time
        self.current_execution["execution_summary"] = self.dspy_supervisor.get_execution_summary()
        self.current_execution["phase_timings"] = dict(self._latest_phase_timings)
        self.current_execution["phase_status"] = dict(self._latest_phase_status)

        if self.handoff_manager and self.handoff_manager.handoff_history:
            self.current_execution["handoff_history"] = [
                handoff.to_dict() for handoff in self.handoff_manager.handoff_history
            ]
            self.current_execution["handoff_summary"] = self.handoff_manager.get_handoff_summary()
        else:
            self.current_execution["handoff_history"] = []

        self.execution_history.append(self.current_execution.copy())
        history_file = await self.history_manager.save_execution_async(self.current_execution)

        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW EXECUTION COMPLETED")
        logger.info(f"Total Execution Time: {total_time:.2f}s")
        result_text = result or ""
        logger.info(f"Result Length: {len(result_text)} characters")
        logger.info(f"History saved to: {history_file}")
        logger.info("=" * 80 + "\n")

        yield WorkflowOutputEvent(
            data={
                "result": result_text,
                "routing": routing.to_dict(),
                "quality": quality,
                "judge_evaluations": judge_evaluations,
                "execution_summary": self.dspy_supervisor.get_execution_summary(),
                "phase_timings": dict(self._latest_phase_timings),
                "phase_status": dict(self._latest_phase_status),
            },
            source_executor_id="supervisor",
        )


async def create_supervisor_workflow(compile_dspy: bool = True) -> SupervisorWorkflow:
    """Factory function to create and initialize supervisor workflow."""

    workflow = SupervisorWorkflow()
    await workflow.initialize(compile_dspy=compile_dspy)
    return workflow
