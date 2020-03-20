import os
import subprocess
from glob import glob
from pathlib import Path
from typing import Any, Optional

import click
import docker  # type: ignore
from docker.errors import ImageNotFound  # type: ignore

from treebeard.buildtime.helper import run_image
from treebeard.conf import treebeard_env
from treebeard.util import fatal_exit


def download_archive(unzip_location: str, download_location: str, url: str):
    subprocess.check_output(
        [
            "bash",
            "-c",
            f'curl -o {download_location} "{url}" && tar -C {unzip_location} -xvf {download_location}',
        ]
    )
    # rm {download_location}""",


def run_repo(
    project_id: str,
    notebook_id: str,
    run_id: str,
    build_tag: str,
    repo_url: str,
    secrets_url: Optional[str],
    local: bool = False,
):
    client: Any = docker.from_env()  # type: ignore

    try:
        # Create bundle directory
        abs_notebook_dir = f"/tmp/{notebook_id}"
        Path(abs_notebook_dir).mkdir(parents=True, exist_ok=True)
        os.chdir(abs_notebook_dir)

        # Add repo to bundle
        download_archive(abs_notebook_dir, f"/tmp/{notebook_id}_repo.tgz", repo_url)

        if secrets_url:
            download_archive(
                abs_notebook_dir, f"/tmp/{notebook_id}_secrets.tgz", secrets_url
            )

        subprocess.check_output(["nbstripout"] + glob("./*.ipynb"))
    finally:
        click.echo("Treebeard Bundle Contents:")
        subprocess.run(["pwd"])
        subprocess.run(["ls", "-la", abs_notebook_dir])

    # Pull down images to use in cache
    image_name = f"gcr.io/treebeard-259315/projects/{project_id}/{notebook_id}"
    # our "base" image is just a routine repo2docker build which can be used for caching
    project_base_image = "docker.io/treebeardtech/project-base-image"

    try:
        client.images.pull(image_name)
    except ImageNotFound:
        try:
            client.images.pull(project_base_image)
        except Exception as ex:
            click.echo(f"Error pulling project base image {ex}, continuing without...")

    # Build image but don't run
    versioned_image_name = f"{image_name}:{build_tag}"
    latest_image_name = f"{image_name}:latest"

    user_name = "project_user"  # All images having the same home dir enables caching
    r2d = f"""
    repo2docker \
        --debug \
        --no-run \
        --user-name {user_name} \
        --user-id 1000 \
        --image-name {versioned_image_name} \
        --cache-from {latest_image_name} \
        --cache-from {project_base_image} \
        --target-repo-dir {abs_notebook_dir} \
        {abs_notebook_dir}
    """
    subprocess.check_output(["bash", "-c", r2d])
    subprocess.check_output(["docker", "tag", versioned_image_name, latest_image_name])

    try:
        run_image(project_id, notebook_id, run_id, image_name)
    except Exception as ex:
        if not local:
            click.echo("Image run failed, pushing failed image...")
            client.images.push(latest_image_name)
        raise ex


if __name__ == "__main__":
    build_tag_key = "TREEBEARD_BUILD_TAG"
    repo_url_key = "TREEBEARD_REPO_URL"
    secrets_url_key = "TREEBEARD_SECRETS_URL"

    subprocess.run(["bash", "-c", "echo Building repo"])

    build_tag = os.getenv(build_tag_key)
    if not build_tag:
        fatal_exit(f"No build_tag provided inside {build_tag_key}")

    repo_url = os.getenv(repo_url_key)
    if not repo_url:
        fatal_exit(f"No repo_url provided inside {repo_url_key}")

    secrets_url = os.getenv(secrets_url_key)
    if not treebeard_env.notebook_id:
        raise Exception("No notebook ID at runtime")
    if not treebeard_env.project_id:
        raise Exception("No project ID at buildtime")

    run_repo(
        treebeard_env.project_id,
        treebeard_env.notebook_id,
        treebeard_env.run_id,
        build_tag,
        repo_url,
        secrets_url,
    )
