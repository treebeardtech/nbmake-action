import os
import subprocess
import threading
from shutil import move
from typing import Callable

import papermill as pm  # type: ignore

from treebeard.conf import run_path, treebeard_config, treebeard_env
from treebeard.runtime.helper import log, upload_artifact

bucket_name = "treebeard-notebook-outputs"
output_notebook_local_path = "/tmp/out.ipynb"
global cancelled
cancelled = False


def set_interval(func: Callable, sec: int):
    def func_wrapper():
        if cancelled:
            return
        func()
        set_interval(func, sec)

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def cancel_interval():
    log("Cancelling Interval")
    global cancelled
    cancelled = True


def save_artifacts():
    log(f"saving all artifacts")

    if treebeard_config is None:
        raise Exception("No Treebeard Config Present at runtime!")

    notebook_upload_path = f"{run_path}/out.ipynb"
    if os.path.exists(output_notebook_local_path):
        log(f"Saving {output_notebook_local_path} to {notebook_upload_path}")
        upload_artifact(notebook_upload_path, output_notebook_local_path)
    else:
        log("No output notebook to save")

    for output_dir in treebeard_config.output_dirs:
        for root, _, files in os.walk(output_dir, topdown=False):
            for name in files:
                full_name = os.path.join(root, name)
                upload_path = f"{run_path}/{full_name}"
                upload_artifact(upload_path, full_name)


def run(project_id: str, notebook_id: str, run_id: str):
    move(".treebeard", "/home/project_user/.treebeard")  # this may not be needed now...
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

    set_interval(save_artifacts, 10)
    try:
        path, notebook_name = os.path.split(treebeard_config.notebook)
        log(f"Executing Notebook {notebook_name} in {path}")
        if len(path) > 0:
            os.chdir(path)
        pm.execute_notebook(  # type: ignore
            notebook_name,
            output_notebook_local_path,
            progress_bar=False,
            request_save_on_cell_execute=True,
            autosave_cell_every=10,
            kernel_name="python3",
            log_output=True,
        )
    except Exception as ex:
        print(f"Run failed!")
        raise ex
    finally:
        cancel_interval()
        save_artifacts()
        log("Finished")


if __name__ == "__main__":
    if not treebeard_env.notebook_id:
        raise Exception("No notebook ID at runtime")
    if not treebeard_env.project_id:
        raise Exception("No project ID at buildtime")

    run(treebeard_env.project_id, treebeard_env.notebook_id, treebeard_env.run_id)
