import os

if os.name == "nt":
    try:
        import sys
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8")
    except:
        pass

import warnings
from typing import Any

import click
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.helper import CliContext, check_for_updates
from treebeard.notebooks.commands import run
from treebeard.other.commands import config, configure, setup, version

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context  # type: ignore
def cli(ctx: Any, debug: bool):
    """🌲 
      
      code: https://github.com/treebeardtech/treebeard
      
      docs: https://treebeard.readthedocs.io/
    """
    ctx.obj = CliContext(debug=debug)
    pass


@cli.resultcallback()
def process_result(*args: Any, **kwargs: Any):
    check_for_updates()


cli.add_command(configure)  # type: ignore
cli.add_command(run)  # type: ignore
cli.add_command(setup)  # type: ignore
cli.add_command(config)  # type: ignore
cli.add_command(version)  # type: ignore
