import unittest
from typing import Callable, TypeVar
from unittest.mock import Mock, patch

# from treebeard.conf import treebeard_env
from treebeard.notebooks import commands

import os

# import treebeard.conf

T = TypeVar("T")


class MockValidator(object):
    def __init__(self, validator: Callable[[T], bool]):
        self.validator = validator

    def __eq__(self, other: T):
        return bool(self.validator(other))


class ComponentTest(unittest.TestCase):
    @patch("treebeard.buildtime.build.helper")
    def test_when_local_docker_name_is_local(self, mock_helper: Mock):
        mock_helper.run_image.return_value = 0  # type: ignore
        commands.run_repo(
            ["tests/treebeard/test.ipynb"], [], [], True, False, False, True,
        )

        def validate_run_id(r: str):
            return r.startswith("local-user/treebeard-lib:local-")

        mock_helper.tag_image.assert_called_with(  # type: ignore
            MockValidator(validate_run_id), "local-user/treebeard-lib:cli"
        )

    # @patch("treebeard.buildtime.build.helper")
    # def test_when_github_no_registry_name_is_local(self, mock_helper: Mock):
    #     mock_helper.run_image.return_value = 0  # type: ignore
    #     commands.run_repo(
    #         ["test.ipynb"], [], [], True, False, False, True,
    #     )

    #     os.environ["GITHUB_REPOSITORY"] = "alex-treebeard/fake-repo"
    #     os.environ["TREEBEARD_API_KEY"] = "aaaaaaaaaa"
    #     os.environ["GITHUB_RUN_ID"] = "787878787878"
    #     os.environ["GITHUB_REF"] = "refs/heads/develop"

    #     new_env = treebeard.conf.get_treebeard_env()
    #     treebeard.conf.treebeard_env.repo_short_name = new_env.repo_short_name
    #     treebeard.conf.treebeard_env.branch = new_env.branch
    #     treebeard.conf.treebeard_env.api_key = new_env.api_key
    #     treebeard.conf.treebeard_env.run_id = new_env.run_id
    #     treebeard.conf.treebeard_env.user_name = new_env.user_name
    #     treebeard.conf.treebeard_env.email = new_env.email

    #     def validate_run_id(r: str):
    #         return r.startswith("alex-treebeard/fake-repo:develop-")

    #     mock_helper.tag_image.assert_called_with(  # type: ignore
    #         MockValidator(validate_run_id), "alex-treebeard/fake-repo:develop"
    #     )


if __name__ == "__main__":
    unittest.main()
