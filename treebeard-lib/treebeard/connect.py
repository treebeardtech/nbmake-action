import sys
import traceback
import IPython  # type: ignore
from IPython.display import display, HTML, IFrame  # type: ignore
from typing import Callable, Optional, Any
import warnings

from urllib.parse import urlencode, quote_plus


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


ORIGINAL_SHOWTRACEBACK: Callable = IPython.core.interactiveshell.InteractiveShell.showtraceback
ip: IPython.InteractiveShell = IPython.get_ipython()  # type: ignore

EVENT_NAME = "pre_run_cell"

# def set_tb(showtraceback: Callable):
#     IPython.core.interactiveshell.InteractiveShell.showtraceback = showtraceback


class Connect:
    def __init__(
        self,
        repo: str,
        file: Optional[str] = None,
        workflow: Optional[str] = None,
        branch: Optional[str] = "master",
    ):
        self.repo = repo
        self.file = file
        self.workflow = workflow
        self.branch = branch

    def insert_comment_button(self, info: Any):
        # print("blah")
        qs = {
            "title": "Notebook cell comment",
            "body": f"```\n{info.raw_cell}\n```",
        }
        issue_url = f"""https://github.com/{self.repo}/issues/new?{urlencode(qs, quote_via=quote_plus)}"""
        display(
            HTML(
                f"""<div style='width:100%;flex-direction:row-reverse;color:gray;display:flex;font-size:10px'>
                       <a style='opacity:0.5;margin-left:auto' target='_blank' href='{issue_url}'>💬 <span>cmd-click to comment</span></a>
                    </div>"""
            )
        )
        display()
        # display(
        #     HTML(
        #         '<iframe frameBorder="0" allowtransparency="true" style="width:99%;height:60px;background:none transparent;" src="http://lite.cnn.com/en"></iframe>'
        #     )
        # )
        # display(IFrame("http://lite.cnn.com/en", width="500px", height="200px"))

    def add_hook(self):

        if len(ip.events.callbacks[EVENT_NAME]) > 0:  # type: ignore
            ip.events.callbacks[EVENT_NAME] = []
        ip.events.register(EVENT_NAME, lambda info: self.insert_comment_button(info))

    def disconnect(self):
        ip.events.callbacks[EVENT_NAME] = []
        # set_tb(ORIGINAL_SHOWTRACEBACK)


INSTANCE: Optional[Connect] = None


def connect(
    repo: str,
    file: Optional[str] = None,
    workflow: Optional[str] = None,
    branch: str = "master",
):

    if INSTANCE:
        INSTANCE.disconnect()

    instance = Connect(repo, file, workflow, branch)
    instance.add_hook()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        display(
            HTML(
                '<div style="overflow:hidden"><iframe frameBorder="0" allowtransparency="true" style="width:99%;height:60px;background:none transparent;margin-bottom:-30px" src="https://localhost:8000/badge"></iframe></div>'
            )
        )


def discuss(prompt: str):
    pass
