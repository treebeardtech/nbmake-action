# import unittest
# from unittest.mock import Mock

# from treebeard.notebooks import commands


# class ComponentTest(unittest.TestCase):
#     def docker_name_test(self):
#         # runs tb --no-upload, mocking r2d, checks
#         commands.run(
#             cli_context=Mock(),
#             notebooks=["main.ipynb"],
#             env=[],
#             ignore=[],
#             confirm=True,
#             dockerless=False,
#             upload=False,
#             debug=True,
#         )
