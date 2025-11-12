from __future__ import annotations

from typing import TYPE_CHECKING

import click
import httpx
import requests
from rich import box
from rich.console import Console
from rich.table import Table

from ev.cli.context import pass_context
from ev.cli.errors import ErrorsGroup

if TYPE_CHECKING:
    from ev.cli.context import Context
    from ev.models import Project

console = Console()


@click.group(name="list", cls=ErrorsGroup)
def _list() -> None:
    """List projects, sources, secrets, etc."""
    pass


@_list.command()
@pass_context
def projects(ctx: Context) -> None:
    """List projects in the current workspace."""
    try:
        workspace_id = ctx.workspace_id
        projects = ctx.client.list_projects(workspace_id)
        _format_projects_table(projects, workspace_id)
    except (requests.HTTPError, httpx.HTTPStatusError) as e:
        raise click.ClickException("Failed to list projects") from e


###
# Formatting Helpers
#
# Note: We will support JSON in the near future.
###


def _format_projects_table(projects: list[Project], workspace_id: str) -> None:
    """Display projects in a formatted table."""
    if not projects:
        console.print(f"No projects found in workspace {workspace_id}.")
        return

    table = Table(box=box.SIMPLE)
    table.add_column("Name")
    table.add_column("ID")
    table.add_column("Source")

    for project in projects:
        source_info = f"GitHub: {project.source.github.remote} ({project.source.github.branch})"
        table.add_row(project.name, project.id, source_info)

    console.print(table)
