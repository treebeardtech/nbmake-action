import configparser
import datetime
import json
import os
from pathlib import Path
from typing import Optional

import click
import requests
from pydantic import BaseModel

from treebeard.conf import api_url, config_path, treebeard_env
from treebeard.version import get_version

version = get_version()


def set_credentials(email: str, key: str, project_id: str):
    """Create user credentials"""
    config = configparser.RawConfigParser()
    config.add_section("credentials")
    config.set("credentials", "TREEBEARD_EMAIL", email)
    config.set("credentials", "TREEBEARD_PROJECT_ID", project_id)
    config.set("credentials", "TREEBEARD_API_KEY", key)
    with open(config_path, "w") as configfile:
        config.write(configfile)
    click.echo(f"🔑  Config saved in {config_path}")
    return project_id


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


def sanitise_notebook_id(notebook_id: str) -> str:
    out = notebook_id.replace("_", "-")
    out = out.replace(" ", "-")
    out = out.replace(".", "-")
    return out.lower()


def create_example_yaml():
    dirname = os.path.split(os.path.abspath(__file__))[0]
    with open(Path(f"{dirname}/example_treebeard.yaml"), "rb") as f:
        open("treebeard.yaml", "wb").write(f.read())
    return


def update(status: str):
    data = {
        "status": status,
    }

    sha = os.getenv("GITHUB_SHA")
    ref = os.getenv("GITHUB_REF")
    if sha and ref:
        branch = ref.split("/")[-1]
        data["sha"] = sha
        data["branch"] = branch

    def get_time():
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    if status == "WORKING":
        data["start_time"] = get_time()
    else:
        data["end_time"] = get_time()

    update_url = f"{api_url}/{treebeard_env.project_id}/{treebeard_env.notebook_id}/{treebeard_env.run_id}/update"
    click.echo(f"Updating {update_url}")
    click.echo(f"data: {data}")
    resp = requests.post(  # type:ignore
        update_url, json=data, headers={"api_key": treebeard_env.api_key},
    )

    print(f"{resp.status_code}")
