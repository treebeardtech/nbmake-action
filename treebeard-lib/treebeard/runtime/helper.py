from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import magic  # type: ignore
import requests
from pydantic import BaseModel  # type: ignore
from requests import Response
from sentry_sdk import capture_exception, capture_message  # type: ignore

from treebeard.conf import api_url, treebeard_config

mime: Any = magic.Magic(mime=True)  # type: ignore


class NotebookResult(BaseModel):
    status: str
    num_cells: int
    num_passing_cells: int
    err_line: str


def log(message: str):
    print(f'{datetime.now().strftime("%H:%M:%S")}: {message}')


def upload_artifact(
    filename: str,
    upload_path: str,
    status: Optional[str],
    set_as_thumbnail: bool = False,
):
    log(f"Saving {filename} to {upload_path}")
    content_type: str = mime.from_file(filename)

    get_url_params = {"content_type": content_type}
    put_object_headers = {"Content-Type": content_type}
    if status:
        get_url_params["status"] = status
        put_object_headers["x-goog-meta-status"] = status

    with open(filename, "rb") as data:
        resp: Response = requests.get(  # type: ignore
            f"{api_url}/get_upload_url/{upload_path}", params=get_url_params,
        )
        if resp.status_code != 200:
            raise (
                Exception(
                    f"Get signed url failed for {filename}, {resp.status_code}\n{resp.text}"
                )
            )
        signed_url: str = resp.text
        put_resp = requests.put(signed_url, data, headers=put_object_headers,)  # type: ignore
        if put_resp.status_code != 200:
            raise (
                Exception(
                    f"Put object failed for {filename}, {put_resp.status_code}\n{put_resp.text}"
                )
            )

        qs = "set_as_thumbnail=true" if set_as_thumbnail else ""
        requests.post(f"{api_url}/{upload_path}/create_extras?{qs}")  # type: ignore


def get_failed_nb_details(nb_dict: Any) -> Tuple[str, int, str]:
    status = "💥"
    num_passing_cells: Optional[int] = 0
    err_line = ""
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
        capture_exception(ex)  # type: ignore

    if not err_line:
        capture_message(f"Could not find err_line for nb {nb_dict['metadata']}")

    return err_line, num_passing_cells, status


def get_health_bar(passing: int, total: int, status: str):
    assert passing <= total
    bar_length = 10
    n_green = int(bar_length * float(passing) / float(total))
    n_red = bar_length - n_green
    if n_green == bar_length:
        return "🟩" * (bar_length - 1) + "✅"
    return ("🟩" * n_green) + status + ("⬜" * (n_red - 1))


def get_summary(
    notebook_results: Dict[str, NotebookResult], n_passed: int, total_nbs: int
):

    summary = "\n"
    nb_percent = int(float(n_passed) / float(total_nbs) * 100)
    summary += f"Notebooks: {n_passed} of {total_nbs} passed ({nb_percent}%)\n"
    total_cells = sum(map(lambda res: res.num_cells, notebook_results.values()))
    total_cells_passed = sum(
        map(lambda res: res.num_passing_cells, notebook_results.values())
    )
    percent = int(100.0 * float(total_cells_passed) / float(total_cells))
    summary += f"Cells: {total_cells_passed} of {total_cells} passed ({percent}%)\n"
    return summary
