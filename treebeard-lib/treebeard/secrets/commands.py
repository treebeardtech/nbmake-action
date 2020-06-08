from typing import IO, Any, List

import click
import requests

from treebeard.conf import (
    secrets_endpoint,
    treebeard_config,
    treebeard_env,
    validate_notebook_directory,
)
from treebeard.secrets.helper import get_secrets_archive


@click.group()
def secrets():
    """Store credentials used by your notebook"""
    pass


@secrets.command()  # type: ignore
@click.argument("files", type=click.File("r"), nargs=-1)
@click.option("--confirm/--no-confirm", default=False)
def push(files: List[IO[Any]], confirm: bool):
    push_secrets(files, confirm)


def push_secrets(files: List[IO[Any]], confirm: bool):
    """Uploads files marked in treebeard.yaml as 'secret'"""
    validate_notebook_directory(treebeard_env, treebeard_config)
    click.echo(
        f"🌲 Pushing secrets for {treebeard_env.project_id}/{treebeard_env.notebook_id}"
    )
    secrets_archive = get_secrets_archive(files, confirm=confirm)
    response = requests.post(  # type: ignore
        secrets_endpoint,
        files={"secrets": open(secrets_archive.name, "rb")},
        headers=treebeard_env.dict(),
    )
    if response.status_code != 200:
        click.echo(
            f"Error: service failure pushing secrets, {response.status_code}: {response.text}"
        )
        return

    click.echo("🔐  secrets pushed\n")
