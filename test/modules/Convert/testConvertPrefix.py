import unittest

from modules.Convert import ConvertPrefix, ConvertPrefixGroup, ConvertRepo


class ConvertPrefixTest(unittest.TestCase):

    def test_xml(self):
        test_repo = ConvertRepo()
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        prefix_name = "test_name"
        prefix_abbr = "test_abbr"
        prefix_mult = 1337
        test_prefix = ConvertPrefix(prefix_group, prefix_name, prefix_abbr, prefix_mult)
        test_xml = test_prefix.to_xml()
        rebuild_prefix = ConvertPrefix.from_xml(prefix_group, test_xml)
        assert rebuild_prefix.prefix == test_prefix.prefix
        assert rebuild_prefix.abbreviation == test_prefix.abbreviation
        assert rebuild_prefix.multiplier == test_prefix.multiplier
