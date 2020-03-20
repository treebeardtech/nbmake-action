import unittest


class ConfTest(unittest.TestCase):
    def test_loads(self):
        import treebeard.conf

        self.assertIsNotNone(treebeard.conf.treebeard_config)
