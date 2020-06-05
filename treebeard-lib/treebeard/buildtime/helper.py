from typing import Any

import click
import docker  # type: ignore


def run_image(project_id: str, notebook_id: str, run_id: str, image_name: str) -> int:
    client: Any = docker.from_env()  # type: ignore

    container = client.containers.run(
        image_name,
        "bash -c '(which treebeard > /dev/null || pip install treebeard) && python -m treebeard.runtime.run'",
        environment={
            "TREEBEARD_PROJECT_ID": project_id,
            "TREEBEARD_NOTEBOOK_ID": notebook_id,
            "TREEBEARD_RUN_ID": run_id,
        },
        detach=True,
    )

    [click.echo(line, nl=False) for line in container.logs(stream=True)]

    result = container.wait()
    return int(result["StatusCode"])
