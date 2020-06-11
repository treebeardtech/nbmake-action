import datetime
import glob
import json
import os
import os.path
import pprint
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from distutils.dir_util import copy_tree
from typing import Any, List

import click
import docker  # type: ignore
import requests
import yaml
from dateutil import parser
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.buildtime.run_repo import run_repo
from treebeard.conf import (
    api_url,
    config_path,
    get_time,
    runner_endpoint,
    treebeard_config,
    treebeard_env,
    validate_notebook_directory,
)
from treebeard.helper import CliContext, sanitise_notebook_id
from treebeard.notebooks.types import Run
from treebeard.secrets.commands import push_secrets as push_secrets_to_store
from treebeard.secrets.helper import get_secrets_archive
from treebeard.util import fatal_exit

pp = pprint.PrettyPrinter(indent=2)

notebook_id = treebeard_env.notebook_id
project_id = treebeard_env.project_id


@click.command()
@click.option(
    "watch", "--watch", is_flag=True, help="Run and check completed build status"
)
@click.option(
    "local", "--local", is_flag=True, help="Build image with local docker installation",
)
@click.option("-n", "--notebooks", help="Notebooks to be run", multiple=True)
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
    "--push-secrets/--no-push-secrets",
    default=False,
    help="Confirm all prompt options except pushing secrets",
)
@click.option(
    "--dockerless/--no-dockerless",
    default=False,
    help="Run locally without docker container",
)
@click.pass_obj  # type: ignore
def run(
    cli_context: CliContext,
    watch: bool,
    notebooks: List[str],
    ignore: List[str],
    local: bool,
    confirm: bool,
    push_secrets: bool,
    dockerless: bool,
):
    """
    Run a notebook and optionally schedule it to run periodically
    """
    notebooks = list(notebooks)
    ignore = list(ignore)

    validate_notebook_directory(treebeard_env, treebeard_config)

    # Apply cli config overrides
    treebeard_yaml_path: str = tempfile.mktemp()  # type: ignore
    with open(treebeard_yaml_path, "w") as yaml_file:
        if notebooks:
            treebeard_config.notebooks = notebooks

        yaml.dump(treebeard_config.dict(), yaml_file)  # type: ignore

    if dockerless:
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

        treebeard.runtime.run.start(upload_outputs=False)  # will sys.exit

    params = {}
    if treebeard_config.schedule:
        if confirm or click.confirm(
            f"📅 treebeard.yaml contains schedule '{treebeard_config.schedule}'. Enable it?"
        ):
            params["schedule"] = treebeard_config.schedule

    if (
        not local
        and len(treebeard_config.secret) > 0
        and not confirm
        and not push_secrets
    ):
        push_secrets = click.confirm("Push secrets first?", default=True)

    if push_secrets:
        push_secrets_to_store([], confirm=confirm)

    if treebeard_config:
        ignore += (
            treebeard_config.ignore
            + treebeard_config.secret
            + treebeard_config.output_dirs
        )

    click.echo("🌲  Copying project to tempdir and stripping notebooks")

    temp_dir = tempfile.mkdtemp()
    copy_tree(os.getcwd(), str(temp_dir), preserve_symlinks=1)
    notebooks_files = treebeard_config.get_deglobbed_notebooks()
    for notebooks_file in notebooks_files:
        try:
            subprocess.check_output(["nbstripout"] + notebooks_file, cwd=temp_dir)
        except:
            print(f"Failed to nbstripout {notebooks_file}! Is it valid?")
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

                # if len(git_files) > 0 and info.name not in git_files:
                #     return None
                click.echo(f"  Including {info.name}")
                return info

            tar.add(
                str(temp_dir), arcname=os.path.basename(os.path.sep), filter=zip_filter,
            )
            tar.add(config_path, arcname=os.path.basename(config_path))
            tar.add(treebeard_yaml_path, arcname="treebeard.yaml")

    if not confirm and not click.confirm(
        "Confirm source file set is correct?", default=True
    ):
        click.echo("Exiting")
        sys.exit()

    if local:
        build_tag = str(time.mktime(datetime.datetime.today().timetuple()))
        repo_image_name = f"gcr.io/treebeard-259315/projects/{project_id}/{sanitise_notebook_id(str(notebook_id))}:{build_tag}"
        click.echo(f"🌲  Building {repo_image_name} Locally\n")
        secrets_archive = get_secrets_archive()
        repo_url = f"file://{src_archive.name}"
        secrets_url = f"file://{secrets_archive.name}"
        status = run_repo(
            str(project_id),
            str(notebook_id),
            treebeard_env.run_id,
            build_tag,
            repo_url,
            secrets_url,
            branch="cli",
            local=True,
        )
        click.echo(f"Local build exited with status code {status}")
        sys.exit(status)

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

    time_seconds = int(time.mktime(datetime.datetime.today().timetuple()))
    build_tag = str(time_seconds)

    upload_api = f"{api_url}/source_upload_url/{project_id}/{notebook_id}/{build_tag}"
    resp = requests.get(upload_api)  # type: ignore

    signed_url: str = resp.text
    put_resp = requests.put(  # type: ignore
        signed_url,
        open(src_archive.name, "rb"),
        headers={"Content-Type": "application/x-tar"},
    )
    assert put_resp.status_code == 200

    if os.getenv("GITHUB_ACTIONS"):
        params["event"] = os.getenv("GITHUB_EVENT_NAME")
        params["sha"] = os.getenv("GITHUB_SHA")
        params["branch"] = os.getenv("GITHUB_REF").split("/")[-1]
        workflow = os.getenv("GITHUB_WORKFLOW")
        params["workflow"] = (
            workflow.replace(".yml", "").replace(".yaml", "").split("/")[-1]
        )

    click.echo(f"🌲  submitting archive to runner ({format_size(size)})...")
    submit_endpoint = f"{api_url}/runs/{treebeard_env.project_id}/{treebeard_env.notebook_id}/{build_tag}"
    response = requests.post(  # type: ignore
        submit_endpoint,
        params=params,
        headers={"api_key": treebeard_env.api_key, "email": treebeard_env.email},
    )
    shutil.rmtree(temp_dir)

    if response.status_code != 200:
        raise click.ClickException(f"Request failed: {response.text}")

    try:
        json_data = json.loads(response.text)
        click.echo(f"✨  Run has been accepted! {json_data['admin_url']}")
    except:
        click.echo("❗  Request to run failed")
        click.echo(sys.exc_info())

    if watch:
        build_result = None
        while not build_result:
            time.sleep(5)
            response = requests.get(runner_endpoint, headers=treebeard_env.dict())  # type: ignore
            json_data = json.loads(response.text)
            if len(json_data["runs"]) == 0:
                status = "FAILURE"
            else:
                status = json_data["runs"][-1]["status"]
            click.echo(f"{get_time()} Build status: {status}")
            if status == "SUCCESS":
                build_result = status
                click.echo(f"Build result: {build_result}")
            elif status in ["FAILURE", "TIMEOUT", "INTERNAL_ERROR", "CANCELLED"]:
                fatal_exit(f"Build failed")


@click.command()
def cancel():
    """Cancels the current notebook build and schedule"""
    validate_notebook_directory(treebeard_env, treebeard_config)
    notif = f"🌲  Cancelling {notebook_id}"
    spinner: Any = Halo(text=notif, spinner="dots")
    spinner.start()
    requests.delete(runner_endpoint, headers=treebeard_env.dict())  # type: ignore
    spinner.stop()
    click.echo(f"{notif}...🛑 cancellation confirmed!")


@click.command()
def status():
    """Show the status of the current notebook"""
    validate_notebook_directory(treebeard_env, treebeard_config)
    response = requests.get(runner_endpoint, headers=treebeard_env.dict())  # type: ignore
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
        now = parser.isoparse(datetime.datetime.utcnow().isoformat() + "Z")
        start_time = parser.isoparse(run.start_time)
        time_string: str = timeago_format(start_time, now=now)

        mechanism: str = run.trigger["mechanism"]
        ran_via = "" if len(mechanism) == 0 else f"via {mechanism}"
        try:
            branch = f"🔀{run.trigger['branch']}"
        except:
            branch = ""

        click.echo(
            f"  {status_emoji[run.status]}  {time_string} {ran_via} {branch} -- {run.url}"
        )
