import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Dict, Optional

import click
import papermill as pm  # type: ignore
from sentry_sdk import capture_exception, capture_message  # type: ignore

from treebeard.conf import run_path, treebeard_config, treebeard_env
from treebeard.importchecker.imports import check_imports
from treebeard.logs.helpers import clean_log_file
from treebeard.runtime.helper import NotebookResult, log, upload_artifact

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

        if os.path.exists("treebeard.log"):
            executor.submit(
                upload_artifact, "treebeard.log", f"{run_path}/treebeard.log", None
            )


def run_notebook(notebook_path: str) -> NotebookResult:
    def get_nb_dict():
        with open(notebook_path) as json_file:
            return json.load(json_file)

    nb_dict = get_nb_dict()
    num_cells = len(nb_dict["cells"])

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
        return NotebookResult(
            status="✅", num_cells=num_cells, num_passing_cells=num_cells
        )
    except Exception:
        tb = format_exc()

        num_passing_cells: Optional[int] = 0
        err_line = None
        status = "💥"
        try:
            for cell in nb_dict["cells"]:
                if "outputs" in cell:
                    errors = [
                        output
                        for output in cell["outputs"]
                        if output["output_type"] == "error" or "ename" in output
                    ]
                    if errors:
                        err_line = errors[0]["traceback"][-1]
                        break

                    if (
                        "metadata" in cell
                        and "papermill" in cell["metadata"]
                        and "duration" in cell["metadata"]["papermill"]
                        and cell["metadata"]["papermill"]["duration"] == None
                    ):
                        num_passing_cells -= 1
                        print("timeout")
                        err_line = f"Cell timed out after {treebeard_config.cell_execution_timeout_seconds}s. You can set `cell_execution_timeout_seconds` in treebeard.yaml."
                        status = "⏰"
                        break

                    num_passing_cells += 1

        except Exception as ex:
            print(ex)
            num_passing_cells = None
            err_line = None
            capture_exception(ex)  # type: ignore

        if err_line and num_passing_cells:
            log(
                f"""{status} Notebook {notebook_path} failed!
  {num_passing_cells}/{num_cells} cells ran.
  {err_line}
  
{tb}"""
            )
        else:
            log(f"""{status} Notebook {notebook_path} failed!\n\n{tb}""")
            capture_message(f"Didn't find error for {notebook_path}")

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
        notebook: NotebookResult(status="⏳") for notebook in notebook_files
    }
    print(f"Will run the following:")
    [print(nb) for nb in notebook_files]
    print()

    for i, notebook_path in enumerate(notebook_files):
        log(f"⏳ Running {i + 1}/{len(notebook_files)}: {notebook_path}")
        notebook_results[notebook_path] = run_notebook(notebook_path)

    return notebook_results


def get_health_bar(passing: int, total: int, status: str):
    assert passing <= total
    bar_length = 10
    n_green = int(bar_length * float(passing) / float(total))
    n_red = bar_length - n_green
    if n_green == bar_length:
        return "🟩" * (bar_length - 1) + "✅"
    return ("🟩" * n_green) + status + ("⬜" * (n_red - 1))


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
        print(f"{health_bar} {notebook}")
        print(f"  ran {result.num_passing_cells} of {result.num_cells} cells")

        if result.status != "✅":
            print(f"  {result.status} {result.err_line}")

        print()

    n_passed = len(list(filter(lambda v: v.status == "✅", notebook_results.values())))

    total_nbs = len(notebook_results)
    if n_passed < len(notebook_results):
        nb_percent = int(float(n_passed) / float(total_nbs) * 100)
        print()
        print(f"Notebooks: {n_passed} of {total_nbs} passed ({nb_percent}%)")
        total_cells = sum(map(lambda res: res.num_cells, notebook_results.values()))
        total_cells_passed = sum(
            map(lambda res: res.num_passing_cells, notebook_results.values())
        )
        percent = int(100.0 * float(total_cells_passed) / float(total_cells))
        print(f"Cells: {total_cells_passed} of {total_cells} passed ({percent}%)")
        print()

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
                        sys.exit(0)
        except Exception as ex:
            click.echo(f"Import checker encountered and error...")
            capture_exception(ex)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    start()
