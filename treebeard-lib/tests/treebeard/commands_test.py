import os
import unittest
from typing import Callable, TypeVar
from unittest.mock import Mock, patch

from treebeard.conf import get_treebeard_config
from treebeard.notebooks import commands

T = TypeVar("T")


class MockValidator(object):
    def __init__(self, validator: Callable[[T], bool]):
        self.validator = validator

    def __eq__(self, other: T):
        return bool(self.validator(other))


class CommandsTest(unittest.TestCase):
    @patch("treebeard.notebooks.commands.build")
    def test_when_config_override_then_yaml_saved(self, mock_build: Mock):
        commands.run_repo(
            ["tests/treebeard/test_command.ipynb"],
            [],
            [],
            True,
            False,
            False,
            True,
            True,
            None,
        )

        print(f"args {mock_build.build.call_args}")  # type: ignore

        bundle_dir: str = mock_build.build.call_args[0][1]  # type: ignore

        os.chdir(bundle_dir)
        config = get_treebeard_config()
        assert config.notebooks == ["tests/treebeard/test.ipynb"]


if __name__ == "__main__":
    unittest.main()
