import os
import subprocess
import sys
from pathlib import Path
from traceback import format_exc
from typing import Any, Optional

import click
import docker  # type: ignore
import requests
from docker.errors import ImageNotFound  # type: ignore

from treebeard.buildtime.helper import run_image
from treebeard.conf import run_path, treebeard_config, treebeard_env
from treebeard.helper import sanitise_notebook_id
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
) -> int:
    click.echo(f"🌲 Treebeard buildtime, building repo")
    click.echo(f"Run path: {run_path}")

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

        try:
            subprocess.check_output(
                ["nbstripout"] + treebeard_config.deglobbed_notebooks
            )
        except:
            fatal_exit(
                f"Failed to nbstripout a notebook! Do you have an invalid .ipynb?"
            )
    finally:
        click.echo("Treebeard Bundle Contents:")
        subprocess.run(["pwd"])
        subprocess.run(["ls", "-la", abs_notebook_dir])

    # Pull down images to use in cache
    image_name = f"gcr.io/treebeard-259315/projects/{project_id}/{sanitise_notebook_id(notebook_id)}"
    # our "base" image is just a routine repo2docker build which can be used for caching
    project_base_image = "docker.io/treebeardtech/project-base-image"

    try:
        click.echo(f"Pulling {image_name}")
        client.images.pull(image_name)
    except requests.exceptions.ConnectionError:
        fatal_exit("Could not connect to Docker registry!")
    except ImageNotFound:
        try:
            click.echo(
                f"Could not pull {image_name}, instead pulling {project_base_image}"
            )
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

    try:
        subprocess.check_output(["bash", "-c", r2d])
    except:
        click.echo(f"\n\n❗ Failed to build container from the source repo")
        return 1

    if not local:
        try:
            click.echo(f"Image built: Pushing {versioned_image_name}")
            client.images.push(versioned_image_name)
        except Exception:
            click.echo(
                f"Failed to push image, will try again on success\n{format_exc()}"
            )

    click.echo(f"Image built successfully, now running.")
    status = run_image(project_id, notebook_id, run_id, versioned_image_name)
    if status != 0:
        click.echo("Image run failed, not updated :latest")
        return status

    subprocess.check_output(["docker", "tag", versioned_image_name, latest_image_name])
    click.echo(f"tagged {versioned_image_name} as {latest_image_name}")
    return 0


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

    status = run_repo(
        treebeard_env.project_id,
        treebeard_env.notebook_id,
        treebeard_env.run_id,
        build_tag,
        repo_url,
        secrets_url,
    )

    sys.exit(status)
