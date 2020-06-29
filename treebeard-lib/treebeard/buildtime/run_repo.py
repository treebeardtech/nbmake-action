import os
import subprocess
from pathlib import Path
from traceback import format_exc
from typing import Any, List

import click
import docker  # type: ignore
from docker.errors import ImageNotFound, NotFound  # type: ignore
from repo2docker.utils import is_valid_docker_image_name  # type:ignore

from treebeard.buildtime.helper import (
    create_post_build_script,
    create_start_script,
    run_image,
)
from treebeard.conf import get_treebeard_config, run_path
from treebeard.helper import sanitise_repo_short_name, update
from treebeard.runtime.run import upload_meta_nbs
from treebeard.util import fatal_exit


def download_archive(unzip_location: str, download_location: str, url: str):
    subprocess.check_output(
        [
            "bash",
            "-c",
            f'curl -o {download_location} "{url}" >/dev/null 2>&1 && tar -C {unzip_location} -xvf {download_location} >/dev/null 2>&1',
        ],
    )


def fetch_image_for_cache(client: Any, image_name: str):
    try:
        click.echo(f"🐳 Pulling {image_name}")
        client.images.pull(image_name)
    except Exception:
        click.echo(f"Could not pull image for cache, continuing without.")


def run_repo(
    user_name: str,
    repo_short_name: str,
    run_id: str,
    build_tag: str,
    repo_url: str,
    branch: str,
    envs_to_forward: List[str],
    upload: bool,
) -> int:
    click.echo(f"🌲 Treebeard buildtime, building repo")
    click.echo(f"Run path: {run_path}")

    click.echo(f" Running repo setup")
    repo_setup_nb = "treebeard/repo_setup.ipynb"
    if os.path.exists(repo_setup_nb):
        try:
            subprocess.check_output(
                f"""
                papermill \
                    --stdout-file /dev/stdout \
                    --stderr-file /dev/stdout \
                    --kernel python3 \
                    --no-progress-bar \
                    {repo_setup_nb} \
                    {repo_setup_nb} \

                """,
                shell=True,
            )
        except Exception:
            if upload:
                upload_meta_nbs()
                update("FAILURE")
                return 2
            else:
                return 1

    client: Any = docker.from_env()  # type: ignore

    default_image_name = f"{sanitise_repo_short_name(user_name)}/{sanitise_repo_short_name(repo_short_name)}"
    image_name = default_image_name
    if "TREEBEARD_IMAGE_NAME" in os.environ:
        image_name = os.environ["TREEBEARD_IMAGE_NAME"]
    elif "DOCKER_REGISTRY_PREFIX" in os.environ:
        image_name = f"{os.environ['DOCKER_REGISTRY_PREFIX']}/{default_image_name}"

    assert image_name is not None
    click.echo(f"🐳 Building {image_name}")
    use_docker_registry = (
        "TREEBEARD_IMAGE_NAME" in os.environ
        or "DOCKER_REGISTRY_PREFIX" in os.environ
        or (os.getenv("DOCKER_USERNAME") and os.getenv("DOCKER_PASSWORD"))
    )

    if use_docker_registry and not is_valid_docker_image_name(image_name):
        fatal_exit(
            "🐳❌ the docker image name you supplied is invalid. It must be lower case, alphanumeric, with only - and _ special chars."
        )

    if os.getenv("DOCKER_USERNAME") and os.getenv("DOCKER_PASSWORD"):
        click.echo(
            f"🐳 Logging into DockerHub using the username and password you provided"
        )
        subprocess.check_output(
            f"printenv DOCKER_PASSWORD | docker login -u {os.getenv('DOCKER_USERNAME')} --password-stdin",
            shell=True,
        )

    try:
        # Create bundle directory
        abs_notebook_dir = f"/tmp/{repo_short_name}"
        Path(abs_notebook_dir).mkdir(parents=True, exist_ok=True)
        os.chdir(abs_notebook_dir)

        # Add repo to bundle
        download_archive(abs_notebook_dir, f"/tmp/{repo_short_name}_repo.tgz", repo_url)

        if os.path.exists("treebeard/container_setup.ipynb"):
            create_start_script()

        if os.path.exists("treebeard/post_install.ipynb"):
            create_post_build_script()

        notebook_files = get_treebeard_config().get_deglobbed_notebooks()
        if len(notebook_files) == 0:
            raise Exception(
                "No notebooks found to run. If you are using a treebeard.yaml file, check it is correct: https://treebeard.readthedocs.io/en/latest/project_config.html"
            )
        try:
            subprocess.check_output(["nbstripout"] + notebook_files)
        except:
            print(
                f"❗Failed to nbstripout a notebook! Do you have an invalid .ipynb?\nNotebooks: {notebook_files}"
            )
    finally:
        click.echo("Treebeard Bundle Contents:")
        subprocess.run(["pwd"])
        subprocess.run(["ls", "-la", abs_notebook_dir])

    # Pull down images to use in cache

    # Build image but don't run
    versioned_image_name = f"{image_name}:{build_tag}"
    passing_image_name = f"{image_name}:{branch}"
    latest_image_name = f"{image_name}:{branch}-latest"

    fetch_image_for_cache(client, latest_image_name)

    r2d = f"""
    repo2docker \
        --no-run \
        --user-name {user_name} \
        --user-id 1000 \
        --image-name {versioned_image_name} \
        --cache-from {latest_image_name} \
        {abs_notebook_dir}
    """

    try:
        subprocess.check_output(["bash", "-c", r2d])
        click.echo(f"✨  Successfully built {versioned_image_name}")
    except:
        click.echo(f"\n\n❗ Failed to build container from the source repo")
        if upload:
            upload_meta_nbs()
            update("FAILURE")
            return 2
        else:
            return 1

    subprocess.check_output(["docker", "tag", versioned_image_name, latest_image_name])

    if use_docker_registry:
        try:
            click.echo(f"🐳 Pushing {versioned_image_name} and {latest_image_name}\n")
            subprocess.check_output(f"docker push {versioned_image_name}", shell=True)
            subprocess.check_output(
                f"docker push {latest_image_name}", shell=True
            )  # this tag is necessary for caching
        except Exception:
            click.echo(
                f"🐳❌ Failed to push image, will try again on success\n{format_exc()}"
            )
    else:
        click.echo(f"🐳 Not pushing docker image as no registry is configured.")

    click.echo(f"Image built successfully, now running.")
    status = run_image(
        user_name,
        repo_short_name,
        run_id,
        versioned_image_name,
        envs_to_forward,
        upload,
    )
    if status != 0:
        click.echo(f"Image run failed, not updated {passing_image_name}")
        return status

    subprocess.check_output(["docker", "tag", versioned_image_name, passing_image_name])
    click.echo(f"🐳 tagged {versioned_image_name} as {passing_image_name}")

    if use_docker_registry:
        subprocess.check_output(f"docker push {passing_image_name}", shell=True)

    return 0
