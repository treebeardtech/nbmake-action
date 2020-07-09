import unittest
from unittest.mock import ANY, DEFAULT, Mock, patch

from tests.test_helper import MockValidator
from treebeard.conf import (
    TreebeardContext,
    get_treebeard_config,
    get_treebeard_env,
)
from treebeard.runtime.run import NotebookRun

config = get_treebeard_config()
config.notebooks = ["tests/resources/test_runtime.ipynb"]
treebeard_env = get_treebeard_env(None)

#  runtime should always log unless usagelogging flag is False


class RuntimeTest(unittest.TestCase):
    @patch.multiple("treebeard.runtime.run", helper=DEFAULT)
    def test_runtime_always_logs_unless_flag_is_set(self, helper: Mock = Mock()):
        # helper.run_image.return_value = 0  # type: ignore
        # tb_helper.sanitise_repo_short_name.side_effect = tb_helper_real.sanitise_repo_short_name  # type: ignore

        nbrun = NotebookRun(
            TreebeardContext(treebeard_env=treebeard_env, treebeard_config=config)
        )
        status = nbrun.start(upload=False, logging=True)

        assert status == 0

        def validate_log(url: str):
            print(f"Log url is {url}")
            return url.endswith("/log")

        helper.update.assert_called_once_with(ANY, update_url=MockValidator(validate_log), status=ANY)  # type: ignore


if __name__ == "__main__":
    unittest.main()
