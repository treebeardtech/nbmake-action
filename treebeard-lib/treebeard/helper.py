import configparser
import datetime
import json
import mimetypes
import os
import subprocess
import sys
from glob import glob
from pathlib import Path
from typing import Optional

import click
import requests
from pydantic import BaseModel  # type: ignore
from requests import Response
from sentry_sdk import capture_message  # type: ignore

from treebeard.conf import (
    META_NOTEBOOKS,
    TreebeardContext,
    api_url,
    get_config_path,
)
from treebeard.version import get_version

version = get_version()


def log(message: str):
    print(f'{datetime.datetime.now().strftime("%H:%M:%S")}: {message}')


def set_credentials(key: str, user_name: str):
    """Create user credentials"""
    config = configparser.RawConfigParser()
    config.add_section("credentials")
    config.set("credentials", "user_name", user_name)
    config.set("credentials", "api_key", key)
    with open(get_config_path(), "w") as configfile:
        config.write(configfile)
    click.echo(f"🔑  Config saved in {get_config_path()}")
    return user_name


def check_for_updates():
    pypi_data = requests.get("https://pypi.org/pypi/treebeard/json")  # type: ignore
    latest_version = json.loads(pypi_data.text)["info"]["version"]

    if latest_version != version:
        click.echo(
            click.style(
                "🌲 Warning: you are not on the latest version of Treebeard, update with `pip install --upgrade treebeard`",
                fg="yellow",
            ),
            err=True,
        )


def get_service_status_message(service_status_url: str) -> Optional[str]:
    try:
        data = json.loads(requests.get(service_status_url).text)  # type: ignore
        if "message" in data:
            return data["message"]
    except:  # Non-200 status/timeout, etc.
        return None


class CliContext(BaseModel):
    debug: bool


def sanitise_repo_short_name(repo_short_name: str) -> str:
    out = repo_short_name
    out = out.replace(" ", "-")
    out = out.replace(".", "-")
    return out.lower()


def create_example_yaml():
    dirname = os.path.split(os.path.abspath(__file__))[0]
    with open(Path(f"{dirname}/example_treebeard.yaml"), "rb") as f:
        open("treebeard.yaml", "wb").write(f.read())
    return


def get_time():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def update(
    treebeard_context: TreebeardContext, update_url: str, status: Optional[str] = None
):
    data = {}
    if status:
        data["status"] = status

    github_details = treebeard_context.github_details
    if github_details:
        data["workflow"] = (
            github_details.workflow.replace(".yml", "")
            .replace(".yaml", "")
            .split("/")[-1]
        )

        data["event_name"] = github_details.event_name
        if github_details.event_name == "push" and os.path.exists(
            github_details.event_path
        ):
            with open(github_details.event_path, "r") as event:
                event_json = json.load(event)
                data["sender"] = event_json["sender"]
                data["head_commit"] = event_json["head_commit"]

        data["sha"] = github_details.sha
        data["branch"] = github_details.branch

    data["start_time"] = os.getenv("TREEBEARD_START_TIME") or get_time()
    if status in ["SUCCESS", "FAILURE"]:
        data["end_time"] = get_time()

    treebeard_env = treebeard_context.treebeard_env
    resp = requests.post(  # type:ignore
        update_url, json=data, headers={"api_key": treebeard_env.api_key},
    )

    treebeard_config = treebeard_context.treebeard_config
    if treebeard_config.debug:
        print(f"Updating backend with data\n{data}")

    if resp.status_code != 200:
        capture_message(f"Failed to update tb {resp.status_code}\n{update_url}\n{data}")


def shell(command: str):
    with subprocess.Popen(
        ["bash", "-c", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
    ) as p:
        if p.stdout:
            for line in p.stdout:
                print(line, end="")  # process line here

        if p.stderr:
            for line in p.stderr:
                print(line, end="", file=sys.stderr)  # process line here

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)


def upload_artifact(
    treebeard_context: TreebeardContext,
    filename: str,
    upload_path: str,
    status: Optional[str],
    set_as_thumbnail: bool = False,
):
    log(f"Uploading {filename} to {upload_path}\n")
    content_type: str = str(mimetypes.guess_type(filename)[0])
    get_url_params = {"content_type": content_type}
    put_object_headers = {"Content-Type": content_type}
    if status:
        get_url_params["status"] = status
        put_object_headers["x-goog-meta-status"] = status

    with open(filename, "rb") as data:
        resp: Response = requests.get(  # type: ignore
            f"{api_url}/get_upload_url/{upload_path}", params=get_url_params,
        )
        if resp.status_code != 200:
            msg = (
                f"Get signed url failed for {filename}, {resp.status_code}\n{resp.text}"
            )
            capture_message(msg)
            raise (Exception(msg))
        signed_url: str = resp.text
        put_resp = requests.put(signed_url, data, headers=put_object_headers,)  # type: ignore
        if put_resp.status_code != 200:
            msg = f"Put object failed for {filename}, {put_resp.status_code}\n{put_resp.text}"
            capture_message(msg)
            raise (Exception(msg))

        qs = "set_as_thumbnail=true" if set_as_thumbnail else ""
        extras_resp = requests.post(f"{api_url}/{upload_path}/create_extras?{qs}")  # type: ignore
        if put_resp.status_code != 200:
            msg = f"Extras failed for {filename}, {extras_resp.status_code}\n{extras_resp.text}"
            capture_message(msg)

    update(
        treebeard_context,
        update_url=f"{api_url}/{treebeard_context.treebeard_env.run_path}/update",
    )


def upload_meta_nbs(treebeard_context: TreebeardContext):
    notebooks_files = glob(META_NOTEBOOKS, recursive=True)

    for notebook_path in notebooks_files:
        notebook_upload_path = (
            f"{treebeard_context.treebeard_env.run_path}/{notebook_path}"
        )
        nb_status = None

        upload_artifact(
            treebeard_context, notebook_path, notebook_upload_path, nb_status
        )
