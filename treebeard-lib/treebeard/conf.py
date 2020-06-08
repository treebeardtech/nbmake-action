import configparser
import os
import time
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import List, Optional

import click
import yaml
from pydantic import BaseModel, ValidationError, validator  # type: ignore

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
    notebooks: List[str] = ["**/*.ipynb"]
    output_dirs: List[str] = ["output"]
    ignore: List[str] = []
    secret: List[str] = []
    kernel_name: str = "python3"
    strict_mode: bool = True
    cell_execution_timeout_seconds: int = 300
    schedule: Optional[str] = None

    @validator("schedule")
    def schedule_valdiator(cls, v: Optional[str]):
        schedules = (None, "hourly", "daily", "weekly")
        if v not in schedules:
            raise ValueError(f"schedule must be one of {schedules}")

        return v and v.lower()

    def get_deglobbed_notebooks(self):
        # warning: sensitive to current directory
        deglobbed_notebooks = []
        for pattern in self.notebooks:
            deglobbed_notebooks.extend(sorted(glob(pattern, recursive=True)))
        if len(deglobbed_notebooks) == 0:
            raise Exception(
                f"No notebooks found in project! Searched for {self.notebooks}"
            )

        ignored_notebooks = []
        for pattern in self.ignore:
            ignored_notebooks.extend(sorted(glob(pattern, recursive=True)))

        return [nb for nb in deglobbed_notebooks if nb not in ignored_notebooks]


env = "production"
if os.getenv("TREEBEARD_ENVIRONMENT"):
    env = os.getenv("TREEBEARD_ENVIRONMENT")


if env == "development":
    click.echo("WARNING: RUNNING IN LOCAL MODE", err=True)
    api_url = "http://localhost:8080"
    treebeard_web_url = "https://localhost:8000"
else:
    api_url = "https://api.treebeard.io"
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
        fatal_exit("No account config detected! Please run `treebeard configure`")

    if not Path("treebeard.yaml").is_file():
        click.secho(  # type: ignore
            "Warning: treebeard.yaml file not found! `treebeard setup` fetches an example.",
            fg="yellow",
        )
        click.echo("Using defaults: notebooks: - '**/*.ipynb' output_dirs: - 'outputs'")

    notebook_files = treebeard_config.get_deglobbed_notebooks()
    if not notebook_files:
        fatal_exit("No notebooks found in project! Treebeard expects at least one.")

    for notebook in notebook_files:
        if not os.path.exists(notebook):
            fatal_exit(
                f"Cannot run non-existent notebook '{notebook}', you should be in a project directory with a treebeard.yaml file"
            )


def get_treebeard_config() -> TreebeardConfig:
    notebook_config = "treebeard.yaml"
    if not os.path.exists(notebook_config):
        return TreebeardConfig()

    with open(notebook_config) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)  # type: ignore
        if not conf:
            return TreebeardConfig()
        try:
            return TreebeardConfig(**conf)
        except ValidationError as e:  # type: ignore
            fatal_exit(f"Error parsing treebeard.yaml\n{e.json()}")  # type: ignore


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

    # .treebeard config is present in CLI in place of env variables
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
secrets_endpoint = (
    f"{api_url}/{treebeard_env.project_id}/{treebeard_env.notebook_id}/secrets"
)
runner_endpoint = (
    f"{api_url}/{treebeard_env.project_id}/{treebeard_env.notebook_id}/runs"
)
service_status_endpoint = f"{api_url}/service_status"
