from __future__ import annotations

from typing import TYPE_CHECKING

import click
import toml
from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path


class ProjectConfig(BaseModel):
    """Project configuration from ev.toml."""

    project_id: str


def load_project_config(ev_config_path: Path) -> ProjectConfig:
    """Load project configuration from ev.toml file.

    Args:
        ev_config_path: Path to ev.toml file

    Returns:
        ProjectConfig instance

    Raises:
        click.ClickException: If file doesn't exist, can't be read, or is invalid
    """
    if not ev_config_path.exists():
        raise click.ClickException("No ev.toml file found. Run 'ev init' first to initialize the project.")

    try:
        with ev_config_path.open("r", encoding="utf-8") as f:
            ev_config = toml.load(f)
    except Exception as e:
        raise click.ClickException(f"Failed to read ev.toml from: {ev_config_path}") from e

    try:
        pconf = ProjectConfig.model_validate(ev_config)
    except Exception as e:
        raise click.ClickException(
            "Invalid ev.toml format. Expected 'project_id' field. Please run 'ev init' to initialize the project."
        ) from e

    return pconf
