# type: ignore
from fnmatch import fnmatch
from os.path import basename
from typing import Optional

import pytest
from _pytest.config.argparsing import Parser
from pytest import Collector, Item, Session  # type: ignore

from treebeard import run_treebeard


def pytest_addoption(parser: Parser):
    group = parser.getgroup("general")
    group.addoption("--treebeard", action="store_true", help="Test Jupyter notebooks")


def pytest_collect_file(path: str, parent: Collector) -> Optional[Item]:  # type: ignore
    """
    Collect IPython notebooks using the specified pytest hook
    """
    opt = parent.config.option
    if opt.treebeard and fnmatch(path, "*.ipynb"):
        # https://docs.pytest.org/en/stable/deprecations.html#node-construction-changed-to-node-from-parent
        return NotebookFile.from_parent(parent, fspath=path)

    return None


class NotebookFile(pytest.File):
    def collect(self):
        yield NotebookItem.from_parent(self, name="blah", spec={})


class NotebookItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        print("running")
        status = run_treebeard([basename(self.fspath)])
        if status != 0:
            raise Exception("tb failed")

    def repr_failure(self, excinfo):
        return "failed"

    def reportinfo(self):
        return "info"
