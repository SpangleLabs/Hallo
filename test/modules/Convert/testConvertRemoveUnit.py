import unittest

from Events import EventMessage
from test.modules.Convert.ConvertFunctionTestBase import ConvertFunctionTestBase


class ConvertRemoveUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_unrecognised_type(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit type=new_type unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "type is not recognised" in data[0].text, "Error should say type does not exist"
        assert len(self.test_type1.unit_list) == 1, "Shouldn't have removed the unit"

    def test_specified_type_unrecognised_unit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit type=test_type1 unit1c"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unit name is not recognised for that unit type" in data[0].text, \
            "Error should say unit does not exist for specified type"
        assert len(self.test_type1.unit_list) == 1, "Shouldn't have removed the unit"

    def test_specified_type_but_its_base_unit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit type=test_type1 unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "cannot remove the base unit for a unit type" in data[0].text, \
            "Error should say base unit cannot be removed"
        assert self.test_type1.base_unit is not None
        assert "unit1a" in self.test_type1.base_unit.name_list
        assert len(self.test_type1.unit_list) == 1, "Shouldn't have removed the unit"

    def test_specified_type_removes_unit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit type=test_type1 unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed unit \"unit1b\"" in data[0].text.lower(), "Didn't remove unit correctly"
        assert len(self.test_type1.unit_list) == 0, "Should have removed the unit"

    def test_specified_type_with_duplicated_unit_name(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit type=test_type1 same_name"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed unit \"unit1b\"" in data[0].text.lower(), "Didn't remove unit correctly"
        assert len(self.test_type1.unit_list) == 0, "Should have removed the unit"

    def test_no_unit_no_type(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit unit1c"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no unit by that name" in data[0].text.lower(), "Error should say unit not found"
        assert "in any type" in data[0].text.lower(), "Should say it checked all types"
        assert len(self.test_type1.unit_list) == 1, "Shouldn't have removed the unit"

    def test_multiple_matching_units(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit same_name"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "more than one unit matching this name" in data[0].text.lower(), "Error should say multiple units match"
        assert "unit1b (type=test_type1)" in data[0].text.lower(), "Should have suggested unit1b"
        assert "unit2b (type=test_type2)" in data[0].text.lower(), "Should have suggested unit2b"
        assert len(self.test_type1.unit_list) == 1, "Shouldn't have removed the unit from type1"
        assert len(self.test_type2.unit_list) == 1, "Shouldn't have removed the unit from type2"

    def test_no_type_but_base_unit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "cannot remove the base unit for a unit type" in data[0].text, \
            "Error should say base unit cannot be removed"
        assert self.test_type1.base_unit is not None
        assert "unit1a" in self.test_type1.base_unit.name_list
        assert len(self.test_type1.unit_list) == 1, "Shouldn't have removed the unit"

    def test_no_type_removes_unit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert remove unit unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed unit \"unit1b\"" in data[0].text.lower(), "Didn't remove unit correctly"
        assert len(self.test_type1.unit_list) == 0, "Should have removed the unit"
