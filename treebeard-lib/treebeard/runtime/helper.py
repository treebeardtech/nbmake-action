import mimetypes
from datetime import datetime
from typing import Any, Dict, Optional

import filetype  # type: ignore
import requests
from requests import Response

file_access_url = "https://api.treebeard.io"


def log(message: str):
    print(f'{datetime.now().strftime("%H:%M:%S")}: {message}')


def get_content_type(filename: str) -> Optional[str]:
    guess: Optional[Any] = filetype.guess(filename)  # type: ignore
    if guess:
        return guess.mime

    return mimetypes.guess_type(filename)[0]


def get_headers(filename: str) -> Dict[str, str]:
    content_type = get_content_type(filename)

    if content_type:
        return {"content_type": content_type}

    return {}


def upload_artifact(filename: str, upload_path: str):
    log(f"Saving {filename} to {upload_path}")

    headers = get_headers(filename)
    with open(filename, "rb") as data:
        resp: Response = requests.get(
            f"{file_access_url}/get_upload_url/{upload_path}", params=headers,
        )
        signed_url: str = resp.text
        requests.put(signed_url, data, headers=headers)
