"""
Custom exceptions for workflow operations.
"""


class WorkflowError(Exception):
    """Base exception for workflow-related errors."""

    pass


class AgentExecutionError(WorkflowError):
    """Raised when an agent fails during execution."""

    def __init__(self, agent_name: str, task: str, original_error: Exception):
        self.agent_name = agent_name
        self.task = task
        self.original_error = original_error
        super().__init__(f"Agent '{agent_name}' failed on task: {task}")


class RoutingError(WorkflowError):
    """Raised when task routing fails or produces invalid results."""

    def __init__(self, message: str, routing_decision: dict | None = None):
        self.routing_decision = routing_decision
        super().__init__(message)


class ConfigurationError(WorkflowError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None):
        self.config_key = config_key
        super().__init__(message)


class HistoryError(WorkflowError):
    """Raised when execution history operations fail."""

    def __init__(self, message: str, history_file: str | None = None):
        self.history_file = history_file
        super().__init__(message)
