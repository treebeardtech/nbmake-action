import glob
import json
import os
import os.path
import pprint
import sys
import tarfile
import tempfile
import time
from datetime import datetime
from typing import Any, List

import click
import docker  # type: ignore
import requests
from dateutil import parser
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.buildtime.run_repo import run_repo
from treebeard.conf import (
    config_path,
    get_time,
    notebooks_endpoint,
    treebeard_config,
    treebeard_env,
    validate_notebook_directory,
)
from treebeard.helper import CliContext
from treebeard.notebooks.types import Run
from treebeard.secrets.helper import get_secrets_archive
from treebeard.util import fatal_exit

pp = pprint.PrettyPrinter(indent=2)

notebook_id = treebeard_env.notebook_id
project_id = treebeard_env.project_id


@click.command()
@click.option("t", "--hourly", flag_value="hourly", help="Run notebook hourly")
@click.option("t", "--daily", flag_value="daily", help="Run notebook daily")
@click.option("t", "--weekly", flag_value="weekly", help="Run notebook weekly")
@click.option(
    "t", "--quarter-hourly", flag_value="quarter-hourly", help="Run quarter-hourly"
)
@click.option(
    "watch", "--watch", is_flag=True, help="Run and check completed build status"
)
@click.option(
    "local", "--local", is_flag=True, help="Build image with local docker installation",
)
@click.option(
    "-i",
    "--ignore",
    help="Don't submit unneeded virtual envs and large files",
    multiple=True,
)
@click.pass_obj
def run(cli_context: CliContext, t: str, watch: bool, ignore: List[str], local: bool):
    """
    Run a notebook and optionally schedule it to run periodically
    """

    validate_notebook_directory(treebeard_env, treebeard_config)

    params = {}
    if t:
        params["schedule"] = t

    spinner: Any = Halo(text="🌲  Compressing Repo\n", spinner="dots")
    spinner.start()

    if treebeard_config:
        ignore += (
            treebeard_config.ignore
            + treebeard_config.secret
            + treebeard_config.output_dirs
        )

    # Create a temporary file for the compressed directory
    # compressed file accessible at f.name
    # git_files: Set[str] = set(
    #     subprocess.check_output(
    #         "git ls-files || exit 0", shell=True, stderr=subprocess.DEVNULL
    #     )
    #     .decode()
    #     .splitlines()
    # )

    with tempfile.NamedTemporaryFile(
        "wb", suffix=".tar.gz", delete=False
    ) as src_archive:
        click.echo("\n")
        with tarfile.open(fileobj=src_archive, mode="w:gz") as tar:

            def zip_filter(info: tarfile.TarInfo):
                for ignored in ignore:
                    if info.name in glob.glob(ignored):
                        return None

                # if len(git_files) > 0 and info.name not in git_files:
                #     return None
                click.echo(f"  Including {info.name}")
                return info

            tar.add(
                os.getcwd(), arcname=os.path.basename(os.path.sep), filter=zip_filter
            )
            tar.add(config_path, arcname=os.path.basename(config_path))
    size = os.path.getsize(src_archive.name)
    max_upload_size = "100MB"
    if size > parse_size(max_upload_size):
        fatal_exit(
            click.style(
                (
                    f"ERROR: Compressed notebook directory is {format_size(size)},"
                    f" max upload size is {max_upload_size}. \nPlease ensure you ignore any virtualenv subdirectory"
                    " using `treebeard run --ignore venv`"
                ),
                fg="red",
            )
        )

    if local:
        spinner.stop()
        build_tag = str(time.mktime(datetime.today().timetuple()))
        repo_image_name = (
            f"gcr.io/treebeard-259315/projects/{project_id}/{notebook_id}:{build_tag}"
        )
        click.echo(f"🌲  Building {repo_image_name} Locally\n")
        secrets_archive = get_secrets_archive()
        repo_url = f"file://{src_archive.name}"
        secrets_url = f"file://{secrets_archive.name}"
        run_repo(
            str(project_id),
            str(notebook_id),
            treebeard_env.run_id,
            build_tag,
            repo_url,
            secrets_url,
            local=True,
        )
        sys.exit(0)

    spinner.text = "🌲  submitting notebook to runner\n"
    response = requests.post(
        notebooks_endpoint,
        files={"repo": open(src_archive.name, "rb")},
        params=params,
        headers=treebeard_env.dict(),
    )

    if response.status_code != 200:
        raise click.ClickException(f"Request failed: {response.text}")

    spinner.stop()
    try:
        json_data = json.loads(response.text)
        click.echo(f"✨  Run has been accepted! {json_data['admin_url']}")
    except:
        click.echo("❗  Request to run failed")
        click.echo(sys.exc_info())

    if watch:
        # spinner = Halo(text='watching build', spinner='dots')
        # spinner.start()
        build_result = None
        while not build_result:
            time.sleep(5)
            response = requests.get(notebooks_endpoint, headers=treebeard_env.dict())
            json_data = json.loads(response.text)
            status = json_data["runs"][-1]["status"]
            click.echo(f"{get_time()} Build status: {status}")
            if status == "SUCCESS":
                build_result = status
                # spinner.stop()
                click.echo(f"Build result: {build_result}")
            elif status in ["FAILURE", "TIMEOUT", "INTERNAL_ERROR", "CANCELLED"]:
                fatal_exit(f"Build failed")


@click.command()
def cancel():
    """Cancels the current notebook build and schedule"""
    validate_notebook_directory(treebeard_env, treebeard_config)
    spinner: Any = Halo(text="cancelling", spinner="dots")
    click.echo(f"🌲  Cancelling {notebook_id}")
    spinner.start()
    requests.delete(notebooks_endpoint, headers=treebeard_env.dict())
    spinner.stop()
    click.echo(f"🛑 Done!")


@click.command()
def status():
    """Show the status of the current notebook"""
    validate_notebook_directory(treebeard_env, treebeard_config)
    response = requests.get(notebooks_endpoint, headers=treebeard_env.dict())
    if response.status_code != 200:
        raise click.ClickException(f"Request failed: {response.text}")

    json_data = json.loads(response.text)
    if len(json_data) == 0:
        fatal_exit(
            "This notebook has not been run. Try running it with `treebeard run`"
        )
    click.echo("🌲  Recent runs:\n")

    max_results = 5
    status_emoji = {
        "SUCCESS": "✅",
        "QUEUED": "💤",
        "WORKING": "⏳",
        "FAILURE": "❌",
        "TIMEOUT": "⏰",
        "CANCELLED": "🛑",
    }

    runs: List[Run] = [Run.parse_obj(run) for run in json_data["runs"][-max_results:]]  # type: ignore
    for run in runs:
        now = parser.isoparse(datetime.utcnow().isoformat() + "Z")
        start_time = parser.isoparse(run.start_time)
        time_string: str = timeago_format(start_time, now=now)

        mechanism: str = run.trigger["mechanism"]
        ran_via = "" if len(mechanism) == 0 else f"via {mechanism}"
        click.echo(
            f"  {status_emoji[run.status]}  {time_string} {ran_via} -- {run.url}"
        )

    if "schedule" in json_data:
        click.echo(f"\n📅  Schedule: {json_data['schedule']}")
