import os
from typing import Any, Dict, List

import click
import docker  # type: ignore

from treebeard.conf import treebeard_env


def run_image(
    project_id: str,
    notebook_id: str,
    run_id: str,
    image_name: str,
    envs_to_forward: List[str],
    upload: bool,
) -> int:
    client: Any = docker.from_env()  # type: ignore

    pip_treebeard = f"pip install git+https://github.com/treebeardtech/treebeard.git@local-docker#subdirectory=treebeard-lib"

    env: Dict[str, str] = {
        "TREEBEARD_PROJECT_ID": project_id,
        "TREEBEARD_NOTEBOOK_ID": notebook_id,
        "TREEBEARD_START_TIME": os.environ["TREEBEARD_START_TIME"],
    }

    if treebeard_env.api_key:
        env["TREEBEARD_API_KEY"] = treebeard_env.api_key

    if "GITHUB_RUN_ID" in os.environ:
        env["GITHUB_RUN_ID"] = os.environ["GITHUB_RUN_ID"]
    if "GITHUB_REF" in os.environ:
        env["GITHUB_REF"] = os.environ["GITHUB_REF"]
    if "GITHUB_SHA" in os.environ:
        env["GITHUB_SHA"] = os.environ["GITHUB_SHA"]

    for e in envs_to_forward:
        var = os.getenv(e)
        if var:
            env[e] = var
        else:
            click.secho(  # type:ignore
                f"Warning: {e} is unset so cannot be forwarded to container",
                fg="yellow",
            )

    click.echo(f"Starting container: {pip_treebeard}\nEnvironment: {env}")
    upload_flag = "--upload" if upload else "--no-upload"
    container = client.containers.run(
        image_name,
        f"bash -c '(which treebeard > /dev/null || {pip_treebeard}) && treebeard run --dockerless {upload_flag} --confirm'",
        environment=env,
        detach=True,
    )

    [click.echo(line, nl=False) for line in container.logs(stream=True)]

    result = container.wait()
    return int(result["StatusCode"])
