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
        count1 = 0
        count2 = 0
        for prefix in rebuild_group.prefix_list:
            assert prefix.prefix_group == rebuild_group
            assert prefix.prefix in [prefix_name1, prefix_name2]
            assert prefix.abbreviation in [prefix_abbr1, prefix_abbr2]
            assert prefix.multiplier in [prefix_mult1, prefix_mult2]
            count1 += prefix.prefix == prefix_name1
            count2 += prefix.prefix == prefix_name2
        assert count1 == 1
        assert count2 == 1

    def test_add_prefix(self):
        # Set up stuff
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        prefix_name1 = "test_name1"
        prefix_abbr1 = "test_abbr1"
        prefix_mult1 = 1001
        test_prefix1 = ConvertPrefix(prefix_group, prefix_name1, prefix_abbr1, prefix_mult1)
        prefix_name2 = "test_name2"
        prefix_abbr2 = "test_abbr2"
        prefix_mult2 = 1002
        test_prefix2 = ConvertPrefix(prefix_group, prefix_name2, prefix_abbr2, prefix_mult2)
        # Add some prefixes and test
        assert len(prefix_group.prefix_list) == 0
        prefix_group.add_prefix(test_prefix1)
        assert len(prefix_group.prefix_list) == 1
        assert test_prefix1 in prefix_group.prefix_list
        prefix_group.add_prefix(test_prefix2)
        assert len(prefix_group.prefix_list) == 2
        assert test_prefix2 in prefix_group.prefix_list

    def test_remove_prefix(self):
        # Set up stuff
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        prefix_name1 = "test_name1"
        prefix_abbr1 = "test_abbr1"
        prefix_mult1 = 1001
        test_prefix1 = ConvertPrefix(prefix_group, prefix_name1, prefix_abbr1, prefix_mult1)
        prefix_name2 = "test_name2"
        prefix_abbr2 = "test_abbr2"
        prefix_mult2 = 1002
        test_prefix2 = ConvertPrefix(prefix_group, prefix_name2, prefix_abbr2, prefix_mult2)
        prefix_group.add_prefix(test_prefix1)
        prefix_group.add_prefix(test_prefix2)
        assert test_prefix1 in prefix_group.prefix_list
        assert test_prefix2 in prefix_group.prefix_list
        assert len(prefix_group.prefix_list) == 2
        # Remove some prefixes and test
        prefix_group.remove_prefix(test_prefix1)
        assert len(prefix_group.prefix_list) == 1
        assert test_prefix2 in prefix_group.prefix_list
        prefix_group.remove_prefix(test_prefix2)
        assert len(prefix_group.prefix_list) == 0

    def test_get_prefix_by_name(self):
        # Set up stuff
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        prefix_name1 = "test_name1"
        prefix_abbr1 = "test_abbr1"
        prefix_mult1 = 1001
        test_prefix1 = ConvertPrefix(prefix_group, prefix_name1, prefix_abbr1, prefix_mult1)
        prefix_name2 = "test_name2"
        prefix_abbr2 = "test_abbr2"
        prefix_mult2 = 1002
        test_prefix2 = ConvertPrefix(prefix_group, prefix_name2, prefix_abbr2, prefix_mult2)
        prefix_group.add_prefix(test_prefix1)
        prefix_group.add_prefix(test_prefix2)
        # Test things
        assert prefix_group.get_prefix_by_name(prefix_name1) == test_prefix1
        assert prefix_group.get_prefix_by_name(prefix_name2) == test_prefix2

    def test_get_prefix_by_abbr(self):
        # Set up stuff
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        prefix_name1 = "test_name1"
        prefix_abbr1 = "test_abbr1"
        prefix_mult1 = 1001
        test_prefix1 = ConvertPrefix(prefix_group, prefix_name1, prefix_abbr1, prefix_mult1)
        prefix_name2 = "test_name2"
        prefix_abbr2 = "test_abbr2"
        prefix_mult2 = 1002
        test_prefix2 = ConvertPrefix(prefix_group, prefix_name2, prefix_abbr2, prefix_mult2)
        prefix_group.add_prefix(test_prefix1)
        prefix_group.add_prefix(test_prefix2)
        # Test things
        assert prefix_group.get_prefix_by_abbr(prefix_abbr1) == test_prefix1
        assert prefix_group.get_prefix_by_abbr(prefix_abbr2) == test_prefix2

    def test_get_appropriate_prefix(self):
        pass
