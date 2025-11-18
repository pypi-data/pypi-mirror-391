"""Configuration management for CommitAid."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages CommitAid configuration."""

    CONFIG_DIR = Path.home() / ".config" / "commitaid"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    VALID_KEYS = {
        "commit-spec": str,
        "auto-signoff": lambda v: v in ["enabled", "disabled"]
    }

    def __init__(self):
        """Initialize config and ensure config directory exists."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._config = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.CONFIG_FILE.exists():
            return {}

        try:
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config: {e}")
            return {}

    def _save(self):
        """Save configuration to file."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save config: {e}")
            return False
        return True

    def set(self, key: str, value: str) -> bool:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            True if successful, False otherwise
        """
        if key not in self.VALID_KEYS:
            print(f"Error: Invalid config key '{key}'")
            print(f"Valid keys: {', '.join(self.VALID_KEYS.keys())}")
            return False

        validator = self.VALID_KEYS[key]
        if callable(validator) and validator != str:
            if not validator(value):
                if key == "auto-signoff":
                    print(f"Error: '{key}' must be 'enabled' or 'disabled'")
                else:
                    print(f"Error: Invalid value for '{key}'")
                return False

        self._config[key] = value
        if self._save():
            print(f"Configuration updated: {key} = {value}")
            return True
        return False

    def get(self, key: str) -> Optional[str]:
        """
        Get a configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value or None if not set
        """
        return self._config.get(key)

    def view(self, key: Optional[str] = None):
        """
        View configuration.

        Args:
            key: Specific key to view, or None to view all
        """
        if key:
            if key not in self.VALID_KEYS:
                print(f"Error: Invalid config key '{key}'")
                print(f"Valid keys: {', '.join(self.VALID_KEYS.keys())}")
                return

            value = self._config.get(key)
            if value is None:
                print(f"{key}: (not set)")
            else:
                print(f"{key}: {value}")
        else:
            if not self._config:
                print("No configuration set")
                return

            print("Current configuration:")
            for k, v in self._config.items():
                print(f"  {k}: {v}")
