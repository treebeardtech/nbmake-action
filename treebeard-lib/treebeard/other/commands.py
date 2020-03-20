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
import uuid
import pprint

pp = pprint.PrettyPrinter(indent=2)


project_id = treebeard_env.project_id
notebook_id = treebeard_env.notebook_id

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)


@click.command()
@click.option("--email", prompt="Your email:")
def configure(email: str):
    """Register with Treebeard services"""
    key = str(uuid.uuid4())
    project_id = set_credentials(email, key, signup_endpoint)
    webbrowser.open_new_tab(
        f"{treebeard_web_url}/cli_signup?email={email}&api_key={key}&project_id={project_id}"
    )


@click.command()
@click.option(
    "--notebook", prompt="Notebook file:", default="main.ipynb",
)
@click.option(
    "--ignore", prompt="Files & folders to ignore (e.g: env, .git)", default=[""],
)
@click.option("--secret", prompt="Secrets files", default=[""])
@click.option(
    "--output_dirs", prompt="Output directories (e.g: output, plots)", default=[""],
)
def setup(notebook: str, ignore: List[str], secret: List[str], output_dirs: List[str]):
    """Creates treebeard.yaml configuration file for the project"""
    treebeard_yaml = dict(notebook=notebook)
    if all(ignore):
        ignore = [x.strip() for x in str(ignore).split(",")]
        treebeard_yaml.update(ignore=ignore)
    if all(output_dirs):
        output_dirs = [x.strip() for x in str(output_dirs).split(",")]
        treebeard_yaml.update(output_dirs=output_dirs)
    if all(secret):
        secret = [x.strip() for x in str(secret).split(",")]
        treebeard_yaml.update(secret=secret)
    with open(r"treebeard.yaml", "w") as f:
        yaml.dump(treebeard_yaml, f, default_flow_style=False)
    click.echo("📁 treebeard.yaml file created.")


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
