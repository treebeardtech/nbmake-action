import os
import sys
from typing import Any

import docker  # type: ignore

from treebeard.buildtime.helper import run_image
from treebeard.conf import treebeard_env
from treebeard.util import fatal_exit


def run(project_id: str, notebook_id: str, run_id: str, image_name: str) -> int:
    client: Any = docker.from_env()  # type: ignore
    client.images.pull(image_name)
    return run_image(project_id, notebook_id, run_id, image_name)


if __name__ == "__main__":
    if not treebeard_env.notebook_id:
        raise Exception("No notebook ID at buildtime")
    if not treebeard_env.project_id:
        raise Exception("No project ID at buildtime")

    image_name_key = "TREEBEARD_IMAGE_NAME"
    image_name = os.getenv(image_name_key)
    if not image_name:
        fatal_exit(f"No image supplied under {image_name_key}")
    sys.exit(
        run(
            treebeard_env.project_id,
            treebeard_env.notebook_id,
            treebeard_env.run_id,
            image_name,
        )
    )
