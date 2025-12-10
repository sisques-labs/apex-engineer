"""Configuration manager for ApexEngineer"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigManager:
    """Manages application configuration from YAML file"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            self.create_default_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.get_default_config()

    def create_default_config(self) -> None:
        """Create default configuration file if it doesn't exist"""
        default_config = self.get_default_config()
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        self.config = default_config
        print(f"Created default configuration at {self.config_path}")

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration dictionary"""
        return {
            "ai": {
                "model": "gpt4all",
                "model_name": "ggml-gpt4all-j-v1.3-groovy.bin",
                "model_path": None,
                "endpoint": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 150,
                "n_threads": 4,
            },
            "telemetry": {
                "game": "assetto_corsa",
                "update_rate": 10,
            },
            "voice": {
                "push_to_talk_key": "SPACE",
                "stt_enabled": True,
                "tts_enabled": False,
                "microphone_index": None,
            },
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path

        Args:
            key_path: Dot-separated path to config value (e.g., "ai.model")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value by dot-separated key path

        Args:
            key_path: Dot-separated path to config value
            value: Value to set
        """
        keys = key_path.split(".")
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def save(self) -> None:
        """Save current configuration to file"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
