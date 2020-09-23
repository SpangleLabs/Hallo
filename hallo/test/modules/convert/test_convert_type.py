import unittest

from hallo.modules.convert import ConvertRepo, ConvertType, ConvertUnit


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
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_unitb = ConvertUnit(test_type, ["base_unit"], 1)
        test_type.base_unit = test_unitb
        test_unit1 = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_unit2 = ConvertUnit(test_type, ["name3", "name4"], 505)
        test_type.add_unit(test_unit1)
        test_type.add_unit(test_unit2)
        # Check full unit list
        assert len(test_type.get_full_unit_list()) == 3
        assert test_unitb in test_type.get_full_unit_list()
        assert test_unit1 in test_type.get_full_unit_list()
        assert test_unit2 in test_type.get_full_unit_list()

    def test_add_unit(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        # Add unit to type
        test_type.add_unit(test_unit)
        # Check
        assert len(test_type.unit_list) == 1
        assert test_type.unit_list[0] == test_unit

    def test_remove_unit(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit1 = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_unit2 = ConvertUnit(test_type, ["name3", "name4"], 505)
        test_type.add_unit(test_unit1)
        test_type.add_unit(test_unit2)
        # Check it's all set up correctly
        assert len(test_type.unit_list) == 2
        # Remove unit from type
        test_type.remove_unit(test_unit1)
        # Check
        assert len(test_type.unit_list) == 1
        assert test_type.unit_list[0] == test_unit2

    def test_get_unit_by_name(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_unitb = ConvertUnit(test_type, ["base_unit"], 1)
        test_type.base_unit = test_unitb
        test_unit1 = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_unit2 = ConvertUnit(test_type, ["name3", "name4"], 505)
        test_unit2.add_abbr("u2")
        test_type.add_unit(test_unit1)
        test_type.add_unit(test_unit2)
        # test some stuff
        assert test_type.get_unit_by_name("base_unit") == test_unitb
        assert test_type.get_unit_by_name("NAME1") == test_unit1
        assert test_type.get_unit_by_name("NaMe4") == test_unit2
        assert test_type.get_unit_by_name("u2") == test_unit2

    def test_json(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.decimals = 4
        test_unitb = ConvertUnit(test_type, ["base_unit"], 1)
        test_type.base_unit = test_unitb
        test_unit1 = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_unit2 = ConvertUnit(test_type, ["name3", "name4"], 505)
        test_unit2.add_abbr("u2")
        test_type.add_unit(test_unit1)
        test_type.add_unit(test_unit2)
        # Collapse to XML and rebuild
        test_json = test_type.to_json()
        rebuild_type = ConvertType.from_json(test_repo, test_json, )
        # Test the type
        assert rebuild_type.repo == test_repo
        assert len(rebuild_type.unit_list) == 2
        assert rebuild_type.name == "test_type"
        assert rebuild_type.decimals == 4
        assert rebuild_type.base_unit.name_list[0] == "base_unit"
