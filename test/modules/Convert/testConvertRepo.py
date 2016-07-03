import unittest

from modules.Convert import ConvertRepo, ConvertType


class ConvertRepoTest(unittest.TestCase):

    def test_init(self):
        # Set up test object
        test_repo = ConvertRepo()
        # Check init
        assert test_repo.prefix_group_list == []
        assert test_repo.type_list == []

    def test_add_type(self):
        # Set up test object
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
        # Set up test object
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
        pass

    def test_get_full_unit_list(self):
        pass

    def test_add_prefix_group(self):
        pass

    def test_remove_prefix_group(self):
        pass

    def test_get_prefix_group_by_name(self):
        pass

    def test_xml(self):
        pass
