import os
from typing import Any, Dict, List

import click
import docker  # type: ignore

from treebeard.conf import treebeard_config, treebeard_env


def run_image(
    user_name: str,
    repo_short_name: str,
    run_id: str,
    image_name: str,
    envs_to_forward: List[str],
    upload: bool,
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

    if "GITHUB_REF" in os.environ:
        env["GITHUB_REF"] = os.environ["GITHUB_REF"]
    if "GITHUB_SHA" in os.environ:
        env["GITHUB_SHA"] = os.environ["GITHUB_SHA"]
    if "GITHUB_EVENT_NAME" in os.environ:
        env["GITHUB_EVENT_NAME"] = os.environ["GITHUB_EVENT_NAME"]
    if "GITHUB_WORKFLOW" in os.environ:
        env["GITHUB_WORKFLOW"] = os.environ["GITHUB_WORKFLOW"]

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
        f"bash -cxeuo pipefail '({pip_treebeard} > /dev/null 2>&1) && treebeard run {debug} --dockerless {upload_flag} --confirm'",
        environment=env,
        detach=True,
    )

    [click.echo(line, nl=False) for line in container.logs(stream=True)]

    result = container.wait()
    return int(result["StatusCode"])


def create_start_script():
    script = f"""
#!/usr/bin/env bash
set -xeuo pipefail

echo Running treebeard/post_install.ipynb
pip install -U "git+https://github.com/treebeardtech/treebeard.git@{treebeard_config.treebeard_ref}#subdirectory=treebeard-lib" > /dev/null 2>&1

papermill \\
  --stdout-file /dev/stdout \\
  --stderr-file /dev/stderr \\
  --kernel python3 \\
  --no-progress-bar \\
  treebeard/post_install.ipynb \\
  treebeard/post_install.ipynb \\
"""

    with open("start", "w") as start:
        start.write(script)


def create_post_build_script():
    script = f"""
#!/usr/bin/env bash
set -xeuo pipefail

echo Running treebeard/post_install.ipynb
pip install -U "git+https://github.com/treebeardtech/treebeard.git@{treebeard_config.treebeard_ref}#subdirectory=treebeard-lib" > /dev/null 2>&1

papermill \\
  --stdout-file /dev/stdout \\
  --stderr-file /dev/stderr \\
  --kernel python3 \\
  --no-progress-bar \\
  treebeard/post_install.ipynb \\
  treebeard/post_install.ipynb \\

"""

    with open("postBuild", "w") as post_build:
        post_build.write(script)
