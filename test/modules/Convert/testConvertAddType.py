import unittest

from Events import EventMessage
from test.modules.Convert.ConvertFunctionTestBase import ConvertFunctionTestBase


class ConvertAddTypeTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_duplicate_type_name(self):
        num_types = len(self.test_repo.type_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type test_type1 unit=unit2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "already exists" in data[0].text, "Error should say type already exists"
        assert len(self.test_repo.type_list) == num_types, "Shouldn't have added a new type"

    def test_no_base_unit(self):
        num_types = len(self.test_repo.type_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type new_type"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "must define a base unit" in data[0].text, "Should warn a base unit is needed"
        assert "unit=<unit name>" in data[0].text, "Should specify syntax to specify base unit"
        assert len(self.test_repo.type_list) == num_types, "Shouldn't have added a new type"

    def test_create_new_type(self):
        num_types = len(self.test_repo.type_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type new_type unit=unit2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "created new type \"new_type\"" in data[0].text.lower(), "Should specify new type name"
        assert "with base unit \"unit2\"." in data[0].text, "Should specify base unit, and not decimals"
        assert len(self.test_repo.type_list) == num_types+1, "Didn't add new type"
        new_type = self.test_repo.get_type_by_name("new_type")
        assert new_type is not None, "Can't find new type"
        assert new_type.base_unit is not None, "New type should have a base unit"
        assert len(new_type.base_unit.name_list) == 1, "Base unit should have 1 name"
        assert new_type.base_unit.name_list[0] == "unit2", "Name should be in base unit name list"
        assert new_type.base_unit.value == 1, "Base unit should have value 1"

    def test_create_new_type_with_decimals(self):
        num_types = len(self.test_repo.type_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert add type new_type unit=unit2 decimals=5"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "created new type \"new_type\"" in data[0].text.lower(), "Should specify new type name"
        assert "with base unit \"unit2\"" in data[0].text, "Should specify base unit"
        assert "and 5 decimal places" in data[0].text, "Didn't specify decimal places"
        assert len(self.test_repo.type_list) == num_types+1, "Didn't add new type"
        new_type = self.test_repo.get_type_by_name("new_type")
        assert new_type is not None, "Can't find new type"
        assert new_type.base_unit is not None, "New type should have a base unit"
        assert len(new_type.base_unit.name_list) == 1, "Base unit should have 1 name"
        assert new_type.base_unit.name_list[0] == "unit2", "Name should be in base unit name list"
        assert new_type.base_unit.value == 1, "Base unit should have value 1"
        assert new_type.decimals == 5, "Didn't correctly set decimals amount"
