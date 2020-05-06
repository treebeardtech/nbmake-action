from datetime import datetime
from typing import Any, Optional

import magic  # type: ignore
import requests
from requests import Response

from treebeard.conf import url as api_url

mime: Any = magic.Magic(mime=True)


def log(message: str):
    print(f'{datetime.now().strftime("%H:%M:%S")}: {message}')


def upload_artifact(filename: str, upload_path: str, status: Optional[str]):
    log(f"Saving {filename} to {upload_path}")
    content_type: str = mime.from_file(filename)

    get_url_params = {"content_type": content_type}
    put_object_headers = {"Content-Type": content_type}
    if status:
        get_url_params["status"] = status
        put_object_headers["x-goog-meta-status"] = status

    with open(filename, "rb") as data:
        resp: Response = requests.get(
            f"{api_url}/get_upload_url/{upload_path}", params=get_url_params,
        )
        if resp.status_code != 200:
            raise (
                Exception(
                    f"Get signed url failed for {filename}, {resp.status_code}\n{resp.text}"
                )
            )
        signed_url: str = resp.text
        put_resp = requests.put(signed_url, data, headers=put_object_headers,)
        if put_resp.status_code != 200:
            raise (
                Exception(
                    f"Put object failed for {filename}, {put_resp.status_code}\n{put_resp.text}"
                )
            )
