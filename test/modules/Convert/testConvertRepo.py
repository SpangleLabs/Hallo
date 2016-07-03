import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit


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
        test_type = ConvertType(test_repo, "test_type")
        # Add type
        test_repo.add_type(test_type)
        # Check
        assert len(test_repo.type_list) == 1
        assert test_repo.type_list[0] == test_type

    def test_remove_type(self):
        pass

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
