from __future__ import annotations

from typing import TYPE_CHECKING

import click

from ev.cli.context import pass_context
from ev.models import (
    RunStatus,
)

if TYPE_CHECKING:
    from ev.cli.context import Context


@click.command()
@click.argument("run_id", required=True)
@pass_context
def cancel(ctx: Context, run_id: str) -> None:
    """Cancel an in-progress run."""
    wid = ctx.workspace_id
    pid = ctx.project_id

    status = ctx.client.get_run_status(wid, pid, run_id)
    if status in (
        RunStatus.PENDING,
        RunStatus.RUNNING,
    ):
        try:
            ctx.client.cancel_run(wid, pid, run_id)
        except Exception as e:
            click.echo(f"Could not cancel run {run_id} due to: {e}")
        else:
            click.echo(f"Run {run_id} successfully cancelled")
    else:
        click.echo(f"Run {run_id} cannot be cancelled because its status is: {status.name.lower()}")
