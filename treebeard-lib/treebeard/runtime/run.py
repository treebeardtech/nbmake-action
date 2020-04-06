import os
import subprocess
import sys
from traceback import format_exc
from typing import Dict

import papermill as pm  # type: ignore

from treebeard.conf import run_path, treebeard_config, treebeard_env
from treebeard.runtime.helper import log, upload_artifact

bucket_name = "treebeard-notebook-outputs"


def save_artifacts():
    log(f"Uploading outputs...")

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


def run_notebook(notebook_path: str) -> str:
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
        log(f"✅ Notebook {notebook_path} passed!\n")
        return "✅"
    except Exception:
        tb = format_exc()
        log(f"❌ Notebook {notebook_path} failed!\n\n{tb}")
        return "❌"


def run(project_id: str, notebook_id: str, run_id: str) -> Dict[str, str]:
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

    notebooks = treebeard_config.deglobbed_notebooks
    notebook_statuses = {notebook: "⏳" for notebook in notebooks}

    for i, notebook_path in enumerate(notebooks):
        log(f"⏳ Running {i + 1}/{len(notebooks)}: {notebook_path}")
        notebook_statuses[notebook_path] = run_notebook(notebook_path)

    save_artifacts()
    log("Run Finished\n")

    return notebook_statuses


def start():
    if not treebeard_env.notebook_id:
        raise Exception("No notebook ID at runtime")
    if not treebeard_env.project_id:
        raise Exception("No project ID at buildtime")

    notebook_statuses = run(
        treebeard_env.project_id, treebeard_env.notebook_id, treebeard_env.run_id
    )

    for notebook in notebook_statuses.keys():
        print(f"{notebook_statuses[notebook]} {notebook}")
    print()

    n_failed = len(list(filter(lambda v: v != "✅", notebook_statuses.values())))

    if n_failed > 0:
        log(f"{n_failed} of {len(notebook_statuses)} notebooks failed.")
        sys.exit(1)


if __name__ == "__main__":
    start()
