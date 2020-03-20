from datetime import datetime
from typing import Any

import magic  # type: ignore
import requests
from requests import Response

mime: Any = magic.Magic(mime=True)

file_access_url = "https://file-access-cvee2224cq-ew.a.run.app"


def log(message: str):
    print(f'{datetime.now().strftime("%H:%M:%S")}: {message}')


def upload_artifact(upload_path: str, filename: str):
    log(f"Saving {filename} to {upload_path}")
    content_type: str = mime.from_file(filename)
    with open(filename, "rb") as data:
        resp: Response = requests.get(
            f"{file_access_url}/get_upload_url/{upload_path}",
            params={"content_type": content_type},
        )
        signed_url: str = resp.text
        requests.put(signed_url, data, headers={"Content-Type": content_type})
