import os
import unittest
from typing import Callable, TypeVar
from unittest.mock import DEFAULT, Mock, patch

from assertpy import assert_that  # type: ignore

from treebeard.conf import (
    TreebeardConfig,
    TreebeardContext,
    TreebeardEnv,
    get_treebeard_config,
)
from treebeard.notebooks.commands import run_repo

T = TypeVar("T")


class MockValidator(object):
    def __init__(self, validator: Callable[[T], bool]):
        self.validator = validator

    def __eq__(self, other: T):
        return bool(self.validator(other))


class CommandsTest(unittest.TestCase):
    @patch("treebeard.notebooks.commands.build")
    def test_when_config_override_then_yaml_saved(self, mock_build: Mock):
        run_repo(
            ["tests/resources/test_command.ipynb"],
            [],
            [],
            True,
            True,
            False,
            True,
            True,
            None,
        )

        print(f"args {mock_build.build.call_args}")  # type: ignore

        bundle_dir: str = mock_build.build.call_args[0][1]  # type: ignore

        os.chdir(bundle_dir)
        config = get_treebeard_config()
        assert_that(config.notebooks).is_equal_to(
            ["tests/resources/test_command.ipynb"]
        )

    @patch.multiple("treebeard.notebooks.commands", build=DEFAULT, conf=DEFAULT)
    def test_when_no_notebooks_passed_in_then_yaml_nbs_used(
        self, build: Mock, conf: Mock
    ):

        default_nbs = ["tests/resources/test_command.ipynb"]
        conf.get_treebeard_config.return_value = TreebeardConfig(notebooks=default_nbs)
        conf.get_treebeard_env.return_value = TreebeardEnv(
            repo_short_name="", run_id="", user_name=""
        )
        conf.get_config_path.return_value = ""

        run_repo(use_docker=True)

        context: TreebeardContext = build.build.call_args[0][0]
        assert_that(context.treebeard_config.notebooks).is_equal_to(default_nbs)


if __name__ == "__main__":
    unittest.main()
