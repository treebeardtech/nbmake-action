import warnings
from typing import Any

import click
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.conf import treebeard_env
from treebeard.helper import CliContext, check_for_updates
from treebeard.notebooks.commands import run
from treebeard.other.commands import config, configure, setup, version
from treebeard.sentry_setup import setup_sentry

user_name = treebeard_env.user_name
repo_short_name = treebeard_env.repo_short_name

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
    setup_sentry()
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
