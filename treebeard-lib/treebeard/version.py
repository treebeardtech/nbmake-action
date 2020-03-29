import os
from pathlib import Path

dirname, filename = os.path.split(os.path.abspath(__file__))
version = Path(f"{dirname}/version.txt").read_text()


def get_version():
    return version
