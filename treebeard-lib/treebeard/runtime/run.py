import os
import pprint
import subprocess
import sys
from traceback import format_exc
from typing import List
import papermill as pm  # type: ignore

from treebeard.conf import run_path, treebeard_config, treebeard_env
from treebeard.runtime.helper import log, upload_artifact

pp = pprint.PrettyPrinter(indent=2)

bucket_name = "treebeard-notebook-outputs"
global cancelled
cancelled = False


def save_artifacts():
    log(f"saving all artifacts")

    if treebeard_config is None:
        raise Exception("No Treebeard Config Present at runtime!")

    for notebook_path in treebeard_config.deglobbed_notebooks:
        notebook_upload_path = f"{run_path}/{notebook_path}"
        upload_artifact(notebook_path, notebook_upload_path)

    for output_dir in treebeard_config.output_dirs:
        for root, _, files in os.walk(output_dir, topdown=False):
            for name in files:
                full_name = os.path.join(root, name)
                upload_path = f"{run_path}/{full_name}"
                upload_artifact(full_name, upload_path)


def run(project_id: str, notebook_id: str, run_id: str) -> List[str]:
    log(f"🌲 treebeard runtime: running repo")
    subprocess.run(
        [
            "bash",
            "-c",
            """
            echo Running notebook in $(pwd)
            printenv
            ls -lah""",
        ]
    )

    if treebeard_config is None:
        raise Exception("No Treebeard Config Present at runtime!")

    for output_dir in treebeard_config.output_dirs:
        os.makedirs(output_dir, exist_ok=True)

    failed_notebooks = []

    for i, notebook_path in enumerate(treebeard_config.deglobbed_notebooks):
        print(
            f"Running {i}/{len(treebeard_config.deglobbed_notebooks)}: {notebook_path}"
        )
        try:
            notebook_dir, notebook_name = os.path.split(notebook_path)
            log(f"Executing Notebook {notebook_name} in {notebook_dir}")
            pm.execute_notebook(  # type: ignore
                notebook_path,
                notebook_path,
                progress_bar=False,
                request_save_on_cell_execute=True,
                autosave_cell_every=10,
                kernel_name="python3",
                log_output=True,
                cwd=f"{os.getcwd()}/{notebook_dir}",
            )
        except Exception:
            failed_notebooks.append(notebook_path)
            tb = format_exc()
            print(f"Notebook {notebook_path} failed!\n{tb}")

    save_artifacts()
    log("Finished")

    return failed_notebooks


if __name__ == "__main__":
    if not treebeard_env.notebook_id:
        raise Exception("No notebook ID at runtime")
    if not treebeard_env.project_id:
        raise Exception("No project ID at buildtime")

    failed_notebooks = run(
        treebeard_env.project_id, treebeard_env.notebook_id, treebeard_env.run_id
    )

    if len(failed_notebooks) > 0:
        print(f"One or more notebooks failed: {pp.pformat(failed_notebooks)}")
        sys.exit(1)
