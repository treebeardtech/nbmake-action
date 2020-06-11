import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Dict

import click
import papermill as pm  # type: ignore
from sentry_sdk import capture_exception, capture_message  # type: ignore

from treebeard.conf import run_path, treebeard_config, treebeard_env
from treebeard.importchecker.imports import check_imports
from treebeard.logs import log as tb_log
from treebeard.logs.helpers import clean_log_file
from treebeard.runtime.helper import (
    NotebookResult,
    get_failed_nb_details,
    get_health_bar,
    get_summary,
    log,
    upload_artifact,
)

bucket_name = "treebeard-notebook-outputs"

notebook_files = treebeard_config.get_deglobbed_notebooks()

notebook_status_descriptions = {
    "✅": "SUCCESS",
    "⏳": "WORKING",
    "💥": "FAILURE",
    "⏰": "TIMEOUT",
}


def save_artifacts(notebook_results: Dict[str, NotebookResult]):
    with ThreadPoolExecutor(max_workers=4) as executor:
        log(f"Uploading outputs...")

        if treebeard_config is None:
            raise Exception("No Treebeard Config Present at runtime!")

        notebooks_files = treebeard_config.get_deglobbed_notebooks()
        first = True
        for notebook_path in notebooks_files:
            notebook_upload_path = f"{run_path}/{notebook_path}"
            executor.submit(
                upload_artifact,
                notebook_path,
                notebook_upload_path,
                notebook_status_descriptions[notebook_results[notebook_path].status],
                set_as_thumbnail=first,
            )
            first = False

        for output_dir in treebeard_config.output_dirs:
            for root, _, files in os.walk(output_dir, topdown=False):
                for name in files:
                    full_name = os.path.join(root, name)
                    upload_path = f"{run_path}/{full_name}"
                    executor.submit(upload_artifact, full_name, upload_path, None)


def run_notebook(notebook_path: str) -> NotebookResult:
    def get_nb_dict():
        with open(notebook_path) as json_file:
            return json.load(json_file)

    try:
        notebook_dir, notebook_name = os.path.split(notebook_path)
        log(
            f"Executing Notebook {notebook_name} in {'.' if len(notebook_dir) == 0 else notebook_dir}"
        )
        pm.execute_notebook(  # type: ignore
            notebook_path,
            notebook_path,
            kernel_name=treebeard_config.kernel_name,
            progress_bar=False,
            request_save_on_cell_execute=True,
            autosave_cell_every=10,
            execution_timeout=treebeard_config.cell_execution_timeout_seconds,
            log_output=True,
            cwd=f"{os.getcwd()}/{notebook_dir}",
        )
        log(f"✅ Notebook {notebook_path} passed!\n")
        nb_dict = get_nb_dict()
        num_cells = len(nb_dict["cells"])
        return NotebookResult(
            status="✅", num_cells=num_cells, num_passing_cells=num_cells, err_line=""
        )
    except Exception:
        tb = format_exc()
        nb_dict = get_nb_dict()
        num_cells = len(nb_dict["cells"])
        err_line, num_passing_cells, status = get_failed_nb_details(nb_dict)

        log(
            f"""{status} Notebook {notebook_path} failed!\n  {num_passing_cells}/{num_cells} cells ran.\n\n{tb}"""
        )

        return NotebookResult(
            status=status,
            num_cells=num_cells,
            num_passing_cells=num_passing_cells,
            err_line=err_line,
        )


def _run(project_id: str, notebook_id: str, run_id: str) -> Dict[str, NotebookResult]:
    log(f"🌲 treebeard runtime: running repo")
    subprocess.run(
        [
            "bash",
            "-c",
            """
            echo "working directory is $(pwd)\n\n$(ls -la)\n"
            """,
        ]
    )

    if treebeard_config is None:
        raise Exception("No Treebeard Config Present at runtime!")

    for output_dir in treebeard_config.output_dirs:
        os.makedirs(output_dir, exist_ok=True)

    notebook_results = {
        notebook: NotebookResult(
            status="⏳", num_cells=1, num_passing_cells=1, err_line=""
        )
        for notebook in notebook_files
    }
    print(f"Will run the following:")
    [print(nb) for nb in notebook_files]
    print()

    for i, notebook_path in enumerate(notebook_files):
        log(f"⏳ Running {i + 1}/{len(notebook_files)}: {notebook_path}")
        notebook_results[notebook_path] = run_notebook(notebook_path)

    return notebook_results


def finish(status: int = 0):
    if os.path.exists("treebeard.log"):
        upload_artifact("treebeard.log", f"{run_path}/treebeard.log", None)
    sys.exit(status)


def start(upload_outputs: bool = True):
    if not treebeard_env.notebook_id:
        raise Exception("No notebook ID at runtime")
    if not treebeard_env.project_id:
        raise Exception("No project ID at buildtime")

    clean_log_file()

    notebook_results = _run(
        treebeard_env.project_id, treebeard_env.notebook_id, treebeard_env.run_id
    )

    if upload_outputs:
        save_artifacts(notebook_results)

    log("🌲 Run Finished. Results:\n")

    for notebook in notebook_results.keys():
        result = notebook_results[notebook]
        health_bar = get_health_bar(
            result.num_passing_cells, result.num_cells, result.status
        )

        if result.status == "✅":
            print(f"{health_bar} {notebook}")
            print(f"  ran {result.num_passing_cells} of {result.num_cells} cells")
        elif not result.err_line:  # failed to parse notebook properly
            print(f"{result.status} {notebook}")
        else:
            print(f"{health_bar} {notebook}")
            print(f"  ran {result.num_passing_cells} of {result.num_cells} cells")
            print(f"  {result.status} {result.err_line}")

        print()

    n_passed = len(list(filter(lambda v: v.status == "✅", notebook_results.values())))

    total_nbs = len(notebook_results)
    if n_passed < total_nbs:
        summary_block = get_summary(notebook_results, n_passed, total_nbs)
        tb_log(summary_block)

        try:
            if treebeard_config.kernel_name == "python3":
                result = check_imports()

                if treebeard_config.strict_mode:
                    click.echo(
                        f"\nℹ️ If you would like to ignore notebook run failures and only fail on missing dependencies, add `strict_mode: False` to a `treebeard.yaml` file"
                    )
                else:
                    if result:
                        click.echo(
                            f"\nℹ️ Strict mode is disabled and import checker passed, run is successful! ✅"
                        )
                        finish(0)
                    else:
                        click.echo(
                            f"\nℹ️ Strict mode is disabled! Fix missing dependencies to get a passing run."
                        )
                click.echo()
        except Exception as ex:
            click.echo(f"Import checker encountered and error...")
            capture_exception(ex)
        finish(1)
    else:
        finish(0)


if __name__ == "__main__":
    start()
