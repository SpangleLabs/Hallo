import os
import unittest

from hallo.modules.convert import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup


class ConvertRepoTest(unittest.TestCase):
    def test_init(self):
        # Set up test object
        test_repo = ConvertRepo()
        # Check init
        assert test_repo.prefix_group_list == []
        assert test_repo.type_list == []

    def test_add_type(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_type2 = ConvertType(test_repo, "test_type2")
        # Add type
        test_repo.add_type(test_type1)
        # Check
        assert len(test_repo.type_list) == 1
        assert test_repo.type_list[0] == test_type1
        # Add another type
        test_repo.add_type(test_type2)
        # Check again
        assert len(test_repo.type_list) == 2
        assert test_type2 in test_repo.type_list

    def test_remove_type(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_type2 = ConvertType(test_repo, "test_type2")
        test_repo.add_type(test_type1)
        test_repo.add_type(test_type2)
        assert len(test_repo.type_list) == 2
        # Remove type
        test_repo.remove_type(test_type1)
        # Check
        assert len(test_repo.type_list) == 1
        assert test_repo.type_list[0] == test_type2
        # Remove other type
        test_repo.remove_type(test_type2)
        # Check again
        assert len(test_repo.type_list) == 0
        assert test_repo.type_list == []

    def test_get_type_by_name(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_type2 = ConvertType(test_repo, "test_type2")
        test_repo.add_type(test_type1)
        test_repo.add_type(test_type2)
        # Test
        assert test_repo.get_type_by_name("test_type1") == test_type1
        assert test_repo.get_type_by_name("test_type2") == test_type2

    def test_get_full_unit_list(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_repo.add_type(test_type1)
        test_unit1 = ConvertUnit(test_type1, ["unit1"], 1)
        test_unit2 = ConvertUnit(test_type1, ["unit2"], 10)
        test_unit3 = ConvertUnit(test_type1, ["unit3"], 100)
        test_type1.base_unit = test_unit1
        test_type1.add_unit(test_unit2)
        test_type1.add_unit(test_unit3)
        test_type2 = ConvertType(test_repo, "test_type2")
        test_unit4 = ConvertUnit(test_type2, ["unit4"], 1)
        test_unit5 = ConvertUnit(test_type2, ["unit5"], 1000)
        test_type2.base_unit = test_unit4
        test_type2.add_unit(test_unit5)
        test_repo.add_type(test_type2)
        # Test
        assert test_unit1 in test_repo.get_full_unit_list()
        assert test_unit2 in test_repo.get_full_unit_list()
        assert test_unit3 in test_repo.get_full_unit_list()
        assert test_unit4 in test_repo.get_full_unit_list()
        assert test_unit5 in test_repo.get_full_unit_list()
        assert len(test_repo.get_full_unit_list()) == 5

    def test_add_prefix_group(self):
        test_repo = ConvertRepo()
        test_group1 = ConvertPrefixGroup(test_repo, "group1")
        test_group2 = ConvertPrefixGroup(test_repo, "group2")
        # Add group
        test_repo.add_prefix_group(test_group1)
        # Check
        assert len(test_repo.prefix_group_list) == 1
        assert test_repo.prefix_group_list[0] == test_group1
        # Add group
        test_repo.add_prefix_group(test_group2)
        # Check
        assert len(test_repo.prefix_group_list) == 2
        assert test_group2 in test_repo.prefix_group_list

    def test_remove_prefix_group(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_group1 = ConvertPrefixGroup(test_repo, "group1")
        test_group2 = ConvertPrefixGroup(test_repo, "group2")
        test_repo.add_prefix_group(test_group1)
        test_repo.add_prefix_group(test_group2)
        # Remove group
        test_repo.remove_prefix_group(test_group1)
        # Check
        assert len(test_repo.prefix_group_list) == 1
        assert test_repo.prefix_group_list[0] == test_group2
        # Remove other group
        test_repo.remove_prefix_group(test_group2)
        # Check
        assert test_repo.prefix_group_list == []

    def test_get_prefix_group_by_name(self):
        # Set up test objects
        test_repo = ConvertRepo()
        test_group1 = ConvertPrefixGroup(test_repo, "group1")
        test_group2 = ConvertPrefixGroup(test_repo, "group2")
        test_repo.add_prefix_group(test_group1)
        test_repo.add_prefix_group(test_group2)
        # Test
        assert test_repo.get_prefix_group_by_name("group1") == test_group1
        assert test_repo.get_prefix_group_by_name("group2") == test_group2

    def test_json(self):
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_type2 = ConvertType(test_repo, "test_type2")
        test_repo.add_type(test_type1)
        test_repo.add_type(test_type2)
        test_unit1 = ConvertUnit(test_type1, ["unit1"], 1)
        test_unit2 = ConvertUnit(test_type2, ["unit2"], 1)
        test_type1.base_unit = test_unit1
        test_type2.base_unit = test_unit2
        test_group1 = ConvertPrefixGroup(test_repo, "group1")
        test_group2 = ConvertPrefixGroup(test_repo, "group2")
        test_repo.add_prefix_group(test_group1)
        test_repo.add_prefix_group(test_group2)
        # Save to JSON and load
        try:
            try:
                os.rename("store/convert.json", "store/convert.json.tmp")
            except OSError:
                pass
            test_repo.save_json()
            new_repo = ConvertRepo.load_json()
            assert len(new_repo.type_list) == 2
            assert len(new_repo.prefix_group_list) == 2
            assert "test_type1" in [x.name for x in new_repo.type_list]
            assert "test_type2" in [x.name for x in new_repo.type_list]
            assert "group1" in [x.name for x in new_repo.prefix_group_list]
            assert "group2" in [x.name for x in new_repo.prefix_group_list]
        finally:
            try:
                os.remove("store/convert.json")
            except OSError:
                pass
            try:
                os.rename("store/convert.json.tmp", "store/convert.json")
            except OSError:
                pass
