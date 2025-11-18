"""Tests for config loader utility."""

import os
import tempfile

import yaml

from agentic_fleet.utils.config_loader import (
    load_config,
    get_default_config,
    get_agent_model,
    get_agent_temperature,
)


def test_get_default_config():
    """Test default configuration."""
    config = get_default_config()

    assert config["dspy"]["model"] == "gpt-4.1"
    assert config["workflow"]["supervisor"]["max_rounds"] == 15
    assert config["workflow"]["handoffs"]["enabled"] is True
    assert config["openai"]["enable_completion_storage"] is False
    assert config["logging"]["history_file"] == "logs/execution_history.jsonl"


def test_load_config_missing_file():
    """Test loading config when file doesn't exist."""
    config = load_config("nonexistent.yaml")

    assert config == get_default_config()


def test_load_config_valid_file():
    """Test loading config from valid YAML file."""
    test_config = {
        "dspy": {"model": "gpt-3.5-turbo", "temperature": 0.5},
        "workflow": {"supervisor": {"max_rounds": 10}},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(test_config, f)
        temp_path = f.name

    try:
        config = load_config(temp_path)
        assert config["dspy"]["model"] == "gpt-3.5-turbo"
        assert config["dspy"]["temperature"] == 0.5
        assert config["workflow"]["supervisor"]["max_rounds"] == 10
    finally:
        os.unlink(temp_path)


def test_get_agent_model():
    """Test getting agent-specific model from config."""
    config = {
        "agents": {
            "researcher": {"model": "gpt-4", "temperature": 0.5},
            "analyst": {"model": "gpt-3.5-turbo"},
        }
    }

    assert get_agent_model(config, "researcher") == "gpt-4"
    assert get_agent_model(config, "analyst") == "gpt-3.5-turbo"
    assert get_agent_model(config, "unknown", "default-model") == "default-model"


def test_get_agent_temperature():
    """Test getting agent-specific temperature from config."""
    config = {
        "agents": {
            "researcher": {"temperature": 0.5},
            "analyst": {"model": "gpt-4"},
        }
    }

    assert get_agent_temperature(config, "researcher") == 0.5
    assert get_agent_temperature(config, "analyst", 0.8) == 0.8
    assert get_agent_temperature(config, "unknown", 0.7) == 0.7
