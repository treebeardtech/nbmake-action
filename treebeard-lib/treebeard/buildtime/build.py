import os
import shutil
import subprocess
from traceback import format_exc
from typing import Any, List

import click
import docker  # type: ignore
from docker.errors import ImageNotFound, NotFound  # type: ignore
from repo2docker.utils import is_valid_docker_image_name  # type:ignore

from treebeard import helper as tb_helper
from treebeard.buildtime import helper
from treebeard.conf import TreebeardContext, api_url, get_treebeard_config
from treebeard.util import fatal_exit


def build(
    treebeard_context: TreebeardContext,
    repo_temp_dir: str,
    envs_to_forward: List[str],
    upload: bool,
    usagelogging: bool,
) -> int:
    click.echo(f"🌲 Treebeard buildtime, building repo")
    click.echo(f" Running repo setup")
    repo_setup_nb = "treebeard/repo_setup.ipynb"
    treebeard_env = treebeard_context.treebeard_env

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
            if usagelogging:
                tb_helper.update(
                    treebeard_context,
                    update_url=f"{api_url}/{treebeard_env.run_path}/log",
                    status="FAILURE",
                )
            if upload:
                tb_helper.upload_meta_nbs(treebeard_context)
                tb_helper.update(
                    treebeard_context,
                    update_url=f"{api_url}/{treebeard_env.run_path}/update",
                    status="FAILURE",
                )
                return 2
            else:
                return 1

    client: Any = docker.from_env()  # type: ignore
    default_image_name = f"{tb_helper.sanitise_repo_short_name(treebeard_env.user_name)}/{tb_helper.sanitise_repo_short_name(treebeard_env.repo_short_name)}"
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

    treebeard_config = treebeard_context.treebeard_config
    workdir = os.getcwd()
    try:
        os.chdir(repo_temp_dir)

        if os.path.exists("treebeard/container_setup.ipynb"):
            helper.create_start_script(treebeard_config.treebeard_ref)

        if os.path.exists("treebeard/post_install.ipynb"):
            helper.create_post_build_script(treebeard_config.treebeard_ref)

        notebook_files = get_treebeard_config().get_deglobbed_notebooks()
        if len(notebook_files) == 0:
            raise Exception(
                f"No notebooks found to run (cwd {os.getcwd()}). If you are using a treebeard.yaml file, check it is correct: https://treebeard.readthedocs.io/en/latest/project_config.html"
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

    # Build image but don't run
    versioned_image_name = f"{image_name}:{treebeard_env.run_id}"
    passing_image_name = f"{image_name}:{treebeard_env.branch}"
    latest_image_name = f"{image_name}:{treebeard_env.branch}-latest"

    helper.fetch_image_for_cache(client, latest_image_name)

    r2d_user_id = "1000"
    try:
        helper.run_repo2docker(
            treebeard_env.user_name,
            r2d_user_id,
            versioned_image_name,
            latest_image_name,
            repo_temp_dir,
        )
        click.echo(f"✨  Successfully built {versioned_image_name}")
    except:
        click.echo(f"\n\n❗ Failed to build container from the source repo")
        if usagelogging:
            tb_helper.update(
                treebeard_context,
                update_url=f"{api_url}/{treebeard_env.run_path}/log",
                status="FAILURE",
            )
        if upload:
            tb_helper.upload_meta_nbs(treebeard_context)
            tb_helper.update(
                treebeard_context,
                update_url=f"{api_url}/{treebeard_env.run_path}/update",
                status="FAILURE",
            )
            return 2
        else:
            return 1
    finally:
        os.chdir(workdir)
        shutil.rmtree(repo_temp_dir)

    helper.tag_image(versioned_image_name, latest_image_name)

    if use_docker_registry:
        try:
            helper.push_image(versioned_image_name)
            helper.push_image(latest_image_name)
        except Exception:
            click.echo(
                f"🐳❌ Failed to push image, will try again on success\n{format_exc()}"
            )
    else:
        click.echo(f"🐳 Not pushing docker image as no registry is configured.")

    click.echo(f"Image built successfully, now running.")
    status = helper.run_image(
        versioned_image_name, envs_to_forward, upload, usagelogging, treebeard_context,
    )
    if status != 0:
        click.echo(f"Image run failed, not updated {passing_image_name}")
        return status

    helper.tag_image(versioned_image_name, passing_image_name)

    if use_docker_registry:
        helper.push_image(passing_image_name)

    return 0
