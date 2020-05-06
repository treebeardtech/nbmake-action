import os
import os.path
import sys
import tarfile
import tempfile
from typing import IO, Any, List

import click

from treebeard.conf import treebeard_config


def get_secrets_archive(files: List[IO[Any]] = [], confirm: bool = True) -> IO[bytes]:
    if treebeard_config:
        files += tuple((open(path, "r") for path in treebeard_config.secret))

    for f in files:
        is_in_project = os.path.realpath(f.name).startswith(os.getcwd())
        if not is_in_project:
            click.echo(
                click.style(
                    f"ERROR: {f.name} is not in the notebook directory. All secrets must be located in the notebook directory",
                    fg="red",
                )
            )

    with tempfile.NamedTemporaryFile(
        "wb", suffix=".tar.gz", delete=False
    ) as secrets_archive:
        with tarfile.open(
            fileobj=secrets_archive, mode="w:gz", dereference=True
        ) as tar:
            for f in files:
                click.echo(f"  Including {f.name}")
                tar.add(f.name)

    if not (
        confirm or click.confirm("Confirm secret file set is correct?", default=True)
    ):
        click.echo("Exiting")
        sys.exit()
    return secrets_archive
