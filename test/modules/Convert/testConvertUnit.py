import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit


class ConvertUnitTest(unittest.TestCase):

    def test_init(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        # Test init
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        assert len(test_unit.abbr_list) == 0
        assert test_unit.abbr_list == []
        assert test_unit.type == test_type
        assert test_unit.name_list == test_unit_names
        assert test_unit.value == test_value
        assert test_unit.offset == 0
        assert test_unit.last_updated is None
        assert test_unit.valid_prefix_group is None

    def test_xml(self):
        pass

    def test_add_name(self):
        pass

    def test_remove_name(self):
        pass

    def test_add_abbr(self):
        pass

    def test_remove_abbr(self):
        pass

    def test_set_value(self):
        pass

    def test_set_offset(self):
        pass

    def test_has_name(self):
        pass

    def test_get_prefix_from_user_input(self):
        pass
