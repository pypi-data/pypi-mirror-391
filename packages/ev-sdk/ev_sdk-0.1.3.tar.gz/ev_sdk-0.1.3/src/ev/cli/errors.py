"""Custom error handling for the Eventual CLI."""

from __future__ import annotations

from typing import Any

import click
import httpx
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()


class ErrorsGroup(click.Group):
    """Custom Click Group with enhanced error handling for HTTP errors."""

    def main(self, *args: Any, **kwargs: Any) -> Any:
        """Override main to add custom error handling for HTTP errors.

        We call super().main() with standalone_mode=False to force Click
        to propagate exceptions instead of handling them internally. This
        allows us to intercept and format them before display.
        """
        try:
            # Force non-standalone mode so exceptions propagate to our handler
            return super().main(*args, standalone_mode=False, **kwargs)  # type: ignore
        except click.Abort:
            # User pressed Ctrl+C - exit gracefully without showing stack trace
            raise SystemExit(1)
        except click.ClickException as e:
            # Check if this exception was caused by an HTTP error
            cause = e.__cause__

            if isinstance(cause, (requests.HTTPError | httpx.HTTPStatusError)):
                # Extract status code from either requests or httpx error
                status_code = None
                if (isinstance(cause, requests.HTTPError) and cause.response is not None) or isinstance(
                    cause, httpx.HTTPStatusError
                ):
                    status_code = cause.response.status_code

                # Display the command's error message first
                click.secho(f"Error: {e.format_message()}", fg="red", err=True)
                console.print()

                # Then pretty-print the cause based on status code
                if status_code == 401:
                    _display_auth_error()
                else:
                    _display_http_error(status_code)

                raise SystemExit(1)
            else:
                # No HTTP cause - show normally (Click's default behavior)
                e.show()
                raise SystemExit(1)


def _display_auth_error() -> None:
    """Display authentication error with login instructions."""
    # Get profile name from context
    ctx = click.get_current_context(silent=True)
    profile_name = "default"
    if ctx and ctx.obj and hasattr(ctx.obj, "config"):
        profile_name = ctx.obj.config.profile

    # Build login command suggestion
    login_cmd = "ev login" if profile_name == "default" else f"ev login --profile {profile_name}"

    # Display authentication error panel
    console.print(f"[red]Profile '[bold]{profile_name}[/bold]' is not authenticated or the session has expired.[/red]")
    console.print()
    panel = Panel(
        f"{login_cmd}",
        title="[bold]Please login[/bold]",
        border_style="dim",
        padding=(1, 2),
        expand=False,
    )
    console.print(panel)
    console.print()


def _display_http_error(status_code: int | None) -> None:
    """Display generic HTTP error information."""
    console.print(f"[yellow]HTTP {status_code} error occurred[/yellow]")
    if status_code == 403:
        console.print("[dim]You don't have permission to access this resource.[/dim]")
    elif status_code == 404:
        console.print("[dim]The requested resource was not found.[/dim]")
    elif status_code and status_code >= 500:
        console.print("[dim]Server error occurred. Please try again later.[/dim]")
    console.print()
