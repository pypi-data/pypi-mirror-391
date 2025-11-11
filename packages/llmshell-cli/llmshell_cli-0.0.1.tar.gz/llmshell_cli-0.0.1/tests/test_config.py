"""Tests for configuration management."""

import pytest
from pathlib import Path
import tempfile
import yaml

from gpt_shell.config import Config, DEFAULT_CONFIG


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_config_init_creates_default(temp_config_dir):
    """Test that config initialization creates default config."""
    config_path = temp_config_dir / "config.yaml"
    config = Config(config_path)
    
    assert config_path.exists()
    assert config.config == DEFAULT_CONFIG


def test_config_load_existing(temp_config_dir):
    """Test loading existing config."""
    config_path = temp_config_dir / "config.yaml"
    
    # Create custom config
    custom_config = {
        "llm_backend": "openai",
        "backends": {
            "openai": {
                "api_key": "test-key",
                "model": "gpt-4"
            }
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(custom_config, f)
    
    config = Config(config_path)
    assert config.get("llm_backend") == "openai"
    assert config.get("backends.openai.api_key") == "test-key"


def test_config_get(temp_config_dir):
    """Test getting config values."""
    config_path = temp_config_dir / "config.yaml"
    config = Config(config_path)
    
    # Test simple key
    assert config.get("llm_backend") == "gpt4all"
    
    # Test nested key with dot notation
    assert config.get("backends.gpt4all.model") is not None
    
    # Test non-existent key with default
    assert config.get("nonexistent", "default") == "default"


def test_config_set(temp_config_dir):
    """Test setting config values."""
    config_path = temp_config_dir / "config.yaml"
    config = Config(config_path)
    
    # Set simple value
    config.set("llm_backend", "openai")
    assert config.get("llm_backend") == "openai"
    
    # Set nested value
    config.set("backends.openai.api_key", "new-key")
    assert config.get("backends.openai.api_key") == "new-key"
    
    # Verify it's saved to file
    config2 = Config(config_path)
    assert config2.get("llm_backend") == "openai"
    assert config2.get("backends.openai.api_key") == "new-key"


def test_config_get_backend_config(temp_config_dir):
    """Test getting backend-specific config."""
    config_path = temp_config_dir / "config.yaml"
    config = Config(config_path)
    
    # Get GPT4All config
    gpt4all_config = config.get_backend_config("gpt4all")
    assert "model" in gpt4all_config
    
    # Get current backend config
    current_config = config.get_backend_config()
    assert current_config == gpt4all_config


def test_config_list_backends(temp_config_dir):
    """Test listing available backends."""
    config_path = temp_config_dir / "config.yaml"
    config = Config(config_path)
    
    backends = config.list_backends()
    assert "gpt4all" in backends
    assert "openai" in backends
    assert "ollama" in backends
    assert "custom" in backends


def test_config_get_models_dir(temp_config_dir):
    """Test getting models directory."""
    config_path = temp_config_dir / "config.yaml"
    config = Config(config_path)
    
    models_dir = config.get_models_dir()
    assert models_dir.exists()
    assert models_dir.is_dir()


def test_config_merge_with_defaults(temp_config_dir):
    """Test that user config merges with defaults."""
    config_path = temp_config_dir / "config.yaml"
    
    # Create minimal config
    minimal_config = {
        "llm_backend": "openai"
    }
    
    with open(config_path, "w") as f:
        yaml.dump(minimal_config, f)
    
    config = Config(config_path)
    
    # Should have user's backend
    assert config.get("llm_backend") == "openai"
    
    # Should still have default backends config
    assert "backends" in config.to_dict()
    assert "gpt4all" in config.to_dict()["backends"]
