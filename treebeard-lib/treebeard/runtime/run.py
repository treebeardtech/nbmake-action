import json
import os
import subprocess
from traceback import format_exc
from typing import Dict, List

import click
import papermill as pm  # type: ignore
from sentry_sdk import capture_exception, capture_message  # type: ignore

from treebeard import helper
from treebeard.conf import (
    TreebeardConfig,
    TreebeardContext,
    TreebeardEnv,
    api_url,
)
from treebeard.importchecker.imports import check_imports
from treebeard.logs import log as tb_log
from treebeard.logs.helpers import clean_log_file
from treebeard.runtime.helper import (
    NotebookResult,
    get_failed_nb_details,
    get_health_bar,
    get_summary,
)

bucket_name = "treebeard-notebook-outputs"


status_emojis = {
    "SUCCESS": "✅",
    "WORKING": "⏳",
    "FAILURE": "💥",
    "TIMEOUT": "⏰",
}


class NotebookRun:
    _treebeard_context: TreebeardContext
    _treebeard_config: TreebeardConfig
    _treebeard_env: TreebeardEnv
    _run_path: str

    def __init__(self, treebeard_context: TreebeardContext) -> None:
        self._treebeard_context = treebeard_context
        self._treebeard_config = treebeard_context.treebeard_config
        self._treebeard_env = treebeard_context.treebeard_env
        self._run_path = self._treebeard_env.run_path

    def upload_nb(self, notebook_path: str, nb_status: str, set_as_thumbnail: bool):
        notebook_upload_path = f"{self._run_path}/{notebook_path}"

        helper.upload_artifact(
            self._treebeard_context,
            notebook_path,
            notebook_upload_path,
            nb_status,
            set_as_thumbnail=set_as_thumbnail,
        )

    def upload_outputs(self):
        for output_dir in self._treebeard_config.output_dirs:
            for root, _, files in os.walk(output_dir, topdown=False):
                for name in files:
                    full_name = os.path.join(root, name)
                    upload_path = f"{self._run_path}/{full_name}"
                    helper.upload_artifact(
                        self._treebeard_context, full_name, upload_path, None
                    )

    def run_notebook(self, notebook_path: str) -> NotebookResult:
        def get_nb_dict():
            with open(notebook_path) as json_file:
                return json.load(json_file)

        try:
            notebook_dir, notebook_name = os.path.split(notebook_path)
            helper.log(
                f"Executing Notebook {notebook_name} in {'.' if len(notebook_dir) == 0 else notebook_dir}"
            )
            pm.execute_notebook(  # type: ignore
                notebook_path,
                notebook_path,
                kernel_name=self._treebeard_config.kernel_name,
                progress_bar=False,
                request_save_on_cell_execute=True,
                autosave_cell_every=10,
                execution_timeout=self._treebeard_config.cell_execution_timeout_seconds,
                log_output=True,
                nest_asyncio=True,  #  https://github.com/nteract/papermill/issues/490
                cwd=f"{os.getcwd()}/{notebook_dir}",
            )
            helper.log(f"{status_emojis['SUCCESS']} Notebook {notebook_path} passed!\n")
            nb_dict = get_nb_dict()
            num_cells = len(nb_dict["cells"])
            return NotebookResult(
                status="SUCCESS",
                num_cells=num_cells,
                num_passing_cells=num_cells,
                err_line="",
            )
        except Exception:
            tb = format_exc()
            nb_dict = get_nb_dict()
            num_cells = len(nb_dict["cells"])
            err_line, num_passing_cells, status = get_failed_nb_details(
                nb_dict, self._treebeard_config
            )

            helper.log(
                f"""{status_emojis[status]} Notebook {notebook_path} failed!\n  {num_passing_cells}/{num_cells} cells ran.\n\n{tb}"""
            )

            return NotebookResult(
                status=status,
                num_cells=num_cells,
                num_passing_cells=num_passing_cells,
                err_line=err_line,
            )

    def _run(
        self,
        user_name: str,
        repo_short_name: str,
        run_id: str,
        upload: bool,
        notebook_files: List[str],
    ) -> Dict[str, NotebookResult]:
        helper.log(f"🌲 treebeard runtime: running repo")

        if self._treebeard_config.debug:
            subprocess.run(
                [
                    "bash",
                    "-c",
                    """
                    echo "working directory is $(pwd)\n\n$(ls -la)\n"
                    """,
                ]
            )

        if self._treebeard_config is None:
            raise Exception("No Treebeard Config Present at runtime!")

        for output_dir in self._treebeard_config.output_dirs:
            os.makedirs(output_dir, exist_ok=True)

        notebook_results = {
            notebook: NotebookResult(
                status="WORKING", num_cells=1, num_passing_cells=1, err_line=""
            )
            for notebook in notebook_files
        }
        print(f"Will run the following:")
        [print(f" - {nb}") for nb in notebook_files]
        print()

        set_as_thumbnail = True
        for i, notebook_path in enumerate(notebook_files):
            helper.log(
                f"{status_emojis['WORKING']} Running {i + 1}/{len(notebook_files)}: {notebook_path}"
            )
            result = self.run_notebook(notebook_path)
            notebook_results[notebook_path] = result
            if upload:
                self.upload_nb(
                    notebook_path, result.status, set_as_thumbnail,
                )
            set_as_thumbnail = False

        return notebook_results

    def finish(
        self, status: int, should_upload_outputs: bool, results: str, logging: bool,
    ):
        def get_status_str():
            if status == 0:
                return "SUCCESS"
            else:
                return "FAILURE"

        print(results)

        if logging:
            helper.update(
                self._treebeard_context,
                update_url=f"{api_url}/{self._treebeard_context.treebeard_env.run_path}/log",
                status=get_status_str(),
            )

        if should_upload_outputs:
            if os.path.exists("treebeard.log"):
                helper.upload_artifact(
                    self._treebeard_context,
                    "treebeard.log",
                    f"{self._run_path}/treebeard.log",
                    None,
                )

            with open("tb_results.log", "w", encoding="utf-8") as results_log:
                results_log.write(results)

            helper.upload_artifact(
                self._treebeard_context,
                "tb_results.log",
                f"{self._run_path}/__treebeard__/tb_results.log",
                None,
            )
            helper.update(
                self._treebeard_context,
                update_url=f"{api_url}/{self._treebeard_context.treebeard_env.run_path}/update",
                status=get_status_str(),
            )
            print(f"🌲 View your outputs at https://treebeard.io/admin/{self._run_path}")

        return status

    def start(self, upload: bool = False, logging: bool = True):
        if not self._treebeard_env.repo_short_name:
            raise Exception("No notebook ID at runtime")
        if not self._treebeard_env.user_name:
            raise Exception("No project ID at buildtime")

        if upload:
            helper.upload_meta_nbs(self._treebeard_context)

        clean_log_file()

        notebook_files = self._treebeard_config.get_deglobbed_notebooks()

        notebook_results = self._run(
            self._treebeard_env.user_name,
            self._treebeard_env.repo_short_name,
            self._treebeard_env.run_id,
            upload,
            notebook_files,
        )

        if upload:
            self.upload_outputs()

        helper.log("🌲 Run Finished. Results:\n")

        results = ""
        for notebook in notebook_results.keys():
            result = notebook_results[notebook]
            health_bar = get_health_bar(
                result.num_passing_cells, result.num_cells, result.status, status_emojis
            )

            if result.status == "SUCCESS":
                results += f"{health_bar} {notebook}\n"
                results += (
                    f"  ran {result.num_passing_cells} of {result.num_cells} cells\n"
                )
            elif not result.err_line:  # failed to parse notebook properly
                results += f"{status_emojis[result.status]} {notebook}"
            else:
                results += f"{health_bar} {notebook}\n"
                results += (
                    f"  ran {result.num_passing_cells} of {result.num_cells} cells\n"
                )
                results += f"  {status_emojis[result.status]} {result.err_line}\n"

            results += "\n"

        n_passed = len(
            list(filter(lambda v: v.status == "SUCCESS", notebook_results.values()))
        )

        total_nbs = len(notebook_results)
        if n_passed < total_nbs:
            summary_block = get_summary(notebook_results, n_passed, total_nbs)
            results += summary_block + "\n"
            tb_log(summary_block, print_content=False)

            try:
                if self._treebeard_config.kernel_name == "python3":
                    imports_ok, import_checker_output = check_imports()
                    results += import_checker_output
                    if self._treebeard_config.strict_mode:
                        results += f"\nℹ️ If you would like to ignore notebook run failures and only fail on missing dependencies, add `strict_mode: False` to a `treebeard.yaml` file\n"
                    else:
                        if imports_ok:
                            results += f"\nℹ️ Strict mode is disabled and import checker passed, run is successful! ✅\n"
                            return self.finish(0, upload, results, logging)
                        else:
                            results += f"\nℹ️ Strict mode is disabled! Fix missing dependencies to get a passing run.\n"
                    results += "\n"
            except Exception as ex:
                click.echo(f"Import checker encountered and error...")
                capture_exception(ex)

            fail_status = 2 if upload else 1
            return self.finish(fail_status, upload, results, logging)
        else:
            return self.finish(0, upload, results, logging)
