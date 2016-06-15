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
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        # Test setup
        assert test_unit.name_list == test_unit_names
        assert len(test_unit.name_list) == 2
        # Add name
        test_unit.add_name("name3")
        # Test changes
        assert len(test_unit.name_list) == 3
        assert "name1" in test_unit.name_list
        assert "name2" in test_unit.name_list
        assert "name3" in test_unit.name_list

    def test_remove_name(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        # Test setup
        assert test_unit.name_list == test_unit_names
        assert len(test_unit.name_list) == 2
        # Add name
        test_unit.remove_name("name1")
        # Test changes
        assert len(test_unit.name_list) == 1
        assert "name2" in test_unit.name_list
        assert "name1" not in test_unit.name_list

    def test_add_abbr(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        # Test setup
        assert test_unit.abbr_list == []
        assert len(test_unit.abbr_list) == 0
        # Add abbreviation
        test_unit.add_abbr("abbr1")
        # Test changes
        assert len(test_unit.abbr_list) == 1
        assert "abbr1" in test_unit.abbr_list
        # Add another abbreviation
        test_unit.add_abbr("abbr2")
        assert len(test_unit.abbr_list) == 2
        assert "abbr2" in test_unit.abbr_list
        assert "abbr1" in test_unit.abbr_list

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
