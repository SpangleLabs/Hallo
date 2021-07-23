import os
import unittest

from hallo.modules.convert.convert import Convert
from hallo.modules.convert.convert_repo import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup, ConvertPrefix
from hallo.test.modules.convert.test_base import TestBase


class ConvertFunctionTestBase(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Create test repo
        self.test_repo = ConvertRepo()
        self.test_type1 = ConvertType(self.test_repo, "test_type1")
        self.test_repo.add_type(self.test_type1)
        self.test_unit1a = ConvertUnit(self.test_type1, ["unit1a"], 1)
        self.test_type1.base_unit = self.test_unit1a
        self.test_unit1b = ConvertUnit(self.test_type1, ["unit1b", "same_name"], 2)
        self.test_unit1b.abbr_list = ["abbr1b", "abbr1bz"]
        self.test_type1.add_unit(self.test_unit1b)
        self.test_unit1c = ConvertUnit(self.test_type1, ["unit1c"], 4)
        self.test_unit1b.abbr_list = ["abbr1c"]
        self.test_type1.add_unit(self.test_unit1c)
        # Add a second type
        self.test_type2 = ConvertType(self.test_repo, "test_type2")
        self.test_repo.add_type(self.test_type2)
        self.test_unit2a = ConvertUnit(self.test_type2, ["unit2a"], 1)
        self.test_type2.base_unit = self.test_unit2a
        self.test_unit2b = ConvertUnit(self.test_type2, ["unit2b", "same_name"], 5)
        self.test_type2.add_unit(self.test_unit2b)
        # Add a prefix group
        self.test_group1 = ConvertPrefixGroup(self.test_repo, "test_group1")
        self.test_repo.add_prefix_group(self.test_group1)
        self.test_prefix1a = ConvertPrefix(self.test_group1, "prefix1a", "pref1a", 5)
        self.test_group1.add_prefix(self.test_prefix1a)
        self.test_prefix1b = ConvertPrefix(self.test_group1, "prefixb", "pref1b", 15)
        self.test_group1.add_prefix(self.test_prefix1b)
        # Add a second prefix group
        self.test_group2 = ConvertPrefixGroup(self.test_repo, "test_group2")
        self.test_repo.add_prefix_group(self.test_group2)
        self.test_prefix2a = ConvertPrefix(self.test_group2, "prefix2a", "pref2a", 7)
        self.test_group2.add_prefix(self.test_prefix2a)
        self.test_prefix2b = ConvertPrefix(self.test_group2, "prefixb", "pref2b", 42)
        self.test_group2.add_prefix(self.test_prefix2b)
        # Move current convert.json
        try:
            os.rename(ConvertRepo.STORE_FILE, ConvertRepo.STORE_FILE / ".tmp")
        except OSError:
            pass
        # Put this test repo into the Convert object
        convert_function = self.function_dispatcher.get_function_by_name("convert")
        convert_function_obj = self.function_dispatcher.get_function_object(
            convert_function
        )  # type: Convert
        convert_function_obj.convert_repo = self.test_repo

    def tearDown(self):
        super().tearDown()
        # Put all the normal convert json back where it should be
        try:
            os.remove(ConvertRepo.STORE_FILE)
        except OSError:
            pass
        try:
            os.rename(ConvertRepo.STORE_FILE / ".tmp", ConvertRepo.STORE_FILE)
        except OSError:
            pass
