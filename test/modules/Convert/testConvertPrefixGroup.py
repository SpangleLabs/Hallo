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
        # Set up stuff
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        # Collapse to XML and rebuild
        text_xml = prefix_group.to_xml()
        rebuild_group = ConvertPrefixGroup.from_xml(test_repo, text_xml)
        assert rebuild_group.repo == test_repo
        assert len(rebuild_group.prefix_list) == 0
        assert rebuild_group.name == "test_group"

    def test_xml_contents(self):
        # Set up stuff
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        prefix_name1 = "test_name1"
        prefix_abbr1 = "test_abbr1"
        prefix_mult1 = 1001
        test_prefix1 = ConvertPrefix(prefix_group, prefix_name1, prefix_abbr1, prefix_mult1)
        prefix_group.add_prefix(test_prefix1)
        prefix_name2 = "test_name2"
        prefix_abbr2 = "test_abbr2"
        prefix_mult2 = 1002
        test_prefix2 = ConvertPrefix(prefix_group, prefix_name2, prefix_abbr2, prefix_mult2)
        prefix_group.add_prefix(test_prefix2)
        # Collapse to XML and rebuild
        text_xml = prefix_group.to_xml()
        rebuild_group = ConvertPrefixGroup.from_xml(test_repo, text_xml)
        assert rebuild_group.repo == test_repo
        assert len(rebuild_group.prefix_list) == 2
        assert rebuild_group.name == "test_group"
        # TODO test prefixes in group

    def test_add_prefix(self):
        pass

    def test_remove_prefix(self):
        pass

    def test_get_prefix_by_name(self):
        pass

    def test_get_prefix_by_abbr(self):
        pass

    def test_get_appropriate_prefix(self):
        pass
