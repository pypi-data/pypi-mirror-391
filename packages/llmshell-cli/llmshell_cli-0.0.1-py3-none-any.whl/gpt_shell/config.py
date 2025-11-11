"""Configuration management for llmshell."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


DEFAULT_CONFIG = {
    "llm_backend": "gpt4all",
    "backends": {
        "gpt4all": {
            "model": "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
            "model_path": None,  # Auto-detect or download
        },
        "openai": {
            "api_key": None,
            "model": "gpt-4-turbo",
            "base_url": None,
        },
        "ollama": {
            "model": "llama3",
            "api_url": "http://localhost:11434",
        },
        "custom": {
            "api_url": None,
            "headers": {},
        },
    },
    "execution": {
        "auto_execute": False,
        "confirmation_required": True,
    },
    "output": {
        "colored": True,
        "verbose": False,
    },
}


class Config:
    """Configuration manager for llmshell."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config file. Defaults to ~/.llmshell/config.yaml
        """
        if config_path is None:
            config_path = Path.home() / ".llmshell" / "config.yaml"
        self.config_path = config_path
        self.config_dir = config_path.parent
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file, creating default if not exists."""
        if not self.config_path.exists():
            self.create_default()
        else:
            try:
                with open(self.config_path, "r") as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        self.config = self._merge_with_defaults(loaded_config)
                    else:
                        self.config = DEFAULT_CONFIG.copy()
            except Exception as e:
                print(f"Warning: Error loading config: {e}")
                self.config = DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user config with defaults.

        Args:
            user_config: User-provided configuration

        Returns:
            Merged configuration
        """
        merged = DEFAULT_CONFIG.copy()
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            """Recursively merge dictionaries."""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(merged, user_config)

    def create_default(self) -> None:
        """Create default configuration file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = DEFAULT_CONFIG.copy()
        self.save()

    def save(self) -> None:
        """Save current configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'backends.openai.api_key')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()

    def get_backend_config(self, backend: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for specific backend.

        Args:
            backend: Backend name. If None, uses current llm_backend setting

        Returns:
            Backend configuration dictionary
        """
        if backend is None:
            backend = self.config.get("llm_backend", "gpt4all")
        return self.config.get("backends", {}).get(backend, {})

    def list_backends(self) -> list[str]:
        """
        List available backends.

        Returns:
            List of backend names
        """
        return list(self.config.get("backends", {}).keys())

    def get_models_dir(self) -> Path:
        """
        Get directory for storing downloaded models.

        Returns:
            Path to models directory
        """
        models_dir = self.config_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        return models_dir

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()
