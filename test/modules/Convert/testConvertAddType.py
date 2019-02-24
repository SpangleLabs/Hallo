import os
import unittest

from Events import EventMessage
from modules.Convert import ConvertRepo, ConvertType, ConvertUnit, Convert
from test.TestBase import TestBase


class ConvertAddTypeTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Create test repo
        self.test_repo = ConvertRepo()
        test_type1 = ConvertType(self.test_repo, "test_type1")
        self.test_repo.add_type(test_type1)
        test_unit1 = ConvertUnit(test_type1, ["unit1"], 1)
        test_type1.base_unit = test_unit1
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

    def test_duplicate_type_name(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type test_type1 unit=unit2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "already exists" in data[0].text, "Error should say type already exists"
        assert len(self.test_repo.type_list) == 1, "Shouldn't have added a new type"

    def test_no_base_unit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type test_type2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "must define a base unit" in data[0].text, "Should warn a base unit is needed"
        assert "unit=<unit name>" in data[0].text, "Should specify syntax to specify base unit"
        assert len(self.test_repo.type_list) == 1, "Shouldn't have added a new type"

    def test_create_new_type(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type test_type2 unit=unit2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "created new type \"test_type2\"" in data[0].text.lower(), "Should specify new type name"
        assert "with base unit \"unit2\"." in data[0].text, "Should specify base unit, and not decimals"
        assert len(self.test_repo.type_list) == 2, "Didn't add new type"
        new_type = self.test_repo.get_type_by_name("test_type2")
        assert new_type is not None, "Can't find new type"
        assert new_type.base_unit is not None, "New type should have a base unit"
        assert len(new_type.base_unit.name_list) == 1, "Base unit should have 1 name"
        assert new_type.base_unit.name_list[0] == "unit2", "Name should be in base unit name list"
        assert new_type.base_unit.value == 1, "Base unit should have value 1"

    def test_create_new_type_with_decimals(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type test_type2 unit=unit2 decimals=5"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "created new type \"test_type2\"" in data[0].text.lower(), "Should specify new type name"
        assert "with base unit \"unit2\"" in data[0].text, "Should specify base unit"
        assert "and 5 decimal places" in data[0].text, "Didn't specify decimal places"
        assert len(self.test_repo.type_list) == 2, "Didn't add new type"
        new_type = self.test_repo.get_type_by_name("test_type2")
        assert new_type is not None, "Can't find new type"
        assert new_type.base_unit is not None, "New type should have a base unit"
        assert len(new_type.base_unit.name_list) == 1, "Base unit should have 1 name"
        assert new_type.base_unit.name_list[0] == "unit2", "Name should be in base unit name list"
        assert new_type.base_unit.value == 1, "Base unit should have value 1"
        assert new_type.decimals == 5, "Didn't correctly set decimals amount"
