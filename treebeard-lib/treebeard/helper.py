import configparser
import json
import sys
from typing import Optional

import click
import requests
from pydantic import BaseModel

from treebeard.conf import config_path
from treebeard.version import get_version


def set_credentials(email: str, key: str, signup_endpoint: str):
    """Create user credentials"""
    # key = secrets.token_urlsafe(16)
    config = configparser.RawConfigParser()
    config.add_section("credentials")
    config.set("credentials", "TREEBEARD_EMAIL", email)
    # Project id is last 10 numbers of hash of email

    click.echo(signup_endpoint)
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
    version = get_version()

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
    data = json.loads(requests.get(service_status_url).text)
    if "message" in data:
        return data["message"]
    return None


class CliContext(BaseModel):
    debug: bool
