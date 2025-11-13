from __future__ import annotations

import asyncio
import functools
from typing import Any

import click

import ev.cli.commands.app
import ev.cli.commands.cancel
import ev.cli.commands.configure
import ev.cli.commands.init
import ev.cli.commands.list
import ev.cli.commands.login
import ev.cli.commands.result
import ev.cli.commands.run
from ev.cli.context import Context
from ev.cli.errors import ErrorsGroup


def click_sync(function) -> Any:  # type: ignore  # noqa: ANN001
    """Decorator to use an async function as a click command."""

    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(function(*args, **kwargs))

    return wrapper


@click.group(cls=ErrorsGroup)
@click.option("--profile", help="Configuration profile to use")
@click.pass_context
def main(ctx: click.Context, profile: str | None = None) -> None:
    """The Daft Cloud CLI application."""
    ctx.obj = Context.load(profile=profile)


main.add_command(ev.cli.commands.app.app)
main.add_command(ev.cli.commands.configure.configure)
main.add_command(ev.cli.commands.init.init)
main.add_command(ev.cli.commands.list._list, name="list")
main.add_command(ev.cli.commands.login.login)
main.add_command(ev.cli.commands.run.run)
main.add_command(ev.cli.commands.result.result)
main.add_command(ev.cli.commands.cancel.cancel)


if __name__ == "__main__":
    main()
