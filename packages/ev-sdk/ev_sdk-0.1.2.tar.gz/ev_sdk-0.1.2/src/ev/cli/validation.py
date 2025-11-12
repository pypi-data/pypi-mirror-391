"""Input validation utilities for CLI commands."""

from __future__ import annotations

import click


def validate_name(name: str, max_length: int = 96, name_type: str = "Name") -> str:
    """Validate a name for length constraints.

    Args:
        name: The name to validate
        max_length: Maximum allowed length (default: 96)
        name_type: Type of name for error messages (e.g., "Project name", "Profile name")

    Returns:
        The validated name (stripped of whitespace)

    Raises:
        click.BadParameter: If name is empty or exceeds max length
    """
    name = name.strip()

    if not name:
        raise click.BadParameter(f"{name_type} cannot be empty")

    if len(name) > max_length:
        raise click.BadParameter(f"{name_type} must be {max_length} characters or less (got {len(name)} characters)")

    return name


def prompt_with_validation(
    prompt_text: str, default: str | None = None, max_length: int = 96, name_type: str = "Name"
) -> str:
    """Prompt for input with validation, re-prompting on validation errors.

    Args:
        prompt_text: The prompt text to display
        default: Default value if user provides no input
        max_length: Maximum allowed length for the input
        name_type: Type of name for error messages

    Returns:
        The validated input string
    """
    while True:
        try:
            value = click.prompt(prompt_text, default=default).strip()
            if not value and default:
                value = default
            return validate_name(value, max_length=max_length, name_type=name_type)
        except click.BadParameter as e:
            click.echo(f"Error: {e.message}")
            click.echo("Please try again.")
