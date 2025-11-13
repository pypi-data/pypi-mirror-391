"""Login command for CLI authentication via WorkOS."""

from __future__ import annotations

import time
import webbrowser

import click
import requests
from rich.console import Console

from ev.cli.context import Context, pass_context
from ev.cli.credentials import (
    AuthorizationError,
    Credentials,
    Token,
    device_authorize,
    device_token,
)

console = Console()


@click.command()
@pass_context
def login(ctx: Context) -> None:
    """Login to Daft Cloud using a browser."""
    profile = ctx.config.profile

    try:
        console.print(f"Logging in with profile [bold]'{profile}[/bold]'...")
        console.print()

        # Initialize the device auth flow via control plane
        endpoint_url = ctx.config.endpoint_url
        authz_res = device_authorize(endpoint_url)

        user_code = authz_res.user_code
        device_code = authz_res.device_code
        verification_uri_complete = authz_res.verification_uri_complete
        verification_uri = authz_res.verification_uri
        interval = authz_res.interval

        # Display instructions to user
        console.print("[bold]To authenticate:[/bold]")
        console.print(f"  1. Confirm the code: [bold bright_magenta]{user_code}[/bold bright_magenta]")
        console.print(
            f"  2. If the browser doesn't open, visit: [link={verification_uri_complete}]{verification_uri}[/link]"
        )
        console.print()

        # Automatically open browser
        try:
            webbrowser.open(verification_uri_complete)
        except Exception:
            console.print("[yellow]Unable to open browser automatically. Please open the URL manually.[/yellow]")

        console.print("[dim]Waiting for authentication...[/dim]")

        # Poll for the access token
        token = poll(endpoint_url, device_code, interval)

        # Save credentials
        Credentials.save(profile, token)

        console.print()
        console.print(f"[green]✓[/green]  Successfully authenticated profile '{profile}'")

    except AuthorizationError as e:
        raise click.ClickException(f"Authorization failed: {e}") from e
    except Exception as e:
        raise click.ClickException("Failed to login.") from e


def poll(endpoint_url: str, device_code: str, interval: int = 5) -> Token:
    """Poll for access token until user authorizes or flow expires.

    Args:
        endpoint_url: API endpoint URL
        device_code: Device code from device_authorize
        interval: Initial polling interval in seconds

    Returns:
        Token with workspace_id, access_token, refresh_token, and expires_in

    Raises:
        AuthorizationError: If user denies or token expires
        requests.HTTPError: If request fails
    """
    total_time_s = 0
    sleep_time_s = interval

    while total_time_s < 900:
        time.sleep(sleep_time_s)
        try:
            # Try to exchange device code for token
            return device_token(endpoint_url, device_code)
        except requests.HTTPError as e:
            # Parse error response from the API
            if e.response is not None and e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_code = error_data.get("error", "")

                    if error_code == "authorization_pending":
                        total_time_s += sleep_time_s
                        continue
                    elif error_code == "slow_down":
                        total_time_s += sleep_time_s
                        sleep_time_s += 5
                        continue
                    elif error_code == "access_denied":
                        raise AuthorizationError("User denied authorization")
                    elif error_code == "expired_token":
                        raise AuthorizationError("Device code expired")
                    else:
                        raise AuthorizationError(
                            f"Authorization failed: {error_data.get('error_description', error_code)}"
                        )
                except (ValueError, KeyError):
                    # If we can't parse the error, re-raise the original exception
                    raise

            # For other HTTP errors, re-raise
            raise

    raise AuthorizationError("Polling timeout: no response received within 900 seconds")
