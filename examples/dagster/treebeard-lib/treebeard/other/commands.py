import warnings
import webbrowser

import click
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.conf import signup_endpoint, treebeard_env, treebeard_web_url
from treebeard.helper import set_credentials
from treebeard.version import get_version

project_id = treebeard_env.project_id
notebook_id = treebeard_env.notebook_id

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)


@click.command()
@click.option("--email", prompt="Your email:")
@click.option("--key", prompt="Your API key:")
def configure(email: str, key: str):
    """Set initial credentials"""
    project_id = set_credentials(email, key, signup_endpoint)
    webbrowser.open_new_tab(
        f"{treebeard_web_url}/cli_signup?email={email}&api_key={key}&project_id={project_id}"
    )


@click.command()
def version():
    """Shows treebeard package version"""
    click.echo(get_version())


@click.command()
def info():
    """Shows treebeard credentials and project info"""
    click.echo(treebeard_env)
