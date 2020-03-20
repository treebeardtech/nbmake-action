import configparser
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import click
import yaml
from pydantic import BaseModel, ValidationError  # type: ignore

from treebeard.util import fatal_exit


class TreebeardEnv(BaseModel):
    notebook_id: Optional[
        str
    ] = None  # Not present when CLI is not in notebook directory
    project_id: Optional[str] = None  # Not present when initially installing
    run_id: str
    email: Optional[str] = None  # Not present at build time
    api_key: Optional[str] = None  # Not present at build time

    def __str__(self) -> str:
        dict_obj = self.dict()
        if self.api_key:
            unredacted_length = 4
            dict_obj["api_key"] = (
                "x" * (len(self.api_key) - unredacted_length)
                + self.api_key[-unredacted_length:]
            )
        return str(dict_obj)


class TreebeardConfig(BaseModel):
    notebook: str = "main.ipynb"
    output_dirs: Tuple[str, ...] = tuple(["output"])
    ignore: Tuple[str, ...] = ()
    secret: Tuple[str, ...] = ()


env = "production"
if os.getenv("TREEBEARD_ENVIRONMENT"):
    env = os.getenv("TREEBEARD_ENVIRONMENT")


if env == "development":
    click.echo("WARNING: RUNNING IN LOCAL MODE", err=True)
    url = "http://localhost:8080"
    treebeard_web_url = "https://localhost:8000"
else:
    url = "https://scheduler-cvee2224cq-ew.a.run.app"
    treebeard_web_url = "https://treebeard.io"


def get_run_path(treebeard_env: TreebeardEnv):
    return (
        f"{treebeard_env.project_id}/{treebeard_env.notebook_id}/{treebeard_env.run_id}"
    )


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def get_config_path():
    home = str(Path.home())
    return f"{home}/.treebeard"


def validate_notebook_directory(
    treebeard_env: TreebeardEnv, treebeard_config: TreebeardConfig
):
    if treebeard_env.project_id is None:
        click.echo(
            click.style(
                "No account config detected! Please run treebeard configure", fg="red",
            ),
            err=True,
        )

    if not os.path.exists(treebeard_config.notebook):
        fatal_exit(
            f"Cannot run non-existent notebook '{treebeard_config.notebook}', you should be in a project directory with a treebeard.yaml file"
        )


def get_treebeard_config() -> TreebeardConfig:
    notebook_config = "treebeard.yaml"
    if not os.path.exists(notebook_config):
        return TreebeardConfig()

    with open(notebook_config) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
        if not conf:
            fatal_exit("treebeard.yaml config file exists but is empty")
        try:
            return TreebeardConfig(**conf)
        except ValidationError as e:  # type: ignore
            fatal_exit(f"Error parsing treebeard.yaml\n{e.json()}")


def get_treebeard_env():
    """Reads variables from a local file, credentials.cfg"""
    treebeard_project_id = os.getenv("TREEBEARD_PROJECT_ID")
    run_id = os.getenv("TREEBEARD_RUN_ID")
    if run_id is None:
        run_id = f"local-{int(time.time())}"

    notebook_id = os.getenv("TREEBEARD_NOTEBOOK_ID")
    if not notebook_id:
        notebook_id = Path(os.getcwd()).name

    email = None
    api_key = None

    # .treebeard config is present in CLI and Runtime
    if os.path.exists(config_path):
        config = configparser.RawConfigParser()
        config.read(config_path)
        email = config.get("credentials", "treebeard_email")
        treebeard_project_id = config.get("credentials", "treebeard_project_id")
        api_key = config.get("credentials", "treebeard_api_key")

    return TreebeardEnv(
        notebook_id=notebook_id,
        project_id=treebeard_project_id,
        run_id=run_id,
        email=email,
        api_key=api_key,
    )


config_path = get_config_path()
treebeard_config = get_treebeard_config()
treebeard_env = get_treebeard_env()
run_path = get_run_path(treebeard_env)
secrets_endpoint = f"{url}/projects/{treebeard_env.project_id}/notebooks/{treebeard_env.notebook_id}/secrets"
notebooks_endpoint = f"{url}/notebooks/{treebeard_env.notebook_id}"
signup_endpoint = f"{url}/cli_signup"
service_status_endpoint = f"{url}/service_status"
