import os
from typing import Any, List, Dict

import click
import docker  # type: ignore

from treebeard.conf import treebeard_env


def run_image(
    project_id: str,
    notebook_id: str,
    run_id: str,
    image_name: str,
    envs_to_forward: List[str],
) -> int:
    client: Any = docker.from_env()  # type: ignore

    pip_treebeard = f"pip install git+https://github.com/treebeardtech/treebeard.git@local-docker#subdirectory=treebeard-lib"

    env: Dict[str, str] = {
        "TREEBEARD_PROJECT_ID": project_id,
        "TREEBEARD_NOTEBOOK_ID": notebook_id,
        "TREEBEARD_API_KEY": treebeard_env.api_key,
        "GITHUB_RUN_ID": os.getenv("GITHUB_RUN_ID"),
        "GITHUB_REF": os.getenv("GITHUB_REF"),
        "GITHUB_SHA": os.getenv("GITHUB_SHA"),
    }

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
    container = client.containers.run(
        image_name,
        f"bash -c '(which treebeard > /dev/null || {pip_treebeard}) && treebeard run --dockerless --upload --confirm'",
        environment=env,
        detach=True,
    )

    [click.echo(line, nl=False) for line in container.logs(stream=True)]

    result = container.wait()
    return int(result["StatusCode"])
