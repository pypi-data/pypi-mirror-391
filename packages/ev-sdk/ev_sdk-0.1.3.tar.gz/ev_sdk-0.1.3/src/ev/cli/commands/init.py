from __future__ import annotations

from typing import TYPE_CHECKING

import click
import httpx
import requests
from rich import box
from rich.console import Console
from rich.table import Table

from ev.cli.context import pass_context
from ev.cli.validation import prompt_with_validation
from ev.git_utils import get_current_branch, get_git_repo_name, get_git_root, get_remote_url, has_remote, is_git_repo
from ev.models import CreateProjectRequest, ProjectSource, ProjectSourceGithub

__all__: tuple[str, ...] = ("init",)

console = Console()

if TYPE_CHECKING:
    from ev.cli.context import Context


@click.command()
@pass_context
def init(ctx: Context, template: str | None = None) -> None:
    """Initialize an Eventual project in the current git repository."""
    if not is_git_repo():
        click.echo("Error: Eventual requires a git repository with a GitHub remote.")
        click.echo("Set up your repository with:")
        click.echo("  git init")
        click.echo("  git remote add origin <github-url>")
        return

    if template:
        raise click.ClickException("Initializing from template not yet supported.")
    else:
        click.echo("Initializing project from existing git repository.")

    # TODO(rchowell): create proper project configuration
    ev_toml_path = get_git_root() / "ev.toml"

    if ev_toml_path.exists():
        click.echo("Error: project already initialized.")
        return

    if not has_remote("origin"):
        click.echo("Error: Projects require a GitHub remote for your repository.")
        click.echo("Add a remote with: git remote add origin <github-url>")
        return

    try:
        git_remote = get_remote_url()
        git_branch = get_current_branch()
    except Exception as e:
        raise click.ClickException(f"Error getting git information: {e}") from e

    if not git_branch:
        console.print()
        console.print(
            "[bold red]Error:[/bold red] Projects require a git branch.\n\n"
            "[yellow]This repository has no branches yet (no commits), please create an initial branch:[/yellow]\n\n"
            "[bold]git add .[/bold]\n"
            '[bold]git commit -m "first commit"[/bold]\n'
            "[bold]git branch -M main[/bold]"
        )
        return

    default_project_name = get_git_repo_name(git_remote)

    # Prompt for project name with validation
    project_name = prompt_with_validation(
        "\nProject name", default=default_project_name, max_length=96, name_type="Project name"
    )

    # Get workspace details for display
    # workspace = ctx.client.get_workspace(ctx.workspace_id)
    workspace_id = ctx.workspace_id

    # Display confirmation table
    console.print()
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Project", project_name)
    table.add_row("Source", f"{git_remote} ({git_branch})")
    table.add_row("Workspace", workspace_id)
    console.print(table)

    # Confirm creation
    if not click.confirm("\nCreate this project?", default=True):
        click.echo("Project initialization cancelled.")
        return

    # Create project and write config
    request = CreateProjectRequest(
        name=project_name,
        source=ProjectSource(
            github=ProjectSourceGithub(
                remote=git_remote,
                branch=git_branch,
            )
        ),
    )
    try:
        project = ctx.client.create_project(ctx.workspace_id, request)
    except (requests.HTTPError, httpx.HTTPStatusError) as e:
        raise click.ClickException("Failed to create project") from e

    try:
        ev_toml_path.write_text(f'project_id = "{project.id}"\n')
    except OSError as e:
        raise click.ClickException(f"Error writing project configuration: {e}") from e

    console.print(f"\nProject '{project_name}' initialized successfully!")
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Project", project_name)
    table.add_row("ID", project.id)
    console.print(table)
    click.echo("\nNext steps:\n")
    console.print("[dim]# Commit the configuration file[/dim]")
    console.print("[magenta]git add ev.toml[/magenta]")
    console.print('[magenta]git commit -m "Add ev.toml project configuration"[/magenta]')
    console.print("[magenta]git push")
    console.print()
    console.print("[dim]# Run a script on Daft Cloud[/dim]")
    console.print("[magenta]ev run script.py[/magenta]")
