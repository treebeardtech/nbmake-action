import unittest
from unittest.mock import ANY, DEFAULT, Mock, patch

from tests.test_helper import MockValidator
from treebeard import helper as tb_helper_real
from treebeard.conf import TreebeardEnv, get_treebeard_config
from treebeard.notebooks.commands import run_repo

# import treebeard.conf


class ComponentTest(unittest.TestCase):
    @patch.multiple("treebeard.buildtime.build", helper=DEFAULT, tb_helper=DEFAULT)
    def test_when_local_docker_name_is_local(
        self, helper: Mock = Mock(), tb_helper: Mock = Mock()
    ):
        helper.run_image.return_value = 0  # type: ignore
        tb_helper.sanitise_repo_short_name.side_effect = tb_helper_real.sanitise_repo_short_name  # type: ignore

        tenv: TreebeardEnv = TreebeardEnv(
            repo_short_name="test", user_name="testuser", run_id="test_run"
        )
        run_repo(
            ["tests/resources/test.ipynb"],
            [],
            [],
            True,
            True,
            False,
            True,
            True,
            None,
            treebeard_env=tenv,
            treebeard_config=get_treebeard_config(),
        )

        def validate_run_id(r: str):
            print(f"Run ID is: {r}")
            return r.startswith("testuser")

        helper.tag_image.assert_called_with(  # type: ignore
            MockValidator(validate_run_id), MockValidator(validate_run_id)
        )

    @patch.multiple("treebeard.buildtime.build", helper=DEFAULT, tb_helper=DEFAULT)
    def test_update_is_called_when_build_fails(
        self, helper: Mock = Mock(), tb_helper: Mock = Mock()
    ):
        helper.run_repo2docker.side_effect = Exception  # type: ignore
        tb_helper.sanitise_repo_short_name.side_effect = tb_helper_real.sanitise_repo_short_name  # type: ignore

        run_repo(
            ["tests/resources/test.ipynb"], [], [], True, True, False, True, True, None
        )

        def validate_log(url: str):
            print(f"Log url is {url}")
            return url.endswith("/log")

        tb_helper.update.assert_called_once_with(ANY, update_url=MockValidator(validate_log), status=ANY)  # type: ignore

    # @patch("treebeard.buildtime.build.helper")
    # def test_when_github_no_registry_name_is_local(self, mock_helper: Mock):
    #     mock_helper.run_image.return_value = 0  # type: ignore
    #     run_repo(
    #         ["tests/resources/test.ipynb"], [], [], True, False, False, True,
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

    #     def validate_run_id(r: str):
    #         return r.startswith("alex-treebeard/fake-repo:develop-")

    #     mock_helper.tag_image.assert_called_with(  # type: ignore
    #         MockValidator(validate_run_id), "alex-treebeard/fake-repo:develop"
    #     )


if __name__ == "__main__":
    unittest.main()
