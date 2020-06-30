import json
import os
import subprocess
from typing import Any, Dict, List, Optional

import click
import docker  # type: ignore

from treebeard.conf import GitHubDetails, treebeard_config, treebeard_env


def run_image(
    user_name: str,
    repo_short_name: str,
    run_id: str,
    image_name: str,
    envs_to_forward: List[str],
    upload: bool,
    github_details: Optional[GitHubDetails],
) -> int:
    client: Any = docker.from_env()  # type: ignore

    pip_treebeard = f"pip install -U git+https://github.com/treebeardtech/treebeard.git@{treebeard_config.treebeard_ref}#subdirectory=treebeard-lib"

    env: Dict[str, str] = {
        "TREEBEARD_USER_NAME": user_name,
        "TREEBEARD_REPO_SHORT_NAME": repo_short_name,
        "TREEBEARD_START_TIME": os.environ["TREEBEARD_START_TIME"],
        "TREEBEARD_RUN_ID": os.environ["TREEBEARD_RUN_ID"],
    }

    if treebeard_env.api_key:
        env["TREEBEARD_API_KEY"] = treebeard_env.api_key

    if github_details:
        env["TREEBEARD_GITHUB_DETAILS"] = json.dumps(github_details.dict())

    if "CI" in os.environ:
        env["CI"] = os.environ["CI"]

    for e in envs_to_forward:
        var = os.getenv(e)
        if var:
            env[e] = var
        else:
            click.secho(  # type:ignore
                f"Warning: {e} is unset so cannot be forwarded to container",
                fg="yellow",
            )

    if treebeard_config.debug:
        click.echo(f"Starting container: {pip_treebeard}\nEnvironment: {env.keys()}")

    upload_flag = "--upload" if upload else "--no-upload"
    debug = " --debug " if treebeard_config.debug else " "
    container = client.containers.run(
        image_name,
        f"bash -cxeu '({pip_treebeard} > /dev/null 2>&1) && treebeard run {debug} --dockerless {upload_flag} --confirm'",
        environment=env,
        detach=True,
    )

    [click.echo(line, nl=False) for line in container.logs(stream=True)]

    result = container.wait()
    return int(result["StatusCode"])


def create_start_script():
    notebook = "treebeard/container_setup.ipynb"
    script = f"""
#!/usr/bin/env bash
set -xeu

echo Running {notebook}
pip install -U "git+https://github.com/treebeardtech/treebeard.git@{treebeard_config.treebeard_ref}#subdirectory=treebeard-lib" > /dev/null 2>&1

papermill \\
  --stdout-file /dev/stdout \\
  --stderr-file /dev/stderr \\
  --kernel python3 \\
  --no-progress-bar \\
  {notebook} \\
  {notebook} \\

exec "$@"
"""

    with open("start", "w") as start:
        start.write(script)


def create_post_build_script():
    notebook = "treebeard/post_install.ipynb"
    script = f"""
#!/usr/bin/env bash
set -xeu

echo Running {notebook}
pip install -U "git+https://github.com/treebeardtech/treebeard.git@{treebeard_config.treebeard_ref}#subdirectory=treebeard-lib" > /dev/null 2>&1

papermill \\
  --stdout-file /dev/stdout \\
  --stderr-file /dev/stderr \\
  --kernel python3 \\
  --no-progress-bar \\
  {notebook} \\
  {notebook} \\

"""

    with open("postBuild", "w") as post_build:
        post_build.write(script)


def fetch_image_for_cache(client: Any, image_name: str):
    try:
        click.echo(f"🐳 Pulling {image_name}")
        client.images.pull(image_name)
    except Exception:
        click.echo(f"Could not pull image for cache, continuing without.")


def push_image(image_name: str):
    click.echo(f"🐳 Pushing {image_name}\n")
    subprocess.check_output(f"docker push {image_name}", shell=True)


def tag_image(image_name: str, tagged_name: str):
    subprocess.check_output(["docker", "tag", image_name, tagged_name])
    click.echo(f"🐳 tagged {image_name} as {tagged_name}")


def run_repo2docker(
    user_name: str,
    r2d_user_id: str,
    versioned_image_name: str,
    latest_image_name: str,
    repo_temp_dir: str,
):
    r2d = f"""
    repo2docker \
        --no-run \
        --user-name {user_name} \
        --user-id {r2d_user_id} \
        --image-name {versioned_image_name} \
        --cache-from {latest_image_name} \
        {repo_temp_dir}
    """
    subprocess.check_output(["bash", "-c", r2d])
