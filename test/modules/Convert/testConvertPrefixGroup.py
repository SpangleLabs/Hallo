import unittest

from modules.Convert import ConvertPrefix, ConvertPrefixGroup, ConvertRepo


class ConvertPrefixGroupTest(unittest.TestCase):

    def test_init(self):
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        assert prefix_group.repo == test_repo
        assert len(prefix_group.prefix_list) == 0
        assert prefix_group.name == "test_group"

    def test_xml(self):
        pass
