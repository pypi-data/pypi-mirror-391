from __future__ import annotations

import re
from typing import TYPE_CHECKING

import click
from rich.console import Console

from ev.cli.config import Config
from ev.cli.context import pass_context

if TYPE_CHECKING:
    from ev.cli.context import Context

console = Console()


@click.command()
@pass_context
def configure(ctx: Context) -> None:
    """Interactive configuration wizard for creating and managing profiles."""
    try:
        config_path, using_default_ev_home = Config.get_path()

        # 1. EV_HOME and config file status display
        if using_default_ev_home:
            console.print(
                f"The variable [bold]EV_HOME[/bold] is not set, using [bold]{config_path.parent}[/bold] as the default."
            )
        else:
            console.print(f"Using [bold]EV_HOME={config_path.parent}[/bold] from the environment.")

        if config_path.exists():
            console.print(f"Configuration file will be overwritten: [bold]{config_path}[/bold]")
        else:
            console.print(f"Configuration file will be created: [bold]{config_path}[/bold]")
        console.print()

        # 2. Prompt for profile name with validation
        profile_name = _prompt_profile_name(ctx.config)

        # 3. Prompt for endpoint URL with default
        endpoint_url = _prompt_endpoint_url()

        # 4. Ask about setting as default profile
        set_as_default = _prompt_default_profile(profile_name)

        # 5. Save configuration
        try:
            # Inform user about the configuration process
            console.print()
            console.print(f"[dim]Saving profile '{profile_name}'...[/dim]")

            # Create or update the profile with endpoint URL
            ctx.config.create_or_update_profile(profile_name, endpoint_url)
            console.print(f"[green]✓[/green]  Profile '{profile_name}' saved successfully")

            # Set as default profile if requested
            if set_as_default:
                console.print()
                console.print(f"[dim]Setting '{profile_name}' as default profile...[/dim]")
                ctx.config.set_default_profile(profile_name)
                console.print(f"[green]✓[/green]  Default profile updated to '{profile_name}'")

        except ValueError as e:
            raise click.ClickException(f"Configuration error: {e}") from e
        except PermissionError as e:
            raise click.ClickException(
                f"Permission denied writing to config file '{config_path}'. "
                f"Please check file permissions or run with appropriate privileges."
            ) from e
        except OSError as e:
            raise click.ClickException(
                f"Failed to write configuration file '{config_path}': {e}. "
                f"Please ensure the directory exists and is writable."
            ) from e
        except Exception as e:
            raise click.ClickException(
                f"Unexpected error saving configuration: {e}. Please check your configuration and try again."
            ) from e

        # 6. Display success message and usage guide
        _display_usage_guide(profile_name, set_as_default, str(config_path), endpoint_url)

    except click.ClickException:
        # Re-raise ClickExceptions to preserve error messages
        raise
    except click.Abort:
        console.print("\n[yellow]Configuration cancelled by user.[/yellow]")
        raise
    except Exception as e:
        raise click.ClickException(
            f"Unexpected error during configuration: {e}. Please try again or check your system configuration."
        ) from e


def _prompt_profile_name(config: Config) -> str:
    """Prompt user for profile name with validation.

    Args:
        config: Config instance to check for existing profiles

    Returns:
        The validated profile name
    """
    while True:
        profile_name = str(click.prompt("Enter profile name", type=str)).strip()

        # Validate that profile name is not empty
        if not profile_name:
            console.print("[red]Profile name cannot be empty. Please try again.[/red]")
            continue

        # Check if profile already exists and confirm overwrite
        if profile_name in config.profiles:
            overwrite = click.confirm(f"Profile '{profile_name}' already exists. Overwrite it?", default=False)
            if not overwrite:
                console.print("Please choose a different profile name.")
                continue

        return profile_name


def _prompt_endpoint_url() -> str:
    """Prompt user for endpoint URL with default value and validation.

    Returns:
        The validated endpoint URL
    """
    default_endpoint = "https://cloud.daft.ai"

    while True:
        # Prompt with default value shown in brackets
        endpoint_url = str(
            click.prompt("Enter endpoint URL", default=default_endpoint, show_default=True, type=str)
        ).strip()

        # Basic URL format validation - must start with http:// or https://
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)?$",  # optional path
            re.IGNORECASE,
        )

        if not url_pattern.match(endpoint_url):
            console.print("[red]Invalid URL format. Please enter a valid HTTP or HTTPS URL.[/red]")
            console.print("[dim]Example: https://cloud.daft.ai[/dim]")
            continue

        return endpoint_url


def _prompt_default_profile(profile_name: str) -> bool:
    """Prompt user to confirm setting the profile as default.

    Args:
        profile_name: The name of the profile to potentially set as default

    Returns:
        True if user wants to set as default, False otherwise
    """
    while True:
        response = click.prompt("Use this as the default profile? (y/n)", type=str).strip().lower()

        # Accept various yes/no responses (case insensitive)
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        else:
            console.print("[red]Please enter 'y' for yes or 'n' for no.[/red]")
            continue


def _display_usage_guide(profile_name: str, is_default: bool, config_path: str, endpoint_url: str) -> None:
    """Display usage guide with profile-specific instructions.

    Args:
        profile_name: The name of the configured profile
        is_default: Whether this profile is set as the default
        config_path: Path where the configuration file was saved
        endpoint_url: The endpoint URL configured for this profile
    """
    console.print("\n[bold]Usage Instructions:[/bold]")
    console.print()

    if is_default:
        console.print(f"Since '{profile_name}' is your default profile, you may omit the profile in commands:")
        console.print("  [bold bright_magenta]ev <command>[/bold bright_magenta]")
        console.print("\nOr explicitly specify the profile:")
        console.print(f"  [bold bright_magenta]ev --profile={profile_name} <command>[/bold bright_magenta]")
    else:
        console.print(f"To use the '{profile_name}' profile, specify it with the --profile flag:")
        console.print(f"  [bold bright_magenta]ev --profile={profile_name} <command>[/bold bright_magenta]")
        console.print(f"\nTo set '{profile_name}' as your default profile later, run:")
        console.print("  [bold bright_magenta]ev configure[/bold bright_magenta] and choose to set it as default")
