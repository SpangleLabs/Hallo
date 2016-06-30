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
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        # Add unit to type
        test_type.add_unit(test_unit)
        # Check
        assert len(test_type.unit_list) == 1
        assert test_type.unit_list[0] == test_unit

    def test_remove_unit(self):
        pass

    def test_get_unit_by_name(self):
        pass

    def test_xml(self):
        pass
