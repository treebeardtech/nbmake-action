import configparser
import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
import requests
from pydantic import BaseModel

from treebeard.conf import config_path
from treebeard.version import get_version

version = get_version()


def set_credentials(email: str, key: str, signup_endpoint: str):
    """Create user credentials"""
    config = configparser.RawConfigParser()
    config.add_section("credentials")
    config.set("credentials", "TREEBEARD_EMAIL", email)

    response = requests.post(signup_endpoint, headers={"api_key": key, "email": email},)

    if response.status_code != 200:
        raise click.ClickException(f"Request failed: {response.text}")

    try:
        json_data = json.loads(response.text)
        project_id = json_data["project_id"]
    except:
        click.echo("❗  Request to configure failed")
        click.echo(sys.exc_info())
        if response:
            click.echo(response.text)
        return

    config.set("credentials", "TREEBEARD_PROJECT_ID", project_id)
    config.set("credentials", "TREEBEARD_API_KEY", key)
    with open(config_path, "w") as configfile:
        config.write(configfile)
    click.echo(f"🔑  Config saved in {config_path}")
    return project_id


def check_for_updates():
    pypi_data = requests.get("https://pypi.org/pypi/treebeard/json")
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
        data = json.loads(requests.get(service_status_url).text)
        if "message" in data:
            return data["message"]
    except:  # Non-200 status/timeout, etc.
        return None


class CliContext(BaseModel):
    debug: bool


def sanitise_notebook_id(notebook_id: str) -> str:
    out = notebook_id.replace("_", "-")
    out = out.replace(" ", "-")
    return out.lower()


def create_example_yaml():
    dirname = os.path.split(os.path.abspath(__file__))[0]
    with open(Path(f"{dirname}/example_treebeard.yaml"), "rb") as f:
        open("treebeard.yaml", "wb").write(f.read())
    return
