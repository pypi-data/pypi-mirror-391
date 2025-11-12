from __future__ import annotations

import ast
import asyncio
import importlib
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click
import httpx
import requests
from requests import HTTPError
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from websocket import WebSocketException, create_connection

from ev.cli.context import pass_context
from ev.git_utils import get_commit_hash, get_git_root, get_remote_url, is_commit_on_remote, is_dirty
from ev.models import (
    CreateRunRequest,
    CreateRunResponse,
    Run,
    RunEntrypoint,
    RunEnvironment,
    RunSource,
    RunStatus,
)
from ev.runtime_env.resolver import RuntimeEnvResolver

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec

    from ev.cli.context import Context
    from ev.client import Client

console = Console()


def execute_run(
    ctx: Context,
    entrypoint: str,
    argv: list[str],
    git_remote: str,
    git_commit: str,
    python_version: str,
    dependencies: list[str],
    secret_environment_variables: dict[str, str],
) -> None:
    wid = ctx.workspace_id
    pid = ctx.project_id

    # Create run request
    run_request = CreateRunRequest(
        entrypoint=_parse_entrypoint(entrypoint, argv),
        source=RunSource.git(remote=git_remote, hash=git_commit),
        environment=RunEnvironment(python_version=python_version, dependencies=dependencies, environment_variables={}),
        secrets=secret_environment_variables,
    )

    res: CreateRunResponse
    try:
        res = ctx.client.create_run(wid, pid, run_request)

        console.print("\n")
        display_run_url(res.run, ctx.config.dashboard_url)
        display_run(res.run)
        console.print("\n")

        # TODO(rchowell): internalize in the client
        console.print("[bold]Run logs[/bold] [dim](ctrl+c to exit)[/dim]")
        console.print("\n")
    except (requests.HTTPError, httpx.HTTPStatusError) as e:
        raise click.ClickException("Failed to submit run") from e

    try:
        # Run log tailing and status polling concurrently
        final_status = asyncio.run(_run_with_monitoring(ctx, res.run.id))

        # After run completes, check if we should fetch and display results
        if final_status == RunStatus.SUCCEEDED:
            result = _fetch_run_result_with_retry(ctx, wid, pid, res.run.id)
            if result is None or len(result) == 0:
                click.echo(f"Run {res.run.id} has no result")
            else:
                try:
                    click.echo(f"\nResult for run {res.run.id}:")
                    click.echo(json.dumps(result, indent=2))
                except json.JSONDecodeError as e:
                    click.echo(f"Run {res.run.id} result is not valid JSON: {e}")
        else:
            click.echo(click.style(f"Run {res.run.id} failed! Please check the logs.", fg="red", bold=True))
            sys.exit(1)
    except (requests.HTTPError, httpx.HTTPStatusError) as e:
        raise click.ClickException("Failed to fetch logs and results") from e


@click.command()
@click.argument("entrypoint", required=True)
@click.argument("argv", nargs=-1)
@click.option("--env-file", type=click.Path(exists=True, path_type=Path), help="Path to environment file")
@pass_context
def run(ctx: Context, entrypoint: str, argv: list[str], env_file: Path | None) -> None:
    """Submit a run to Daft Cloud."""
    try:
        # Get git information
        git_root = get_git_root()
        # Should not the remote come from the project?
        git_commit = get_commit_hash()
        git_remote = get_remote_url()  # TODO(rchowell): normalize to HTTPS

        if is_dirty(git_root):
            console.print()
            console.print("[bold red]⚠️  Git repository has uncommitted changes  ⚠️[/bold red]")
            console.print()
            console.print(
                f"[yellow]You're about to submit a run for commit [bright_magenta]{git_commit[:8]}[/bright_magenta]"
                "that will [bold]NOT[/bold] include local changes.[/yellow]\n"
            )

            panel = Panel(
                'git add .\ngit commit -m "your message"\ngit push',
                title="[bold]To commit your changes, run:[/bold]",
                title_align="left",
                border_style="dim",
                padding=(1, 2),
                expand=False,
            )
            console.print(panel)
            console.print()

            if not sys.stdin.isatty() or click.confirm("Do you want to continue WITHOUT local changes?", default=False):
                console.print("[yellow]Ignoring local changes for run.[/yellow]")
            else:
                return

        # Check if the commit exists on the remote
        if not is_commit_on_remote(git_root, git_remote, git_commit):
            console.print(f"[bold red]❌ Commit {git_commit[:8]} does not exist on remote[/bold red]")
            console.print(f"[dim]{git_remote}[/dim]")
            console.print("[dim]Cannot submit run until you've pushed your local commits to the remote![/dim]\n")

            panel = Panel(
                "[yellow]git push[/yellow]",
                title="[bold]To push your commits, run:[/bold]",
                title_align="left",
                border_style="red",
                padding=(1, 2),
                expand=False,
            )
            console.print(panel)
            raise click.ClickException("Must push local commits to git remote before submitting a run!")

        # Should we default to the `sys.version`?
        # This ensures compatibility with the user's environment as we're grabbing
        # their version.
        env_resolver = RuntimeEnvResolver(cwd=Path.cwd(), git_root=git_root, env_file=env_file)
        python_version = env_resolver.resolve_python_version() or sys.version
        dependencies = env_resolver.resolve_dependencies()
        secret_environment_variables = env_resolver.resolve_environment_secrets()

        execute_run(
            ctx,
            entrypoint,
            argv,
            git_remote,
            git_commit,
            python_version,
            dependencies,
            secret_environment_variables,
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Error getting git information: {e}")
        raise click.ClickException("Make sure you're in a git repository with committed changes")


class ProgressBarLogger:
    """
    Manages display of logs with progress bars in the terminal.
    Intercepts any log messages that are Daft progress bars and displays them in a progress bar format.
    """

    def __init__(self) -> None:
        self.active_progress_bars: dict[str, str] = {}
        self.has_progress_bars = False

    def _is_progress_bar(self, message: str) -> bool:
        """Detect if a message is a progress bar indicator."""
        # This is a little bit hack, but it works pretty consistently for now.
        # If we invest more into this route, we can have the source pipe the progress bars
        # into a different aggregator.
        return "(pid=" in message and "->" in message

    def _extract_progress_index(self, message: str) -> str | None:
        """Extract the progress bar index
        Example: "(pid=1073) GlobScan->Project->IntoBatches 0: 100%|██████████| 1.00/1.00 [00:28<00:00, 25.0s/it]"
        Returns: "GlobScan->Project->IntoBatches 0"
        """
        match = re.search(r"\(pid=\d+\)\s+(.+?):\s+\d+%", message)
        if match:
            return match.group(1).strip()
        return None

    def _clear(self) -> None:
        """Clear all currently displayed progress bars."""
        if not self.has_progress_bars:
            return

        num_lines = len(self.active_progress_bars) + 2  # +1 for blank line, +1 for header

        # Move cursor up and clear all progress bar lines
        for _ in range(num_lines):
            sys.stdout.write("\033[F")  # Move cursor up to previous line

        sys.stdout.write("\033[J")  # Clear from cursor to end of screen
        sys.stdout.flush()
        self.has_progress_bars = False

    def _display(self) -> None:
        """Display all active progress bars."""
        if not self.active_progress_bars:
            return

        # Add blank line and header before progress bars
        sys.stdout.write("\n")
        header = click.style("[Daft Operations]", fg="magenta", bold=True)
        sys.stdout.write(header + "\n")

        # Display each progress bar
        for progress_msg in self.active_progress_bars.values():
            # Extract everything after (pid=xxx)
            match = re.search(r"\(pid=\d+\)\s+(.+)$", progress_msg)
            if match:
                clean_msg = match.group(1)
                styled_msg = click.style("▸", fg="bright_black") + " " + clean_msg
                sys.stdout.write(styled_msg + "\n")
            else:
                sys.stdout.write(progress_msg + "\n")

        sys.stdout.flush()
        self.has_progress_bars = True

    def log_message(self, payload: dict[str, str]) -> None:
        """Process and display a log message or progress bar."""
        timestamp_raw = payload.get("timestamp")
        message = payload.get("message")
        if not timestamp_raw or not message:
            return

        # Parse timestamp
        timestamp_raw = timestamp_raw.rstrip("Z")
        dt = datetime.strptime(timestamp_raw[:26], "%Y-%m-%dT%H:%M:%S.%f")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone()
        formatted_dt = dt_local.strftime("%Y-%m-%d %H:%M:%S")

        clean_message = message.replace("\u001b[A", "").replace("\r", "").replace("\n", "").strip()

        if not clean_message:
            return

        # Handle progress bar
        if self._is_progress_bar(clean_message):
            index = self._extract_progress_index(clean_message)
            if index:
                self._clear()
                self.active_progress_bars[index] = clean_message
                self._display()
            return

        # Handle regular log
        if self.has_progress_bars:
            self._clear()

        click.echo(f"{click.style(f'[{formatted_dt}]', fg='bright_black')} {clean_message}")

        if self.active_progress_bars:
            self._display()


async def _tail_logs(ctx: Context, run_id: str, stop_event: asyncio.Event) -> None:
    """Tail logs from SSE stream until stop_event is set.

    TODO: Move this async streaming logic into the Client class once it supports async methods.
    """
    log_url = ctx.client.get_run_logs_tail_url(ctx.workspace_id, ctx.project_id, run_id)
    progress_logger = ProgressBarLogger()

    # Get auth headers from client for httpx, we'll make the client use httpx later
    auth_headers = ctx.client.get_auth_headers()
    stream_headers = {**auth_headers, "Accept": "text/event-stream"}

    try:
        # SSE streams need no timeout since they're long-lived connections
        async with (
            httpx.AsyncClient(timeout=None) as client,
            client.stream("GET", log_url, headers=stream_headers) as response,
        ):
            response.raise_for_status()

            # Stream logs until stop_event is set
            async for line in response.aiter_lines():
                if stop_event.is_set():
                    break

                # Skip empty lines and SSE comments
                if not line or line.startswith(":"):
                    continue

                # Parse SSE data lines
                if line.startswith("data: "):
                    data = line.removeprefix("data: ")
                    try:
                        payload = json.loads(data)
                        progress_logger.log_message(payload)
                    except json.JSONDecodeError:
                        # Skip malformed log entries
                        pass

    except Exception as e:
        click.echo(f"Error tailing logs: {e}")


async def _poll_status(ctx: Context, run_id: str, stop_event: asyncio.Event) -> RunStatus:
    """Poll run status until it's complete, wait for log drain period, then set stop_event.

    TODO: Move this async polling logic into the Client class once it supports async methods.
    """
    # Get auth headers from client for httpx
    auth_headers = ctx.client.get_auth_headers()

    async with httpx.AsyncClient(headers=auth_headers) as http_client:
        while True:
            # Make async HTTP GET request to get run status
            status = await _get_run_status(
                ev_client=ctx.client,
                http_client=http_client,
                workspace_id=ctx.workspace_id,
                project_id=ctx.project_id,
                run_id=run_id,
            )

            if status.is_complete():
                await asyncio.sleep(10.0)  # 10 second log drain period to catch remaining logs
                stop_event.set()
                return status
            await asyncio.sleep(5.0)


async def _get_run_status(
    ev_client: Client,
    http_client: httpx.AsyncClient,
    workspace_id: str,
    project_id: str,
    run_id: str,
) -> RunStatus:
    """Async implementation of ev.client.Client.get_run_status(). For use in async status polling task.

    TODO: This duplicates Client.get_run_status() logic. Move to Client class once it supports async.
    """
    run_url = ev_client.get_run_url(workspace_id, project_id, run_id)
    response = await http_client.get(run_url)
    response.raise_for_status()
    run = Run.model_validate(response.json())
    return run.status


async def _run_with_monitoring(ctx: Context, run_id: str) -> RunStatus:
    """Run log tailing and status polling concurrently."""
    stop_event = asyncio.Event()

    # Create tasks
    log_task = asyncio.create_task(_tail_logs(ctx, run_id, stop_event))
    status_task = asyncio.create_task(_poll_status(ctx, run_id, stop_event))

    # Wait for status polling to complete (which will set stop_event)
    final_status: RunStatus = await status_task

    # Wait for log tailing to stop (should stop quickly after stop_event is set)
    try:
        await asyncio.wait_for(log_task, timeout=5.0)
    except asyncio.TimeoutError:
        # If log task doesn't stop in time, cancel it
        log_task.cancel()
        try:
            await log_task
        except asyncio.CancelledError:
            pass

    return final_status


def _fetch_run_result_with_retry(
    ctx: Context,
    workspace_id: str,
    project_id: str,
    run_id: str,
    max_retries: int = 3,
) -> Any | None:
    """Fetch run result with exponential backoff retry logic.

    Retries up to max_retries times with exponential backoff starting at 1 second.
    This handles the race condition where results may not be immediately available
    after run completion.
    """
    delay = 1.0
    for attempt in range(max_retries):
        try:
            result = ctx.client.get_run_result(workspace_id, project_id, run_id)
            if result is not None:
                return result
        except HTTPError as e:
            # Ignores a 404 because right now 404 means empty results and isn't an error
            if getattr(e.response, "status_code", None) == 404:
                pass
            else:
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, this is a proper error and should be raised
                raise click.ClickException(f"Failed to fetch result after {max_retries} attempts: {e}") from e
        # Sleep before next retry (exponential backoff)
        if attempt < max_retries - 1:
            time.sleep(delay)
            delay *= 2

    return None


def _get_function_names_from_file(filepath: Path) -> set[str]:
    """Parse a Python file and extract all top-level function names without executing it."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))

        names = set()
        for item in tree.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                names.add(item.name)

        return names
    except SyntaxError as e:
        raise click.ClickException(f"Syntax error in Python file '{filepath}': {e}") from e
    except Exception as e:
        raise click.ClickException(f"Failed to parse Python file '{filepath}': {e}") from e


def _format_available_symbols(names: set[str] | list[str], limit: int = 10) -> str:
    """Format a list of symbols for display in error messages."""
    if not names:
        return "(none found)"

    sorted_names = sorted(names)
    displayed = sorted_names[:limit]
    result = ", ".join(displayed)

    if len(sorted_names) > limit:
        result += f" ... and {len(sorted_names) - limit} more"

    return result


def _validate_symbol_in_names(symbol: str, available_names: set[str], context: str) -> None:
    """Validate that a symbol exists in a set of available names."""
    if symbol not in available_names:
        available_str = _format_available_symbols(available_names)
        raise click.ClickException(f"Symbol '{symbol}' not found in {context}.\n" f"Available symbols: {available_str}")


def _get_and_validate_file_path(file_path_str: str) -> Path:
    """Get and validate a Python file path. Raises a click.ClickException if the file is not found."""
    file_path = Path(file_path_str)
    if not file_path.is_absolute():
        try:
            git_root = get_git_root()
            file_path = git_root / file_path
            if not file_path.exists():
                raise click.ClickException(
                    f"Python file '{file_path_str}' not found in git repository.\n"
                    f"Searched in project root: {git_root}"
                )
        except subprocess.CalledProcessError:
            # Not in a git repo, this would have been caught earlier by the run command.
            raise click.ClickException("Not in a git repository.")
    else:
        if not file_path.exists():
            raise click.ClickException(f"Python file '{file_path_str}' not found.")
    return file_path


def _validate_file_and_symbol(file_path_str: str, symbol: str) -> None:
    """Validate that a Python file exists and contains the specified symbol."""
    file_path = _get_and_validate_file_path(file_path_str)
    available_names = _get_function_names_from_file(file_path)
    _validate_symbol_in_names(symbol, available_names, f"file '{file_path_str}'")


def _get_and_validate_module_spec(module_name: str) -> ModuleSpec:
    """Get and validate a module spec. Raises a click.ClickException if the module is not found."""

    def raise_module_not_found_error() -> None:
        raise click.ClickException(
            f"Cannot find module '{module_name}'.\n"
            f"If this is a local file, use the file path: ev run <file.py>:{module_name}\n"
            f"Otherwise, ensure the module is installed or in your PYTHONPATH."
        )

    spec = None
    try:
        spec = importlib.util.find_spec(module_name)
    except (ModuleNotFoundError, ImportError, ValueError):
        raise_module_not_found_error()

    if spec is None:
        raise_module_not_found_error()

    assert spec is not None  # For mypy: spec is guaranteed to be non-None here
    return spec


def _validate_module_and_symbol(module_name: str, symbol: str) -> None:
    """Validate that a module exists and contains the specified symbol."""
    spec = _get_and_validate_module_spec(module_name)

    # If it's a file-based module, use AST parsing to check for the symbol.
    if spec.origin and spec.origin.endswith(".py"):
        filepath = Path(spec.origin)
        available_names = _get_function_names_from_file(filepath)
        _validate_symbol_in_names(symbol, available_names, f"module '{module_name}'")
    else:
        # For compiled modules or packages, we need to import
        # This is generally safe for installed packages
        try:
            module = importlib.import_module(module_name)
            if not hasattr(module, symbol):
                available = [name for name in dir(module) if not name.startswith("_")]
                available_str = _format_available_symbols(available)
                raise click.ClickException(
                    f"Symbol '{symbol}' not found in module '{module_name}'.\n" f"Available symbols: {available_str}"
                )
        except (ImportError, ModuleNotFoundError) as e:
            raise click.ClickException(
                f"Cannot import module '{module_name}': {e}\n" f"Make sure all dependencies are installed."
            ) from e


def _parse_entrypoint(entrypoint: str, argv: list[str]) -> RunEntrypoint:
    """Parse entrypoint string into RunEntrypoint model."""
    # Check if it's a module:function format
    if ":" in entrypoint:
        module_or_file, symbol = entrypoint.split(":", 1)

        # Check if it's actually a file path (ends with .py)
        if module_or_file.endswith(".py"):
            # It's a file path, validate it and the symbol
            _validate_file_and_symbol(module_or_file, symbol)
            module_name = module_or_file
        else:
            # It's a module, validate it and the symbol
            _validate_module_and_symbol(module_or_file, symbol)
            module_name = module_or_file

        args: list[str] = []
        kwargs: dict[str, Any] = {}
        # TODO(EVE-941): proper argument parsing
        #       If "symbol" is a function, then we need to check what argument types
        #       it has and convert these strings into them. This way, we can JSON serialzie
        #       them correctly when we make the submit run request.
        #
        #       NOTE: For module & script, we pass the CLI arg string array directly.
        for arg in argv:
            if arg.startswith("--"):
                if "=" not in arg:
                    raise click.BadParameter(f"Keyword argument must be in format '--key=value', got: {arg}")
                key, value = arg[2:].split("=", 1)
                kwargs[key] = value
            else:
                args.append(arg)

        return RunEntrypoint.function(
            module=module_name,
            symbol=symbol,
            args=args,
            kwargs=kwargs,
        )

    # Check if it's a Python file
    if entrypoint.endswith(".py"):
        _get_and_validate_file_path(entrypoint)
        return RunEntrypoint.file(file_path=entrypoint, argv=list(argv))

    # Assume it's a module
    _get_and_validate_module_spec(entrypoint)
    return RunEntrypoint.module(module=entrypoint, argv=list(argv))


def display_run(run: Run) -> None:
    """Display a run in a formatted table."""
    console.print("[bold]Run details[/bold]")

    table = Table(box=box.SIMPLE, show_header=True, header_style="dim")
    table.add_column("ENTRYPOINT")
    table.add_column("ID")
    table.add_column("COMMIT")

    # Create the entrypoint string
    if func := run.entrypoint.get_function():
        entrypoint = f"{func.module}:{func.symbol}"
    elif file := run.entrypoint.get_file():
        entrypoint = file.file_path
    elif module := run.entrypoint.get_module():
        entrypoint = module.module
    else:
        entrypoint = "unknown"

    # Extract commit hash (first 8 characters)
    git_source = run.source.get_git()
    commit_hash = git_source.hash[:8] if git_source else "local"

    table.add_row(entrypoint, run.id, commit_hash)
    console.print(Padding(table, (0, 0, 0, 1)))


def display_run_url(run: Run, dashboard_url: str) -> None:
    """Display the run URL in a formatted table."""
    console.print("[bold]Run link[/bold]")

    url = f"{dashboard_url}/runs/{run.id}"
    table = Table(box=box.SIMPLE, show_header=True, header_style="dim")
    table.add_column("URL")
    table.add_row(f"[link={url}]{url}[/link]")
    console.print(Padding(table, (0, 0, 0, 1)))
    console.print()


def display_log(data: str) -> None:
    try:
        log = json.loads(data)
        console.print(f"{log['timestamp']}\t{log['message']}")
    except Exception:
        console.print(data)


def _tail_realtime_stats(ctx: Context, workspace_id: str, project_id: str, run_id: str) -> None:
    """Open a websocket to the run's realtime stats endpoint and print updates.

    This is currently a WIP and only prints debug data for now.

    TODO(oliver): implement progress bars with the realtime stats.
    """

    url = ctx.client.get_realtime_stats_url(workspace_id, project_id, run_id)
    headers = []
    auth_header = ctx.client.get_auth_headers().get("Authorization")
    if auth_header:
        headers.append(f"Authorization: {auth_header}")

    try:
        ws = create_connection(url, header=headers)
    except WebSocketException as exc:
        raise RuntimeError(f"Failed to connect to realtime stats websocket: {exc}") from exc

    try:
        while True:
            try:
                message = ws.recv()
            except WebSocketException as exc:
                raise RuntimeError(f"Realtime stats websocket error: {exc}") from exc

            if message is None:
                break

            try:
                parsed = json.loads(message)
                # TODO(oliver): do something with this data
                console.print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                console.print(message)
    except KeyboardInterrupt:
        console.print("\nStopping realtime stats tail...")
    finally:
        try:
            ws.close()
        except WebSocketException:
            pass
