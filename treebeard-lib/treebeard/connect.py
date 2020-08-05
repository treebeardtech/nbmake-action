import sys
import traceback
import IPython  # type: ignore
from IPython.display import display, HTML  # type: ignore


def showtraceback():
    traceback_lines = traceback.format_exception(*sys.exc_info())  # type: ignore
    del traceback_lines[1]
    message = "".join(traceback_lines)
    sys.stderr.write(message)
    display(
        HTML(
            '\n🌲 Problem with this notebook? <a style="color:blue">Report an issue</a>'
        )
    )


def set_tb():
    IPython.core.interactiveshell.InteractiveShell.showtraceback = showtraceback


def connect(repo: str):
    print(repo)


def discuss(prompt: str):
    pass
