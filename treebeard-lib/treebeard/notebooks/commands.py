import json
import os
import os.path
import pprint
import sys
import tempfile
from distutils.dir_util import copy_tree
from typing import List, Optional

import click
import yaml

from treebeard import conf
from treebeard.buildtime import build
from treebeard.conf import (
    GitHubDetails,
    TreebeardConfig,
    TreebeardContext,
    TreebeardEnv,
    api_url,
    validate_notebook_directory,
)
from treebeard.helper import CliContext, get_time, update
from treebeard.sentry_setup import setup_sentry

pp = pprint.PrettyPrinter(indent=2)


def create_github_details(use_docker: bool):
    run_id = os.getenv("GITHUB_RUN_ID")

    if not run_id:
        inside_r2d = not use_docker and os.getenv("TREEBEARD_GITHUB_DETAILS")
        if inside_r2d:
            return GitHubDetails(**json.loads(os.environ["TREEBEARD_GITHUB_DETAILS"]))
        return None

    sha = os.environ["GITHUB_SHA"]
    ref = os.environ["GITHUB_REF"]
    workflow = os.environ["GITHUB_WORKFLOW"]
    event_name = os.environ["GITHUB_EVENT_NAME"]
    event_path = os.environ["GITHUB_EVENT_PATH"]

    branch = ref.split("/")[-1]
    user_name = os.environ["GITHUB_REPOSITORY"].split("/")[0]
    repo_short_name = os.environ["GITHUB_REPOSITORY"].split("/")[1]

    return GitHubDetails(
        run_id=run_id,
        sha=sha,
        branch=branch,
        repo_short_name=repo_short_name,
        user_name=user_name,
        event_name=event_name,
        event_path=event_path,
        workflow=workflow,
    )


@click.command()
@click.option("-n", "--notebooks", help="Notebooks to be run", multiple=True)
@click.option(
    "-e", "--env", help="Environment variables to forward into container", multiple=True
)
@click.option(
    "-i",
    "--ignore",
    help="Don't submit unneeded virtual envs and large files",
    multiple=True,
)
@click.option(
    "--confirm/--no-confirm", default=False, help="Confirm all prompt options"
)
@click.option(
    "--use-docker/--no-use-docker",
    default=False,
    help="Run inside a repo2docker container",
)
@click.option(
    "--upload/--no-upload", default=False, help="Upload outputs",
)
@click.option(
    "--debug/--no-debug", default=False, help="Enable debug logging",
)
@click.option(
    "--usagelogging/--no-usagelogging",
    default=False,
    help="Send usage logs to treebeard",
)
@click.pass_obj  # type: ignore
def run(
    cli_context: CliContext,
    notebooks: List[str],
    env: List[str],
    ignore: List[str],
    confirm: bool,
    use_docker: bool,
    upload: bool,
    debug: bool,
    usagelogging: bool,
):

    github_details = create_github_details(use_docker)
    status = run_repo(
        notebooks,
        env,
        ignore,
        confirm,
        use_docker,
        upload,
        debug,
        usagelogging,
        github_details,
    )
    click.echo(f"Build exited with status code {status}")
    sys.exit(status)


def run_repo(
    notebooks: List[str] = [],
    env: List[str] = [],
    ignore: List[str] = [],
    confirm: bool = True,
    use_docker: bool = False,
    upload: bool = False,
    debug: bool = False,
    usagelogging: bool = False,
    github_details: Optional[GitHubDetails] = None,
    treebeard_env: Optional[TreebeardEnv] = None,
    treebeard_config: Optional[TreebeardConfig] = None,
) -> int:
    """
    Run a notebook and optionally schedule it to run periodically
    """
    notebooks = list(notebooks)
    ignore = list(ignore)

    if not treebeard_env:
        treebeard_env = conf.get_treebeard_env(github_details)
    if not treebeard_config:
        treebeard_config = conf.get_treebeard_config()

    treebeard_context = TreebeardContext(
        treebeard_env=treebeard_env,
        treebeard_config=treebeard_config,
        config_path=conf.get_config_path(),
        github_details=github_details,
    )

    if debug:
        click.echo(
            f"Treebeard context:\n{json.dumps(treebeard_context.dict(), sort_keys=True, indent=4)}"
        )

    setup_sentry(treebeard_context.treebeard_env)
    treebeard_config = treebeard_context.treebeard_config
    treebeard_config.debug = debug
    validate_notebook_directory(
        treebeard_context.treebeard_env, treebeard_context.treebeard_config, upload
    )

    # Apply cli config overrides
    if notebooks:
        treebeard_config.notebooks = notebooks

    if ignore:
        treebeard_config.ignore = ignore + treebeard_config.output_dirs

    if "TREEBEARD_START_TIME" not in os.environ:
        os.environ["TREEBEARD_START_TIME"] = get_time()

    if not use_docker:
        if upload:
            update(
                treebeard_context,
                status="WORKING",
                update_url=f"{api_url}/{treebeard_context.treebeard_env.run_path}/update",
            )
        click.echo(
            f"🌲  Running locally without docker using your current python environment"
        )
        if not confirm and not click.confirm(
            f"Warning: This will clear the outputs of your notebooks, continue?",
            default=True,
        ):
            sys.exit(1)

        # Note: import runtime.run causes win/darwin devices missing magic to fail at start
        import treebeard.runtime.run

        nbrun = treebeard.runtime.run.NotebookRun(treebeard_context)

        status = nbrun.start(upload=upload, logging=usagelogging)
        return status

    if upload:
        update(
            treebeard_context,
            status="BUILDING",
            update_url=f"{api_url}/{treebeard_context.treebeard_env.run_path}/update",
        )

    click.echo("🌲  Creating Project bundle")
    temp_dir = tempfile.mkdtemp()
    copy_tree(os.getcwd(), str(temp_dir), preserve_symlinks=1)

    # Overwrite config with in-memory-modified
    with open(f"{temp_dir}/treebeard.yaml", "w") as yaml_file:
        yaml.dump(treebeard_config.dict(), yaml_file)  # type: ignore

    return build.build(
        treebeard_context,
        temp_dir,
        envs_to_forward=env,
        upload=upload,
        usagelogging=usagelogging,
    )
