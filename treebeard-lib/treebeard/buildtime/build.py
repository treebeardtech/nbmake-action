import os
import shutil
import subprocess
from traceback import format_exc
from typing import Any, List

import click
import docker  # type: ignore
from docker.errors import ImageNotFound, NotFound  # type: ignore
from repo2docker.utils import is_valid_docker_image_name  # type:ignore

from treebeard.buildtime.helper import (
    create_post_build_script,
    create_start_script,
    fetch_image_for_cache,
    push_image,
    run_image,
    run_repo2docker,
    tag_image,
)
from treebeard.conf import get_treebeard_config, run_path
from treebeard.helper import sanitise_repo_short_name, update
from treebeard.runtime.run import upload_meta_nbs
from treebeard.util import fatal_exit


def build(
    user_name: str,
    repo_short_name: str,
    run_id: str,
    build_tag: str,
    repo_temp_dir: str,
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
        os.chdir(repo_temp_dir)

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
        subprocess.run(["ls", "-la", repo_temp_dir])

    # Pull down images to use in cache

    # Build image but don't run
    versioned_image_name = f"{image_name}:{build_tag}"
    passing_image_name = f"{image_name}:{branch}"
    latest_image_name = f"{image_name}:{branch}-latest"

    fetch_image_for_cache(client, latest_image_name)

    r2d_user_id = "1000"
    try:
        run_repo2docker(
            user_name,
            r2d_user_id,
            versioned_image_name,
            latest_image_name,
            repo_temp_dir,
        )
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
            push_image(versioned_image_name)
            push_image(latest_image_name)
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

    tag_image(versioned_image_name, passing_image_name)

    if use_docker_registry:
        push_image(passing_image_name)

    os.chdir(os.environ["HOME"])
    shutil.rmtree(repo_temp_dir)
    return 0
