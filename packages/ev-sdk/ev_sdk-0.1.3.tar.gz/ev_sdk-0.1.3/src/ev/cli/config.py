from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import click
import toml


class Config:
    """Configuration management for Daft Cloud CLI."""

    def __init__(self, config_data: dict[str, Any], config_path: Path, profile: str) -> None:
        """Private constructor. Use Config.load() to create instances."""
        self._config_toml = config_data
        self._config_path = config_path
        self._profile = profile
        self._validate()

    # TODO(rchowell): proper pydantic validation
    def _validate(self) -> None:
        """Validate config structure, raise clear error for old format."""
        if "default" in self._config_toml and "workspace" in self._config_toml["default"]:
            raise click.ClickException(
                f"Invalid configuration found at '{self._config_path}', please remove this file."
            )

    @classmethod
    def get_path(cls) -> tuple[Path, bool]:
        """Returns the configuration path and whether using default EV_HOME."""
        ev_home = os.environ.get("EV_HOME")
        if ev_home:
            return Path(ev_home) / "config.toml", False
        else:
            return Path.home() / ".ev" / "config.toml", True

    @classmethod
    def load(cls, profile: str | None = None, path: Path | None = None) -> Config:
        """Load configuration from TOML file.

        Args:
            profile: Profile name to load. If None, uses value from [default][profile] or "default"
            path: Path to config file (not directory). If None, uses get_path() to determine
                  from EV_HOME environment variable or default location.
        """
        config_path = cls.get_path()[0] if path is None else path

        if not config_path.exists():
            return cls({}, config_path, profile or "default")

        try:
            with config_path.open("rt", encoding="utf-8") as f:
                config_data = toml.load(f)
        except Exception as e:
            raise click.ClickException(f"Failed to load config from '{config_path}'.") from e

        # If no profile specified, check [default] section
        if profile is None:
            default_section = config_data.get("default", {})
            profile = default_section.get("profile", "default")

        return cls(config_data, config_path, profile)

    @property
    def endpoint_url(self) -> str:
        """Get endpoint URL for current profile."""
        profiles = self._config_toml.get("profiles", {})
        profile_config = profiles.get(self._profile, {})
        endpoint = profile_config.get("endpoint_url", "https://api.daft.ai")
        return str(endpoint)

    @endpoint_url.setter
    def endpoint_url(self, value: str) -> None:
        """Set endpoint URL for current profile."""
        self._set_profile_value("endpoint_url", value)

    @property
    def dashboard_url(self) -> str:
        """Get dashboard URL for current profile."""
        profiles = self._config_toml.get("profiles", {})
        profile_config = profiles.get(self._profile, {})
        dashboard = profile_config.get("dashboard_url", "https://cloud.daft.ai")
        return str(dashboard)

    @dashboard_url.setter
    def dashboard_url(self, value: str) -> None:
        """Set dashboard URL for current profile."""
        self._set_profile_value("dashboard_url", value)

    @property
    def profile(self) -> str:
        """Get current profile name."""
        return self._profile

    @property
    def profiles(self) -> list[str]:
        """Get list of all profile names."""
        return list(self._config_toml.get("profiles", {}).keys())

    def create_or_update_profile(self, name: str, endpoint_url: str) -> None:
        """Create new profile with endpoint URL.

        Args:
            name: Profile name
            endpoint_url: API endpoint URL for the profile
        """
        if "profiles" not in self._config_toml:
            self._config_toml["profiles"] = {}

        if name not in self._config_toml["profiles"]:
            self._config_toml["profiles"][name] = {}

        # Set endpoint_url for the profile
        self._config_toml["profiles"][name]["endpoint_url"] = endpoint_url
        self._save()

    def set_default_profile(self, name: str) -> None:
        """Set default profile."""
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' does not exist")

        if "default" not in self._config_toml:
            self._config_toml["default"] = {}
        self._config_toml["default"]["profile"] = name
        self._save()

    def _get_profile_value(self, key: str) -> str:
        """Get value from current profile."""
        profiles = self._config_toml.get("profiles", {})
        profile_config = profiles.get(self._profile, {})

        value = profile_config.get(key)
        if not value:
            raise click.ClickException(
                f"No {key} configured for profile '{self._profile}'. Run 'ev configure' to set up your profile."
            )
        return str(value)

    def _set_profile_value(self, key: str, value: str) -> None:
        """Set value in current profile."""
        if "profiles" not in self._config_toml:
            self._config_toml["profiles"] = {}
        if self._profile not in self._config_toml["profiles"]:
            self._config_toml["profiles"][self._profile] = {}

        self._config_toml["profiles"][self._profile][key] = value
        self._save()

    def _save(self) -> None:
        """Save configuration to TOML file."""
        self._config_path.parent.mkdir(exist_ok=True, parents=True)
        try:
            with self._config_path.open("w", encoding="utf-8") as f:
                toml.dump(self._config_toml, f)
        except Exception as e:
            raise click.ClickException(f"Failed to save config to '{self._config_path}'.") from e
