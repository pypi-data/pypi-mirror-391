from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
import toml
from rich.console import Console
from rich.panel import Panel

from ev.cli.commands.run import _parse_entrypoint, execute_run
from ev.cli.context import pass_context
from ev.cli.validation import prompt_with_validation
from ev.git_utils import get_commit_hash, get_git_root, get_remote_url
from ev.models import (
    AppSource,
    CreateAppRequest,
    CreateAppResponse,
    RunEnvironment,
    Trigger,
    UpdateAppRequest,
    UpdateAppResponse,
)
from ev.runtime_env.resolver import RuntimeEnvResolver

if TYPE_CHECKING:
    from ev.cli.context import Context

console = Console()


def prompt_for_trigger_type() -> str:
    """Prompt user to choose a trigger type.

    Returns:
        The selected trigger type ("cron", "event", or "endpoint")
    """
    console.print()
    console.print("[bold]What type of trigger would you like to set up?[/bold]")
    console.print(
        "For more information about triggers, see: [magenta][link]https://docs.daft.ai/apps/triggers[/link][/magenta]"
    )

    choices = [
        ("1", "Cron", "Schedule runs using a cron expression"),
        ("2", "Event", "Trigger runs based on events (coming soon)"),
        ("3", "Endpoint", "Trigger runs via HTTP endpoints (coming soon)"),
    ]

    for choice, title, description in choices:
        console.print(f"  {choice}. [bold]{title}[/bold] - {description}")

    console.print()

    while True:
        choice = click.prompt("Choose a trigger type", type=click.Choice(["1", "2", "3"]))
        if choice == "1":
            return "cron"
        elif choice == "2":
            console.print("[yellow]Event triggers are not yet supported. Please choose another option.[/yellow]")
            continue
        elif choice == "3":
            console.print("[yellow]Endpoint triggers are not yet supported. Please choose another option.[/yellow]")
            continue


def display_cron_format_hint() -> None:
    """Display a helpful hint about cron format."""
    cron_hint = """Cron Schedule Format:
* * * * *
┬ ┬ ┬ ┬ ┬
│ │ │ │ │
│ │ │ │ └──── Day of the week (0 - 7) (Sunday is both 0 and 7)
│ │ │ └────── Month (1 - 12)
│ │ └──────── Day of the month (1 - 31)
│ └────────── Hour (0 - 23)
└──────────── Minute (0 - 59)

Examples:
• 0 0 * * * - Every day at midnight
• 0 */6 * * * - Every 6 hours
• 0 9 * * 1 - Every Monday at 9 AM
• 30 14 * * 1-5 - Weekdays at 2:30 PM

For more details, refer to our documentation: [magenta][link]https://docs.daft.ai/apps/triggers/cron[/link][/magenta]"""

    console.print(Panel(cron_hint, title="Cron Schedule Help", border_style="blue"))


def prompt_for_cron_schedule() -> str:
    """Prompt user for a cron schedule with hints.

    Returns:
        The cron schedule string
    """
    console.print()
    display_cron_format_hint()
    console.print()
    # TODO(desmond): It would be great to validate the given cron schedule at this point. But this depends
    # on what cron service we end up using, so let's punt on validation.
    return str(click.prompt("Enter cron schedule", type=str).strip())


@click.group()
@pass_context
def app(ctx: Context) -> None:
    """Manage apps on Daft Cloud."""
    pass


@app.command()
@pass_context
def init(ctx: Context) -> None:
    """Initialize a new app in the current project."""
    try:
        # Get project ID from ev.toml file.
        git_root = get_git_root()
        ev_config_path = git_root / "ev.toml"
        if not ev_config_path.exists():
            raise click.ClickException("No ev.toml file found. Run 'ev init' first to initialize the project.")

        try:
            ev_config = toml.load(ev_config_path)
        except Exception as e:
            raise click.ClickException(f"Failed to read ev.toml from: {ev_config_path}") from e

        project_id = ev_config.get("project_id")
        if not project_id:
            raise click.ClickException(
                "No project_id found in ev.toml. Please run 'ev init' to initialize the project."
            )

        app_name = prompt_with_validation("\nApp name", max_length=96, name_type="App name")
        if "apps" not in ev_config:
            ev_config["apps"] = {}
        if app_name in ev_config["apps"]:
            raise click.ClickException(f"App '{app_name}' already exists in ev.toml")

        console.print("\n[bold]Entrypoint Configuration[/bold]")
        console.print("Specify how your app should be executed:")
        console.print("• Python file: script.py")
        console.print("• Module: my_module")
        console.print("• Function: my_module:my_function -- --arg1 value1 --arg2 value2...")

        entrypoint = click.prompt("\nEntrypoint", type=str)

        # Get git information (without hash) and environment info.
        git_remote = get_remote_url()
        env_resolver = RuntimeEnvResolver(cwd=Path.cwd(), git_root=git_root)
        python_version = env_resolver.resolve_python_version() or sys.version

        # Create app via API.
        workspace_id = ctx.workspace_id
        entrypoint_obj = _parse_entrypoint(entrypoint, [])
        app_source = AppSource.git(remote=git_remote) if git_remote else AppSource.directory(path=str(git_root))
        environment = RunEnvironment(python_version=python_version, dependencies=[], environment_variables={})
        create_app_request = CreateAppRequest(
            name=app_name,
            entrypoint=entrypoint_obj,
            source=app_source,
            environment=environment,
            triggers=[],  # No triggers initially - user can add them later
        )

        console.print(f"\n[bold]Creating app '{app_name}' on Daft Cloud...[/bold]")
        create_app_response: CreateAppResponse = ctx.client.create_app(workspace_id, project_id, create_app_request)
        app_id = create_app_response.app.id

        # Create app configuration for local storage.
        app_config = {
            "id": app_id,
            "entrypoint": entrypoint,
        }

        # Store git and environment information
        if git_remote:
            app_config["git_remote"] = git_remote
        app_config["python_version"] = python_version

        ev_config["apps"][app_name] = app_config

        # Write the updated config back to ev.toml.
        with ev_config_path.open("w", encoding="utf-8") as f:
            toml.dump(ev_config, f)

        console.print(f"\n[green]✓[/green] App '{app_name}' initialized successfully!")
        console.print(f"App ID: {app_id}")
        console.print(f"Entrypoint: {entrypoint}")
        if git_remote:
            console.print(f"Git remote: {git_remote}")
        console.print(f"Python version: {python_version}")
        console.print("App configuration added to ev.toml")
        console.print("\nNext steps:")
        console.print(f"  ev app add-trigger {app_name}         # Add a trigger to automate runs")
        console.print(f"  ev app run {app_name}                 # Run your app manually")
        console.print(f"  ev app update-environment {app_name}  # Update environment information")

    except Exception as e:
        raise click.ClickException(f"Error initializing app: {e}") from e


@app.command()
@click.argument("app_name", required=True)
@click.argument("argv", nargs=-1)
@pass_context
def run(ctx: Context, app_name: str, argv: list[str]) -> None:
    """Run an app with additional arguments."""
    try:
        git_root = get_git_root()
        ev_config_path = git_root / "ev.toml"
        if not ev_config_path.exists():
            raise click.ClickException("No ev.toml file found. Run 'ev init' first to initialize the project.")

        try:
            ev_config = toml.load(ev_config_path)
        except Exception as e:
            raise click.ClickException(f"Failed to read ev.toml from: {ev_config_path}") from e

        project_id = ev_config.get("project_id")
        if not project_id:
            raise click.ClickException(
                "No project_id found in ev.toml. Please run 'ev init' to initialize the project."
            )

        if "apps" not in ev_config or app_name not in ev_config["apps"]:
            raise click.ClickException(f"App '{app_name}' not found. Run 'ev app init' first to create the app.")

        app_config = ev_config["apps"][app_name]

        if "entrypoint" not in app_config:
            raise click.ClickException(
                f"App '{app_name}' has no entrypoint defined. "
                "Please add an entrypoint to the app configuration in ev.toml."
            )

        entrypoint_str = app_config["entrypoint"]
        # Combine any existing argv from config with new argv.
        existing_argv = app_config.get("argv", [])
        combined_argv = existing_argv + list(argv)

        # Get git information (like ev run).
        git_commit = get_commit_hash()
        # Use git remote from TOML if available, otherwise fetch it.
        git_remote = app_config.get("git_remote") or get_remote_url()

        # Resolve runtime environment (always from source files for single source of truth).
        env_resolver = RuntimeEnvResolver(cwd=Path.cwd(), git_root=git_root)
        python_version = env_resolver.resolve_python_version() or sys.version
        dependencies = env_resolver.resolve_dependencies()
        secret_environment_variables = env_resolver.resolve_environment_secrets()

        # Parse entrypoint string to separate module:function from arguments.
        if " -- " in entrypoint_str:
            entrypoint_part, entrypoint_args = entrypoint_str.split(" -- ", 1)
            # Parse the entrypoint arguments and add them to combined_argv.
            entrypoint_args_list = entrypoint_args.split() if entrypoint_args.strip() else []
            combined_argv = entrypoint_args_list + combined_argv
            entrypoint_str = entrypoint_part

        execute_run(
            ctx,
            entrypoint_str,
            combined_argv,
            git_remote,
            git_commit,
            python_version,
            dependencies,
            secret_environment_variables,
        )

    except subprocess.CalledProcessError as e:
        click.echo(f"Error getting git information: {e}")
        raise click.ClickException("Make sure you're in a git repository with committed changes")
    except Exception as e:
        click.echo(f"Error running app: {e}")
        raise click.ClickException("Failed to run app")


@app.command()
@click.argument("app_name", required=True)
@pass_context
def add_trigger(ctx: Context, app_name: str) -> None:
    """Add a trigger to an app."""
    try:
        git_root = get_git_root()
        ev_config_path = git_root / "ev.toml"
        if not ev_config_path.exists():
            raise click.ClickException("No ev.toml file found. Run 'ev init' first to initialize the project.")

        try:
            ev_config = toml.load(ev_config_path)
        except Exception as e:
            raise click.ClickException(f"Failed to read ev.toml from: {ev_config_path}") from e

        if "apps" not in ev_config:
            raise click.ClickException("No apps found in ev.toml. Run 'ev app init' first.")

        if app_name not in ev_config["apps"]:
            raise click.ClickException(f"App '{app_name}' not found. Run 'ev app init' first to create the app.")

        app_config = ev_config["apps"][app_name]

        trigger_type = prompt_for_trigger_type()

        if trigger_type == "cron":
            schedule = prompt_for_cron_schedule()
            if "triggers" not in app_config:
                app_config["triggers"] = []
            app_config["triggers"].append({"cron": schedule})
            console.print(f"[green]✓[/green] Added cron trigger: [bold]{schedule}[/bold]")

        ev_config["apps"][app_name] = app_config
        with ev_config_path.open("w", encoding="utf-8") as f:
            toml.dump(ev_config, f)

        console.print(f"\n[green]✓[/green] Trigger added to app '{app_name}' successfully!")
        console.print("App configuration updated in ev.toml")
        console.print("\nNext steps:")
        console.print("  Commit and push your changes to register the trigger")
        console.print(f"  ev app run {app_name}  # Run your app manually")

    except Exception as e:
        raise click.ClickException(f"Error adding trigger: {e}") from e


@app.command()
@click.argument("app_name", required=True)
@pass_context
def update_environment(ctx: Context, app_name: str) -> None:
    """Update environment information for an app."""
    try:
        git_root = get_git_root()
        ev_config_path = git_root / "ev.toml"
        if not ev_config_path.exists():
            raise click.ClickException("No ev.toml file found. Run 'ev init' first to initialize the project.")

        try:
            ev_config = toml.load(ev_config_path)
        except Exception as e:
            raise click.ClickException(f"Failed to read ev.toml from: {ev_config_path}") from e

        if "apps" not in ev_config:
            raise click.ClickException("No apps found in ev.toml. Run 'ev app init' first.")

        if app_name not in ev_config["apps"]:
            raise click.ClickException(f"App '{app_name}' not found. Run 'ev app init' first to create the app.")

        app_config = ev_config["apps"][app_name]

        env_resolver = RuntimeEnvResolver(cwd=Path.cwd(), git_root=git_root)
        python_version = env_resolver.resolve_python_version() or sys.version
        dependencies = env_resolver.resolve_dependencies()

        app_config["python_version"] = python_version
        # Note: Dependencies are always resolved from source files and not stored in ev.toml
        # Remove any existing stored dependencies to maintain single source of truth
        if "dependencies" in app_config:
            del app_config["dependencies"]

        ev_config["apps"][app_name] = app_config

        with ev_config_path.open("w", encoding="utf-8") as f:
            toml.dump(ev_config, f)

        console.print(f"\n[green]✓[/green] Environment information updated for app '{app_name}'!")
        console.print(f"Python version: {python_version}")
        if dependencies:
            console.print(f"Dependencies: {len(dependencies)} resolved from source files")
        else:
            console.print("Dependencies: None found in source files")
        console.print("App configuration updated in ev.toml")

    except Exception as e:
        raise click.ClickException(f"Error updating environment: {e}") from e


@app.command()
@click.argument("app_name", required=True)
@pass_context
def deploy(ctx: Context, app_name: str) -> None:
    """⚠️ For development ⚠️ Deploy an app to Daft Cloud."""
    try:
        # Get project ID from ev.toml file.
        git_root = get_git_root()
        workspace_id = ctx.workspace_id
        ev_config_path = git_root / "ev.toml"
        if not ev_config_path.exists():
            raise click.ClickException("No ev.toml file found. Run 'ev init' first to initialize the project.")

        try:
            ev_config = toml.load(ev_config_path)
        except Exception as e:
            raise click.ClickException(f"Failed to read ev.toml from: {ev_config_path}") from e

        if "apps" not in ev_config or app_name not in ev_config["apps"]:
            raise click.ClickException(f"App '{app_name}' not found. Run 'ev app init' first to create the app.")

        app_config = ev_config["apps"][app_name]

        if "id" not in app_config:
            raise click.ClickException(f"App '{app_name}' is missing ID. Please reinitialize the app.")
        app_id = app_config["id"]

        if "project_id" not in ev_config:
            raise click.ClickException("No project_id found in ev.toml. Run 'ev init' first.")
        project_id = ev_config["project_id"]

        if "entrypoint" not in app_config:
            raise click.ClickException(f"App '{app_name}' is missing entrypoint configuration.")
        entrypoint_obj = _parse_entrypoint(app_config["entrypoint"], [])

        git_remote = app_config.get("git_remote")
        if git_remote:
            app_source = AppSource({"git": {"remote": git_remote}})
        else:
            app_source = AppSource({"directory": {"path": str(git_root)}})

        # Always resolve dependencies from source files for single source of truth
        env_resolver = RuntimeEnvResolver(cwd=Path.cwd(), git_root=git_root)
        python_version = app_config.get("python_version", sys.version)
        dependencies = env_resolver.resolve_dependencies()
        environment_variables = app_config.get("environment_variables", {})

        environment = RunEnvironment(
            python_version=python_version, dependencies=dependencies, environment_variables=environment_variables
        )

        triggers: list[Trigger] = []
        if "triggers" in app_config:
            triggers.extend(Trigger.create_cron(tc["cron"]) for tc in app_config["triggers"] if "cron" in tc)

        update_request = UpdateAppRequest(
            name=app_name,
            entrypoint=entrypoint_obj,
            source=app_source,
            environment=environment,
            triggers=triggers,
        )

        console.print(f"\n[bold]Deploying app '{app_name}' to Daft Cloud...[/bold]")
        update_response: UpdateAppResponse = ctx.client.update_app(workspace_id, project_id, app_id, update_request)

        console.print(f"[green]✓[/green] App '{app_name}' deployed successfully!")
        console.print(f"App ID: {update_response.app.id}")

        if triggers:
            console.print(f"Triggers: {len(triggers)} configured")
        else:
            console.print("Triggers: None configured")

    except Exception as e:
        raise click.ClickException(f"Error deploying app: {e}") from e
