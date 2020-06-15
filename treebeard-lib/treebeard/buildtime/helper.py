import os
from typing import Any

import click
import docker  # type: ignore

from treebeard.conf import treebeard_env


def run_image(project_id: str, notebook_id: str, run_id: str, image_name: str) -> int:
    client: Any = docker.from_env()  # type: ignore

    pip_treebeard = f"pip install git+https://github.com/treebeardtech/treebeard.git@local-docker#subdirectory=treebeard-lib"

    click.echo(f"Starting: {pip_treebeard}")
    container = client.containers.run(
        image_name,
        f"bash -c '(which treebeard > /dev/null || {pip_treebeard}) && treebeard run --dockerless --upload --confirm'",
        environment={
            "TREEBEARD_PROJECT_ID": project_id,
            "TREEBEARD_NOTEBOOK_ID": notebook_id,
            "TREEBEARD_API_KEY": treebeard_env.api_key,
            "GITHUB_RUN_ID": os.getenv("GITHUB_RUN_ID"),
            "GITHUB_REF": os.getenv("GITHUB_REF"),
            "GITHUB_SHA": os.getenv("GITHUB_SHA"),
        },
        detach=True,
    )

    [click.echo(line, nl=False) for line in container.logs(stream=True)]

    result = container.wait()
    return int(result["StatusCode"])
