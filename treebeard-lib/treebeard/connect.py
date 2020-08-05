import sys
import traceback
import IPython  # type: ignore
from IPython.display import display, HTML  # type: ignore
from typing import Any, Callable, Optional


def custom_showtraceback():
    traceback_lines = traceback.format_exception(*sys.exc_info())  # type: ignore
    del traceback_lines[1]
    message = "".join(traceback_lines)
    sys.stderr.write(message)
    display(
        HTML(
            '\n❗ Problem with this notebook? <a style="color:blue">Report an issue</a>'
        )
    )


ORIGINAL_SHOWTRACEBACK = IPython.core.interactiveshell.InteractiveShell.showtraceback
ip: IPython.InteractiveShell = IPython.get_ipython()


def set_tb(showtraceback: Callable):
    IPython.core.interactiveshell.InteractiveShell.showtraceback = showtraceback


def p():
    IPython.core.display.publish_display_data(
        data={
            "text/html": [
                "<div style='width:100%;flex-direction:row-reverse;color:gray;display:flex'>💬 Leave a comment</div>"
            ]
        }
    )


EVENT_NAME = "pre_run_cell"


def add_hook():

    if len(ip.events.callbacks[EVENT_NAME]) > 0:
        ip.events.callbacks[EVENT_NAME] = []
    ip.events.register(EVENT_NAME, p)


def connect(repo: str, workflow: Optional[str] = None):
    add_hook()

    display(
        HTML(
            '<iframe frameBorder="0" allowtransparency="true" style="width:99%;height:60px;background:none transparent;" src="https://localhost:8000/badge"></iframe>'
        )
    )


def disconnect():
    ip.events.unregister(EVENT_NAME, p)
    set_tb(ORIGINAL_SHOWTRACEBACK)


def discuss(prompt: str):
    pass
