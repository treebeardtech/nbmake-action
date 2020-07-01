import sentry_sdk  # type: ignore
from sentry_sdk import configure_scope  # type: ignore

from treebeard.conf import TreebeardEnv, env
from treebeard.version import get_version


def setup_sentry(treebeard_env: TreebeardEnv):
    sentry_sdk.init(  # type: ignore
        "https://58543632a309471a88bb99f4f6bbdca0@sentry.io/2846147", environment=env
    )

    with configure_scope() as scope:  # type: ignore
        scope.set_tag("treebeard_version", get_version())  # type: ignore
        scope.set_tag("user_name", str(treebeard_env.user_name))  # type: ignore
        scope.set_tag("treebeard_repo_short_name", str(treebeard_env.repo_short_name))  # type: ignore
