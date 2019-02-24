import os
import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit
from test.TestBase import TestBase


class ConvertFunctionTestBase(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Create test repo
        self.test_repo = ConvertRepo()
        test_type1 = ConvertType(self.test_repo, "test_type1")
        self.test_repo.add_type(test_type1)
        test_unit1a = ConvertUnit(test_type1, ["unit1a"], 1)
        test_type1.base_unit = test_unit1a
        test_unit1b = ConvertUnit(test_type1, ["unit1b", "same_name"], 2)
        test_type1.add_unit(test_unit1b)
        # Add a second type
        test_type2 = ConvertType(self.test_repo, "test_type2")
        self.test_repo.add_type(test_type2)
        test_unit2a = ConvertUnit(test_type2, ["unit2a"], 1)
        test_type2.base_unit = test_unit2a
        test_unit2b = ConvertUnit(test_type2, ["unit2b", "same_name"], 5)
        test_type2.add_unit(test_unit2b)
        # Move current convert.json
        try:
            os.rename("store/convert.json", "store/convert.json.tmp")
        except OSError:
            pass
        # Put this test repo into the Convert object
        convert_function = self.function_dispatcher.get_function_by_name("convert")
        convert_function_obj = self.function_dispatcher.get_function_object(convert_function)  # type: Convert
        convert_function_obj.convert_repo = self.test_repo

    def tearDown(self):
        super().tearDown()
        # Put all the normal convert json back where it should be
        try:
            os.remove("store/convert.json")
        except OSError:
            pass
        try:
            os.rename("store/convert.json.tmp", "store/convert.json")
        except OSError:
            pass
