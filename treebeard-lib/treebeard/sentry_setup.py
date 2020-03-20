import sentry_sdk  # type: ignore

from treebeard.conf import env

sentry_sdk.init(
    "https://58543632a309471a88bb99f4f6bbdca0@sentry.io/2846147", environment=env
)
