import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup, ConvertPrefix


class ConvertTypeTest(unittest.TestCase):

    def test_init(self):
        # Set up test objects
        test_repo = ConvertRepo()
        # Test init
        test_type = ConvertType(test_repo, "test_type")
        assert len(test_type.unit_list) == 0
        assert test_type.unit_list == []
        assert test_type.repo == test_repo
        assert test_type.name == "test_type"
        assert test_type.decimals == 2
        assert test_type.base_unit is None

    def test_get_full_unit_list(self):
        pass

    def test_add_unit(self):
        pass

    def test_remove_unit(self):
        pass

    def test_get_unit_by_name(self):
        pass

    def test_xml(self):
        pass
