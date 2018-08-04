import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup, ConvertPrefix


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
        assert test_unit.last_updated_date is None
        assert test_unit.valid_prefix_group is None

    def test_xml(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_repo.add_type(test_type)
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        test_repo.add_prefix_group(prefix_group)
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        # Create test unit
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.update_offset(10)
        test_unit.add_abbr("abbr1")
        test_unit.valid_prefix_group = prefix_group
        # Convert to XML and back
        test_xml = test_unit.to_xml()
        xml_unit = ConvertUnit.from_xml(test_type, test_xml)
        assert len(test_unit.abbr_list) == 1
        assert "abbr1" in xml_unit.abbr_list
        assert xml_unit.type == test_type
        assert len(test_unit.name_list) == 2
        assert "name1" in xml_unit.name_list
        assert "name2" in xml_unit.name_list
        assert xml_unit.value == test_value
        assert xml_unit.offset == 10
        assert xml_unit.last_updated == test_unit.last_updated
        assert xml_unit.valid_prefix_group == prefix_group

    def test_json(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_repo.add_type(test_type)
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        test_repo.add_prefix_group(prefix_group)
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        # Create test unit
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.update_offset(10)
        test_unit.add_abbr("abbr1")
        test_unit.valid_prefix_group = prefix_group
        # Convert to json and back
        test_json = test_unit.to_json()
        json_unit = ConvertUnit.from_json(test_type, test_json)
        assert len(test_unit.abbr_list) == 1
        assert "abbr1" in json_unit.abbr_list
        assert json_unit.type == test_type
        assert len(test_unit.name_list) == 2
        assert "name1" in json_unit.name_list
        assert "name2" in json_unit.name_list
        assert json_unit.value == test_value
        assert json_unit.offset == 10
        assert json_unit.last_updated_date == test_unit.last_updated_date
        assert json_unit.valid_prefix_group == prefix_group

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
        # Remove name
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
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.add_abbr("abbr1")
        test_unit.add_abbr("abbr2")
        # Test setup
        assert "abbr1" in test_unit.abbr_list
        assert "abbr2" in test_unit.abbr_list
        assert len(test_unit.abbr_list) == 2
        # Remove abbreviation
        test_unit.remove_abbr("abbr1")
        # Test changes
        assert len(test_unit.abbr_list) == 1
        assert "abbr2" in test_unit.abbr_list
        assert "abbr1" not in test_unit.abbr_list

    def test_set_value(self):
        # Set up test object
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        # Check value and time updated
        assert test_unit.value == 1337
        assert test_unit.last_updated_date is None
        # Change value
        test_unit.update_value(101)
        # Check value
        assert test_unit.value == 101
        assert test_unit.last_updated_date is not None

    def test_set_offset(self):
        # Set up test object
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        # Check value and time updated
        assert test_unit.offset == 0
        assert test_unit.last_updated_date is None
        # Change value
        test_unit.update_offset(10)
        # Check value
        assert test_unit.offset == 10
        assert test_unit.last_updated_date is not None

    def test_has_name(self):
        # Set up test object
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2", "NaMe3"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.add_abbr("ABbr1")
        test_unit.add_abbr("abbr2")
        # Do some tests
        assert test_unit.has_name("name1")
        assert test_unit.has_name("name3")
        assert test_unit.has_name("NamE2")
        assert not test_unit.has_name("name4")
        assert test_unit.has_name("abbr1")
        assert test_unit.has_name("ABBR2")
        assert not test_unit.has_name("abbr3")

    def test_get_prefix_from_user_input_name(self):
        # Set up prefix group
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
        # Set up test object
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2", "NaMe3"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.add_abbr("ABbr1")
        test_unit.add_abbr("abbr2")
        test_unit.valid_prefix_group = prefix_group
        # Get prefix from input
        assert test_unit.get_prefix_from_user_input("test_name1name2") == test_prefix1
        assert test_unit.get_prefix_from_user_input("test_name1not_a_unit") is False
        assert test_unit.get_prefix_from_user_input("not_a_prefixname2") is False
        assert test_unit.get_prefix_from_user_input("name2") is None
        # Remove prefix group and see what happens
        test_unit.valid_prefix_group = None
        assert test_unit.get_prefix_from_user_input("test_name1name2") is False

    def test_get_prefix_from_user_input_abbr(self):
        # Set up prefix group
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
        # Set up test object
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2", "NaMe3"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.add_abbr("ABbr1")
        test_unit.add_abbr("abbr2")
        test_unit.valid_prefix_group = prefix_group
        # Get prefix from input
        assert test_unit.get_prefix_from_user_input("test_abbr1abbr2") == test_prefix1
        assert test_unit.get_prefix_from_user_input("test_abbr1not_a_unit") is False
        assert test_unit.get_prefix_from_user_input("not_a_prefixabbr2") is False
        assert test_unit.get_prefix_from_user_input("abbr2") is None
        # Remove prefix group and see what happens
        test_unit.valid_prefix_group = None
        assert test_unit.get_prefix_from_user_input("test_abbr1abbr2") is False

    def test_get_prefix_from_user_input_name_internal(self):
        # Set up prefix group
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
        # Set up test object
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "cubic {X}name2", "NaMe3"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.add_abbr("ABbr1")
        test_unit.add_abbr("abbr2")
        test_unit.valid_prefix_group = prefix_group
        # Get prefix from input
        assert test_unit.get_prefix_from_user_input("cubic test_name1name2") == test_prefix1
        assert test_unit.get_prefix_from_user_input("cubic test_name1not_a_unit") is False
        assert test_unit.get_prefix_from_user_input("cubic not_a_prefixname2") is False
        assert test_unit.get_prefix_from_user_input("cubic name2") is None
        # Remove prefix group and see what happens
        test_unit.valid_prefix_group = None
        assert test_unit.get_prefix_from_user_input("cubic test_name1name2") is False

    def test_get_prefix_from_user_input_abbr_internal(self):
        # Set up prefix group
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
        # Set up test object
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit_names = ["name1", "name2", "NaMe3"]
        test_value = 1337
        test_unit = ConvertUnit(test_type, test_unit_names, test_value)
        test_unit.add_abbr("ABbr1")
        test_unit.add_abbr("cubic {X}abbr2")
        test_unit.valid_prefix_group = prefix_group
        # Get prefix from input
        assert test_unit.get_prefix_from_user_input("cubic test_abbr1abbr2") == test_prefix1
        assert test_unit.get_prefix_from_user_input("cubic test_abbr1not_a_unit") is False
        assert test_unit.get_prefix_from_user_input("cubic not_a_prefixabbr2") is False
        assert test_unit.get_prefix_from_user_input("cubic abbr2") is None
        # Remove prefix group and see what happens
        test_unit.valid_prefix_group = None
        assert test_unit.get_prefix_from_user_input("cubic test_abbr1abbr2") is False
