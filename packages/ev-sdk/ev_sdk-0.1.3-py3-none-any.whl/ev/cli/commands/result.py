from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
import httpx
import requests

from ev.cli.context import pass_context
from ev.models import (
    RunStatus,
)

if TYPE_CHECKING:
    from ev.cli.context import Context


def echo(msg: str) -> None:
    click.echo(msg, err=True)


@click.command()
@click.argument("run_id", required=True)
@click.option(
    "--out",
    required=False,
    type=click.Path(path_type=Path),
    default=None,
    help="Location on disk to write results, if found. Writes to STDOUT otherwise.",
)
@click.option("--nopretty", is_flag=True, help="If supplied, do pretty print JSON result. Pretty prints by default.")
@pass_context
def result(ctx: Context, run_id: str, out: Path | None, nopretty: bool) -> None:
    """Get the result of a run."""
    wid = ctx.workspace_id
    pid = ctx.project_id

    if out is not None:
        if out.is_dir():
            raise click.ClickException(f"Output path {out} is a directory. It must be a writable file!")
        if not out.parent.exists():
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise click.ClickException(f"Could not create parent directory for output path {out}") from e

    try:
        status = ctx.client.get_run_status(wid, pid, run_id)

        if status == RunStatus.SUCCEEDED:
            res = ctx.client.get_run_result(wid, pid, run_id)
            if res is None:
                echo(f"Run {run_id} has no result")
            else:
                try:
                    if nopretty:
                        json_res = json.dumps(res, indent=None)
                    else:
                        json_res = json.dumps(res, indent=2)
                        json_res += "\n"
                except json.JSONDecodeError as e:
                    echo(f"[ERROR] Run {run_id} result is not valid JSON: {e}")
                else:
                    if out is None:
                        echo(f"Run {run_id} result:")
                        sys.stderr.flush()
                        sys.stdout.write(json_res)
                        sys.stdout.flush()
                    else:
                        with out.open("wt") as wt:
                            wt.write(json_res)
                        echo(f"Run {run_id} result written to {out}")
        else:
            echo(f"No result yet for run {run_id} because its status is: {status.value}")
    except (requests.HTTPError, httpx.HTTPStatusError) as e:
        raise click.ClickException("Failed to get run result") from e
