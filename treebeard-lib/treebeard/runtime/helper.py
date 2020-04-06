import mimetypes
from datetime import datetime

import filetype  # type: ignore
import requests
from requests import Response

file_access_url = "https://api.treebeard.io"


def log(message: str):
    print(f'{datetime.now().strftime("%H:%M:%S")}: {message}')


def upload_artifact(filename: str, upload_path: str):
    log(f"Saving {filename} to {upload_path}")
    content_type: str = filetype.guess(filename)  # type: ignore
    if content_type == None:
        content_type = mimetypes.guess_type(filename)[0] or ""

    with open(filename, "rb") as data:
        resp: Response = requests.get(
            f"{file_access_url}/get_upload_url/{upload_path}",
            params={"content_type": content_type},
        )
        signed_url: str = resp.text
        requests.put(signed_url, data, headers={"Content-Type": content_type})
