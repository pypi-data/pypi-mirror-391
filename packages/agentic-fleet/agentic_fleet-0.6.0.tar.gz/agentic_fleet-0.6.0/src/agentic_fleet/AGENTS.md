# AGENTS.md

## Overview

`src/agentic_fleet/` contains the DSPy-enhanced runtime that powers the Magentic Fleet orchestration layer. It
instantiates specialists from declarative YAML, compiles DSPy supervisors, streams OpenAI-compatible Responses
events, and wires optional integrations such as Hosted Code Interpreter, Tavily search, or MCP bridges. Treat
this directory as the source of truth for workflow behaviour—adjust configuration through the YAML helpers and
`AgentFactory` instead of hardcoding values.

## Runtime Layout

| Path                          | Purpose                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `console.py`                  | Rich + Typer console powering the `dspy-fleet` command, streaming Responses events, running workflows, and exposing handoff exploration. |
| `main.py`                     | uvicorn-friendly entrypoint that re-exports the FastAPI app supplied by the agent-framework HTTP surface.                                |
| `manage_cache.py`             | Utility to inspect or clear the DSPy compilation cache stored under `logs/compiled_supervisor.pkl`.                                      |
| `agents/`                     | Specialist configuration modules and `coordinator.AgentFactory` for building `ChatAgent` instances from YAML.                            |
| `prompts/`                    | Prompt modules exposing `get_instructions()` for planner/executor/coder/verifier/generator specialists.                                  |
| `workflows/`                  | `SupervisorWorkflow`, `HandoffManager`, and workflow-specific exceptions orchestrating agent execution.                                  |
| `dspy_modules/`               | DSPy `Signatures`, handoff-specific signatures, and `DSPySupervisor` implementation.                                                     |
| `tools/`                      | Tool adapters (Hosted Code Interpreter, Tavily search, browser automation, MCP bridge) resolved by the tool registry.                    |
| `utils/`                      | Configuration loader, DSPy compiler cache, GEPA optimizer, history manager, telemetry bootstrap, models, tracing, and `ToolRegistry`.    |
| `evaluation/`                 | Batch evaluation engine and metrics used by CLI commands and scripts.                                                                    |
| `config/workflow_config.yaml` | Authoritative configuration for DSPy settings, agent rosters, routing thresholds, quality gates, and tool toggles.                       |
| `data/`                       | Training examples (`supervisor_examples.json`) and evaluation datasets consumed by DSPy compilation and batch runs.                      |
| `scripts/`                    | Helpers for history analysis, evaluation dataset generation, and self-improvement loops.                                                 |
| `examples/`                   | Minimal scripts such as `simple_workflow.py` demonstrating workflow execution.                                                           |
| `cli/`                        | Thin package exposing entry points that defer to the Rich console utilities.                                                             |

## Agent Rosters

### Supervisor default team

- **Researcher** — Retrieves context, performs web search (via `TavilySearchTool`), and drafts initial findings.
- **Analyst** — Uses the Hosted Code Interpreter to validate data, run computations, or manipulate artifacts.
- **Writer** — Synthesises polished narrative outputs based on accumulated context and intermediate results.
- **Reviewer** — Provides quality gates and structured critiques before final delivery.

### Handoff specialists

- **Planner (`agents.planner`)** — Performs high-effort reasoning to decompose the request into discrete steps and assign ownership.
- **Executor (`agents.executor`)** — Coordinates progress across specialists, escalates blockers, and tracks plan completion.
- **Coder (`agents.coder`)** — Low-temperature technical implementer with Hosted Code Interpreter access for patches and prototypes.
- **Verifier (`agents.verifier`)** — Validates intermediate outputs, flags regressions, and drives refinement loops.
- **Generator (`agents.generator`)** — Produces the final user-facing response once intermediate work is verified.

Updates to any roster require concurrent changes in `config/workflow_config.yaml`, the relevant `agents/*.py` module, prompt modules, and coverage in the workflow/evaluation tests.

## DSPy Supervisor & Workflow Pipeline

1. **Task Analysis** – `DSPySupervisor.analyze_task` extracts goals, constraints, and tooling hints using DSPy `ChainOfThought` signatures.
2. **Task Routing** – `DSPySupervisor.route_task` selects agents, execution mode (delegated/sequential/parallel), and tool requirements.
3. **Agent Execution** – `SupervisorWorkflow` executes the plan, leveraging the `ToolRegistry`, `HandoffManager`, and agent-framework builders.
4. **Quality Assessment** – `DSPySupervisor.evaluate_progress` and `assess_quality` score results; sub‑threshold scores trigger refinement loops or judge-based reviews.

Event streams are emitted as OpenAI Responses-compatible payloads consumed by the CLI, TUI, and optional frontend.

## Configuration & Environment

- `config/workflow_config.yaml` governs DSPy models, GEPA optimization knobs, agent definitions, tool toggles, quality thresholds, tracing, and evaluation settings.
- Required environment variable: `OPENAI_API_KEY`. Optional: `OPENAI_BASE_URL`, `TAVILY_API_KEY`, `DSPY_COMPILE` (force recompilation), `ENABLE_OTEL`, `OTLP_ENDPOINT`, plus integration-specific credentials (Mem0, Cosmos DB, etc.).
- Load `.env` for local development; production deployments should inject secrets via managed stores or environment configuration.
- Keep behaviour declarative—reference prompt modules (`prompts.executor`, etc.) rather than embedding instruction strings inline.

## Tools & Integrations

- Tool registry resolves names declared in YAML to concrete instances (`HostedCodeInterpreterTool`, `TavilySearchTool`, browser automation, MCP adapters).
- GEPA optimization (`utils/gepa_optimizer.py`) accelerates DSPy compilation and supports history-informed reruns.
- OpenTelemetry tracing hooks live in `utils/tracing.py` and align with AI Toolkit collectors.
- History capture and analytics live in `utils/history_manager.py` and the `scripts/` helpers.

## CLI & Automation

- `uv run python console.py run -m "..."` – Run a single workflow (streamed or buffered).
- `uv run python console.py handoff --interactive` – Explore agent handoffs with `HandoffManager`.
- `uv run python console.py analyze --dataset data/evaluation_tasks.jsonl` – Batch evaluation with metrics logged to `logs/evaluation/`.
- `uv run python manage_cache.py --info|--clear` – Inspect or clear DSPy compilation cache.
- Entry point `dspy-fleet` wraps the console for shorter commands.
- `scripts/self_improve.py` updates DSPy training examples from history; `scripts/analyze_history.py` surfaces execution analytics.

## Testing & Validation

- `make test` / `uv run pytest -v` – Backend tests (stubs avoid external API calls).
- `make test-config` – Validates YAML wiring and agent imports.
- `make check` – Runs Ruff, Black, and mypy to enforce style and typing.
- `make validate-agents` – Ensures documentation and configuration stay in sync (when the validation script is enabled).

## Troubleshooting

- **Missing API keys** – `ValueError: OPENAI_API_KEY is not set`; load `.env` or export the key before invoking workflows.
- **Tavily not available** – The researcher falls back to reasoning-only mode if `TAVILY_API_KEY` is absent; expect reduced context gathering.
- **Slow DSPy compilation** – Reduce GEPA limits in `workflow_config.yaml` (`gepa_max_metric_calls`, `max_bootstrapped_demos`) or clear cache before reruns.
- **Tool resolution warnings** – Ensure tool names in YAML exist in `ToolRegistry` and relevant extras are installed.
- **No streaming output** – Confirm `workflow.supervisor.enable_streaming` is true and tracing exporters are not throwing OTLP errors (suppress via logging settings if needed).
