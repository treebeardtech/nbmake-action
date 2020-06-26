import glob
import os
import os.path
import pprint
import sys
import tarfile
import tempfile
from distutils.dir_util import copy_tree
from typing import List

import click
import yaml

from treebeard.buildtime.run_repo import run_repo
from treebeard.conf import (
    treebeard_config,
    treebeard_env,
    validate_notebook_directory,
)
from treebeard.helper import CliContext, get_time, update

pp = pprint.PrettyPrinter(indent=2)

repo_short_name = treebeard_env.repo_short_name
user_name = treebeard_env.user_name


@click.command()
@click.option("-n", "--notebooks", help="Notebooks to be run", multiple=True)
@click.option(
    "-e", "--env", help="Environment variables to forward into container", multiple=True
)
@click.option(
    "-i",
    "--ignore",
    help="Don't submit unneeded virtual envs and large files",
    multiple=True,
)
@click.option(
    "--confirm/--no-confirm", default=False, help="Confirm all prompt options"
)
@click.option(
    "--dockerless/--no-dockerless",
    default=False,
    help="Run locally without docker container",
)
@click.option(
    "--upload/--no-upload", default=False, help="Upload outputs",
)
@click.option(
    "--debug/--no-debug", default=False, help="Enable debug logging",
)
@click.pass_obj  # type: ignore
def run(
    cli_context: CliContext,
    notebooks: List[str],
    env: List[str],
    ignore: List[str],
    confirm: bool,
    dockerless: bool,
    upload: bool,
    debug: bool,
):
    """
    Run a notebook and optionally schedule it to run periodically
    """
    notebooks = list(notebooks)
    ignore = list(ignore)
    treebeard_config.debug = True
    validate_notebook_directory(treebeard_env, treebeard_config, upload)

    # Apply cli config overrides
    treebeard_yaml_path: str = tempfile.mktemp()  # type: ignore
    with open(treebeard_yaml_path, "w") as yaml_file:
        if notebooks:
            treebeard_config.notebooks = notebooks

        yaml.dump(treebeard_config.dict(), yaml_file)  # type: ignore

    if "TREEBEARD_START_TIME" not in os.environ:
        os.environ["TREEBEARD_START_TIME"] = get_time()

    if dockerless:
        if upload:
            update(status="WORKING")
        click.echo(
            f"🌲  Running locally without docker using your current python environment"
        )
        if not confirm and not click.confirm(
            f"Warning: This will clear the outputs of your notebooks, continue?",
            default=True,
        ):
            sys.exit(0)

        # Note: import runtime.run causes win/darwin devices missing magic to fail at start
        import treebeard.runtime.run

        treebeard.runtime.run.start(upload=upload)  # will sys.exit

    if upload:
        update(status="BUILDING")

    if treebeard_config:
        ignore += (
            treebeard_config.ignore
            + treebeard_config.secret
            + treebeard_config.output_dirs
        )

    click.echo("🌲  Creating Project bundle")

    temp_dir = tempfile.mkdtemp()
    copy_tree(os.getcwd(), str(temp_dir), preserve_symlinks=1)
    notebooks_files = treebeard_config.get_deglobbed_notebooks()
    click.echo(notebooks_files)

    click.echo("🌲  Compressing Repo")

    with tempfile.NamedTemporaryFile(
        "wb", suffix=".tar.gz", delete=False
    ) as src_archive:
        with tarfile.open(fileobj=src_archive, mode="w:gz") as tar:

            def zip_filter(info: tarfile.TarInfo):
                if info.name.endswith("treebeard.yaml"):
                    return None

                for ignored in ignore:
                    if info.name in glob.glob(ignored, recursive=True):
                        return None

                if not confirm:
                    click.echo(f"  Including {info.name}")
                return info

            tar.add(
                str(temp_dir), arcname=os.path.basename(os.path.sep), filter=zip_filter,
            )
            tar.add(treebeard_yaml_path, arcname="treebeard.yaml")

    if not confirm and not click.confirm(
        "Confirm source file set is correct?", default=True
    ):
        click.echo("Exiting")
        sys.exit()

    build_tag = treebeard_env.run_id
    repo_url = f"file://{src_archive.name}"

    status = run_repo(
        str(user_name),
        str(repo_short_name),
        treebeard_env.run_id,
        build_tag,
        repo_url,
        envs_to_forward=env,
        upload=upload,
        branch=treebeard_env.branch,
    )
    click.echo(f"Build exited with status code {status}")
    sys.exit(status)
