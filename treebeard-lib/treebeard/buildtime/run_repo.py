import os
import subprocess
import sys
from pathlib import Path
from traceback import format_exc
from typing import Any, Optional

import click
import docker  # type: ignore
from docker.errors import ImageNotFound, NotFound  # type: ignore

from treebeard.buildtime.helper import run_image
from treebeard.conf import get_treebeard_config, run_path, treebeard_env
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


def fetch_image_for_cache(client: Any, image_name: str):
    try:
        click.echo(f"Pulling {image_name}")
        client.images.pull(image_name)
    except:
        click.echo(f"Could not pull image for cache, continuing without.")


def run_repo(
    project_id: str,
    notebook_id: str,
    run_id: str,
    build_tag: str,
    repo_url: str,
    secrets_url: Optional[str],
    branch: str,
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

        notebook_files = get_treebeard_config().get_deglobbed_notebooks()
        if len(notebook_files) == 0:
            raise Exception(
                "No notebooks found to run. If you are using a treebeard.yaml file, check it is correct: https://treebeard.readthedocs.io/en/latest/project_config.html"
            )
        try:
            subprocess.check_output(["nbstripout"] + notebook_files)
        except:
            print(
                f"Failed to nbstripout a notebook! Do you have an invalid .ipynb?\nNotebooks: {notebook_files}"
            )
    finally:
        click.echo("Treebeard Bundle Contents:")
        subprocess.run(["pwd"])
        subprocess.run(["ls", "-la", abs_notebook_dir])

    # Pull down images to use in cache
    image_name = f"gcr.io/treebeard-259315/projects/{sanitise_notebook_id(project_id)}/{sanitise_notebook_id(notebook_id)}"

    # Build image but don't run
    versioned_image_name = f"{image_name}:{build_tag}"
    passing_image_name = f"{image_name}:{branch}"
    latest_image_name = f"{image_name}:{branch}-latest"

    if not local:
        fetch_image_for_cache(client, latest_image_name)

    user_name = "project_user"  # All images having the same home dir enables caching
    r2d = f"""
    repo2docker \
        --debug \
        --no-run \
        --user-name {user_name} \
        --user-id 1000 \
        --image-name {versioned_image_name} \
        --cache-from {latest_image_name} \
        --target-repo-dir {abs_notebook_dir} \
        {abs_notebook_dir}
    """

    try:
        subprocess.check_output(["bash", "-c", r2d])
        click.echo(f"✨  Successfully built {versioned_image_name}")
    except:
        click.echo(f"\n\n❗ Failed to build container from the source repo")
        return 1

    subprocess.check_output(["docker", "tag", versioned_image_name, latest_image_name])
    if not local:
        try:
            click.echo(
                f"Image built: Pushing {versioned_image_name} and {latest_image_name}"
            )
            client.images.push(versioned_image_name)
            client.images.push(latest_image_name)  # this tag is necessary for caching
        except Exception:
            click.echo(
                f"Failed to push image, will try again on success\n{format_exc()}"
            )

    click.echo(f"Image built successfully, now running.")
    status = run_image(project_id, notebook_id, run_id, versioned_image_name)
    if status != 0:
        click.echo(f"Image run failed, not updated {passing_image_name}")
        return status

    subprocess.check_output(["docker", "tag", versioned_image_name, passing_image_name])
    click.echo(f"tagged {versioned_image_name} as {passing_image_name}")
    return 0


if __name__ == "__main__":
    build_tag_key = "TREEBEARD_BUILD_TAG"
    repo_url_key = "TREEBEARD_REPO_URL"
    secrets_url_key = "TREEBEARD_SECRETS_URL"
    branch_key = "TREEBEARD_BRANCH"

    subprocess.run(["bash", "-c", "echo Building repo"])

    build_tag = os.getenv(build_tag_key)
    if not build_tag:
        fatal_exit(f"No build_tag provided inside {build_tag_key}")

    branch = os.getenv(branch_key)
    if not branch:
        fatal_exit(f"No branch provided inside {branch_key}")

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
        branch,
    )

    sys.exit(status)
