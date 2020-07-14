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

META_NOTEBOOKS = "treebeard/**/*ipynb"


class TreebeardEnv(BaseModel):
    repo_short_name: str

    user_name: str
    run_id: str
    api_key: Optional[str] = None  # Not present at build time
    branch: str = "cli"

    @property
    def run_path(self):
        return f"{self.user_name}/{self.repo_short_name}/{self.run_id}"

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
    kernel_name: str = "python3"
    strict_mode: bool = True
    cell_execution_timeout_seconds: int = 300
    schedule: Optional[str] = None
    debug: bool = False
    treebeard_ref: str = os.getenv("TREEBEARD_REF", "master")

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
                f"No notebooks found in project! Searched for {self.notebooks}, cwd {os.getcwd()}"
            )

        ignored_notebooks = []
        for pattern in [META_NOTEBOOKS] + self.ignore:
            ignored_notebooks.extend(sorted(glob(pattern, recursive=True)))

        return [nb for nb in deglobbed_notebooks if nb not in ignored_notebooks]


class GitHubDetails(BaseModel):
    sha: str
    branch: str
    workflow: str
    event_name: str
    event_path: str
    run_id: str
    user_name: str
    repo_short_name: str


class TreebeardContext(BaseModel):
    treebeard_env: TreebeardEnv
    treebeard_config: TreebeardConfig
    github_details: Optional[GitHubDetails] = None


env = os.getenv("TREEBEARD_ENVIRONMENT", "staging")

if env == "development":
    click.echo("WARNING: RUNNING IN LOCAL MODE", err=True)
    api_url = "http://localhost:8080"
    treebeard_web_url = "https://localhost:8000"
else:
    api_url = "https://api.treebeard.io"
    treebeard_web_url = "https://treebeard.io"


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def get_config_path():
    home = str(Path.home())
    return f"{home}/.treebeard"


def validate_notebook_directory(
    treebeard_env: TreebeardEnv, treebeard_config: TreebeardConfig, upload: bool
):
    if upload and treebeard_env.user_name is None:
        fatal_exit("No account config detected! Please run `treebeard configure`")

    # if not Path("treebeard.yaml").is_file():
    #     click.secho(  # type: ignore
    #         "Warning: treebeard.yaml file not found! `treebeard setup` fetches an example.",
    #         fg="yellow",
    #     )
    #     click.echo("Using defaults: notebooks: - '**/*.ipynb' output_dirs: - 'outputs'")

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


def get_treebeard_env(github_details: Optional[GitHubDetails]) -> TreebeardEnv:
    """Reads variables from a local file, credentials.cfg"""

    run_id = os.getenv("TREEBEARD_RUN_ID")  # available at runtime

    if not run_id:
        if github_details:
            time_id = str(int(time.time()))[
                -3:
            ]  # add time to id to prevent clashes when restarted workflows have the same ID
            run_id = f"github-{github_details.run_id}-{time_id}"
        else:
            run_id = f"local-{int(time.time())}"
    os.environ["TREEBEARD_RUN_ID"] = run_id

    repo_short_name = os.getenv("TREEBEARD_REPO_SHORT_NAME")
    if not repo_short_name:
        repo_short_name = Path(os.getcwd()).name

    api_key = os.getenv("TREEBEARD_API_KEY")

    # .treebeard config is present in CLI in place of env variables
    user_name = "local-user"
    config_path = get_config_path()

    if github_details:
        user_name = github_details.user_name
    if os.path.exists(config_path):
        config = configparser.RawConfigParser()
        config.read(config_path)
        user_name = config.get("credentials", "user_name")
        api_key = config.get("credentials", "api_key")

    if "TREEBEARD_USER_NAME" in os.environ:  # runtime
        user_name = os.environ["TREEBEARD_USER_NAME"]

    def get_branch():
        if github_details:
            return github_details.branch
        else:
            return "cli"

    return TreebeardEnv(
        repo_short_name=repo_short_name,
        user_name=user_name,
        run_id=run_id,
        api_key=api_key,
        branch=get_branch(),
    )
