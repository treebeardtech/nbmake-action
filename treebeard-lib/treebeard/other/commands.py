import pprint
import requests
import uuid
import warnings
import webbrowser
from typing import List

import click
import yaml
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.conf import signup_endpoint, treebeard_env, treebeard_web_url
from treebeard.helper import set_credentials
from treebeard.version import get_version

pp = pprint.PrettyPrinter(indent=2)


project_id = treebeard_env.project_id
notebook_id = treebeard_env.notebook_id

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)


@click.command()
@click.option("--email", prompt="Your email:")
@click.option("--api_key", default=str(uuid.uuid4()))
def configure(email: str, api_key: str):
    """Register with Treebeard services"""
    project_id = set_credentials(email, api_key, signup_endpoint)
    web_signup_url = f"{treebeard_web_url}/cli_signup?email={email}&api_key={api_key}&project_id={project_id}"
    webbrowser.open_new_tab(web_signup_url)
    click.echo(
        click.style(
            f"Please ensure you complete web signup at {web_signup_url} before continuing!",
            fg="red",
        )
    )


@click.command()
@click.option(
    "--notebooks",
    prompt="Notebook files/patterns e.g.: *.ipynb, subdir/run.ipynb:",
    default=["main.ipynb"],
)
@click.option(
    "--ignore", prompt="Files & folders to ignore e.g: env, .git", default=[""],
)
@click.option("--secret", prompt="Secrets files", default=[""])
@click.option(
    "--output_dirs", prompt="Output directories (e.g: output, plots)", default=[""],
)
def setup():
    """Fetches example treebeard.yaml configuration file"""
    url = "https://github.com/treebeardtech/treebeard/blob/master/examples/example_treebeard.yaml"
    f = requests.get(url)
    open("example_treebeard.yaml", "wb").write(f.content)
    click.echo(
        "📁 fetched example_treebeard.yaml - please edit and save as treebeard.yaml"
    )


@click.command()
def version():
    """Shows treebeard package version"""
    click.echo(get_version())


@click.group()
def config():
    """Shows Treebeard internal configuration"""


@config.command()
def list():
    click.echo(pp.pformat(treebeard_env.dict()))


@config.command()
@click.argument("key", type=click.STRING)
def get(key: str):
    if key in treebeard_env.dict():
        click.echo(treebeard_env.dict()[key])
    else:
        click.echo(f"There is no value for {key}")
