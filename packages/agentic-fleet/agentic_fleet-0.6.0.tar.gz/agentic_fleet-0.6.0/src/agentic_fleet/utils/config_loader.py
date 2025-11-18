"""Configuration loader for workflow settings."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file (defaults to config/workflow_config.yaml)

    Returns:
        Dictionary with configuration settings
    """
    if config_path is None:
        config_path = "config/workflow_config.yaml"

    config_file = Path(config_path)

    if not config_file.exists():
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return get_default_config()

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config or get_default_config()
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Return default configuration."""
    return {
        "dspy": {
            "model": "gpt-4.1",
            "temperature": 0.7,
            "max_tokens": 2000,
            "optimization": {
                "enabled": True,
                "examples_path": "data/supervisor_examples.json",
                "metric_threshold": 0.8,
                "max_bootstrapped_demos": 4,
                "use_gepa": False,
                "gepa_auto": "light",
                "gepa_max_full_evals": 50,
                "gepa_max_metric_calls": 150,
                "gepa_reflection_model": None,
                "gepa_log_dir": "logs/gepa",
                "gepa_perfect_score": 1.0,
                "gepa_use_history_examples": False,
                "gepa_history_min_quality": 8.0,
                "gepa_history_limit": 200,
                "gepa_val_split": 0.2,
                "gepa_seed": 13,
            },
        },
        "workflow": {
            "supervisor": {
                "max_rounds": 15,
                "max_stalls": 3,
                "max_resets": 2,
                "enable_streaming": True,
            },
            "execution": {
                "parallel_threshold": 3,
                "timeout_seconds": 300,
                "retry_attempts": 2,
            },
            "quality": {
                "refinement_threshold": 8.0,
                "enable_refinement": True,
                "judge_model": None,
                "judge_reasoning_effort": "medium",
            },
            "handoffs": {
                "enabled": True,
            },
        },
        "agents": {
            "researcher": {
                "model": "gpt-4.1",
                "tools": ["TavilyMCPTool"],
                "temperature": 0.5,
            },
            "analyst": {
                "model": "gpt-4.1",
                "tools": ["HostedCodeInterpreterTool"],
                "temperature": 0.3,
            },
            "writer": {
                "model": "gpt-4.1",
                "tools": [],
                "temperature": 0.7,
            },
            "reviewer": {
                "model": "gpt-4.1",
                "tools": [],
                "temperature": 0.2,
            },
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/workflow.log",
            "save_history": True,
            "history_file": "logs/execution_history.jsonl",
            "verbose": True,
        },
        "openai": {
            "enable_completion_storage": False,
        },
        "tracing": {
            "enabled": False,
            "otlp_endpoint": "http://localhost:4317",
            "capture_sensitive": True,
        },
        "evaluation": {
            "enabled": False,
            "dataset_path": "data/evaluation_tasks.jsonl",
            "output_dir": "logs/evaluation",
            "metrics": [
                "quality_score",
                "keyword_success",
                "latency_seconds",
                "routing_efficiency",
                "refinement_triggered",
            ],
            "max_tasks": 0,
            "stop_on_failure": False,
        },
    }


def get_agent_model(config: Dict[str, Any], agent_name: str, default: str = "gpt-4.1") -> str:
    """Get model for specific agent from config."""
    try:
        value = config.get("agents", {}).get(agent_name.lower(), {}).get("model", default)
        return str(value)
    except Exception:
        return default


def get_agent_temperature(config: Dict[str, Any], agent_name: str, default: float = 0.7) -> float:
    """Get temperature for specific agent from config."""
    try:
        value = config.get("agents", {}).get(agent_name.lower(), {}).get("temperature", default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    except Exception:
        return default
