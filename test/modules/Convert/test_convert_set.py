import unittest

import modules.convert
from events import EventMessage
from test.modules.Convert.convert_function_test_base import ConvertFunctionTestBase
from test.modules.Convert.test_convert_view_repo import MockMethod


class ConvertSetRunTest(ConvertFunctionTestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.output_add = "{added unit}"
        self.output_set = "{updated unit}"
        self.mock_add = MockMethod(self.output_add)
        self.mock_set = MockMethod(self.output_set)
        self.unit_add = modules.convert.ConvertSet.add_unit
        self.unit_set = modules.convert.ConvertSet.set_unit
        modules.convert.ConvertSet.add_unit = self.mock_add.method
        modules.convert.ConvertSet.set_unit = self.mock_set.method

    def tearDown(self):
        super().tearDown()
        modules.convert.ConvertSet.add_unit = self.unit_add
        modules.convert.ConvertSet.set_unit = self.unit_set

    def test_more_than_two(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 5 unit1b is 3 unit1a = 5 unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "are you specifying 3 units?" in data[0].text.lower()
        assert "convert set <value> <old unit> to <new unit>" in data[0].text.lower()
        assert self.mock_add.arg is None
        assert self.mock_set.arg is None

    def test_only_one_unit(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 3 unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "are you specifying 3 units?" in data[0].text.lower()
        assert "convert set <value> <old unit> to <new unit>" in data[0].text.lower()
        assert self.mock_add.arg is None
        assert self.mock_set.arg is None

    def test_second_part_invalid_1(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 5 unit1b is 15 no_unit"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i don't understand the second half of your input" in data[0].text.lower()
        assert self.mock_add.arg is None
        assert self.mock_set.arg is None

    def test_second_part_invalid_2(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 5 unit1b is no_unit"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i don't understand the second half of your input" in data[0].text.lower()
        assert self.mock_add.arg is None
        assert self.mock_set.arg is None

    def test_second_part_no_value(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 5 unit1b is unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_set
        assert self.mock_add.arg is None
        assert self.mock_set.arg is not None
        (measures_from, measures_to) = self.mock_set.arg
        assert len(measures_from) == 1
        assert len(measures_to) == 1
        assert measures_from[0].unit == self.test_unit1b
        assert measures_from[0].amount == 5
        assert measures_to[0].unit == self.test_unit1a
        assert measures_to[0].amount == 1

    def test_first_part_no_value(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set unit1b is 5 unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_set
        assert self.mock_add.arg is None
        assert self.mock_set.arg is not None
        (measures_from, measures_to) = self.mock_set.arg
        assert len(measures_from) == 1
        assert len(measures_to) == 1
        assert measures_from[0].unit == self.test_unit1b
        assert measures_from[0].amount == 1
        assert measures_to[0].unit == self.test_unit1a
        assert measures_to[0].amount == 5

    def test_neither_have_value(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set unit1a = unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_set
        assert self.mock_add.arg is None
        assert self.mock_set.arg is not None
        (measures_from, measures_to) = self.mock_set.arg
        assert len(measures_from) == 1
        assert len(measures_to) == 1
        assert measures_from[0].unit == self.test_unit1a
        assert measures_from[0].amount == 1
        assert measures_to[0].unit == self.test_unit1b
        assert measures_to[0].amount == 1

    def test_both_have_value(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 15 unit1a = 5 unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_set
        assert self.mock_add.arg is None
        assert self.mock_set.arg is not None
        (measures_from, measures_to) = self.mock_set.arg
        assert len(measures_from) == 1
        assert len(measures_to) == 1
        assert measures_from[0].unit == self.test_unit1a
        assert measures_from[0].amount == 15
        assert measures_to[0].unit == self.test_unit1b
        assert measures_to[0].amount == 5

    def test_add_new_unit(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 7 new_unit = 1 unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_add
        assert self.mock_add.arg is not None
        assert self.mock_set.arg is None
        (input_add, measures_to) = self.mock_add.arg
        assert input_add.strip() == "7 new_unit"
        assert len(measures_to) == 1
        assert measures_to[0].unit == self.test_unit1a
        assert measures_to[0].amount == 1

    def test_add_new_unit_not_base(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 35 new_unit = 5 unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_add
        assert self.mock_add.arg is not None
        assert self.mock_set.arg is None
        (input_add, measures_to) = self.mock_add.arg
        assert input_add.strip() == "35 new_unit"
        assert len(measures_to) == 1
        assert measures_to[0].unit == self.test_unit1b
        assert measures_to[0].amount == 5


# noinspection PyTypeChecker
class ConvertSetSetUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_not_same_type(self):
        value_unit1b = self.test_unit1b.value
        measure_from = modules.convert.ConvertMeasure(5, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(3, self.test_unit2a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "these units do not share the same type" in resp.lower()
        assert self.test_unit1b.value == value_unit1b

    def test_none_same_type(self):
        value_unit1a = self.test_unit1a.value
        value_unit1b = self.test_unit1b.value
        measure_from1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        measure_from2 = modules.convert.ConvertMeasure(5, self.test_unit1a)
        measure_to1 = modules.convert.ConvertMeasure(3, self.test_unit2a)
        measure_to2 = modules.convert.ConvertMeasure(3, self.test_unit2b)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from1, measure_from2], [measure_to1, measure_to2])
        assert "these units do not share the same type" in resp.lower()
        assert self.test_unit1a.value == value_unit1a
        assert self.test_unit1b.value == value_unit1b

    def test_multiple_options(self):
        value_unit1a = self.test_unit1a.value
        value_unit1b = self.test_unit1b.value
        measure_from1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        measure_from2 = modules.convert.ConvertMeasure(5, self.test_unit1a)
        measure_to = modules.convert.ConvertMeasure(3, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from1, measure_from2], [measure_to])
        assert "ambiguous which units you are referring to" in resp.lower()
        assert self.test_unit1a.value == value_unit1a
        assert self.test_unit1b.value == value_unit1b

    def test_base_unit_fixed(self):
        value_unit1a = self.test_unit1a.value
        value_unit1b = self.test_unit1b.value
        measure_from = modules.convert.ConvertMeasure(5, self.test_unit1a)
        measure_to = modules.convert.ConvertMeasure(3, self.test_unit1b)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "you cannot change values of the base unit" in resp.lower()
        assert self.test_unit1a.value == value_unit1a
        assert self.test_unit1b.value == value_unit1b

    def test_set_offset_first_measure_zero(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(0, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(3, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new offset for unit1b" in resp.lower()
        assert "0 unit1b = 3 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 3
        assert self.test_unit1b.value == 1

    def test_set_offset_second_measure_zero(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(15, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(0, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new offset for unit1b" in resp.lower()
        assert "15 unit1b = 0 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == -15
        assert self.test_unit1b.value == 1

    def test_set_offset_both_measures_zero(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 7
        measure_from = modules.convert.ConvertMeasure(0, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(0, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new offset for unit1b" in resp.lower()
        assert "0 unit1b = 0 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 1

    def test_set_offset_with_non_trivial_value(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 5
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(15, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(0, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new offset for unit1b" in resp.lower()
        assert "15 unit1b = 0 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == -75
        assert self.test_unit1b.value == 5

    def test_remove_offset_with_non_trivial_value(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 5
        self.test_unit1b.offset = -75
        measure_from = modules.convert.ConvertMeasure(0, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(0, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new offset for unit1b" in resp.lower()
        assert "0 unit1b = 0 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 5

    def test_set_value_with_non_trivial_offset(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = -5
        measure_from = modules.convert.ConvertMeasure(3, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(1, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1b" in resp.lower()
        assert "10 unit1b = 1 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == -5
        assert self.test_unit1b.value == 2

    def test_remove_value_with_non_trivial_offset(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 10
        self.test_unit1b.offset = -5
        measure_from = modules.convert.ConvertMeasure(6, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(1, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1b" in resp.lower()
        assert "6 unit1b = 1 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == -5
        assert self.test_unit1b.value == 1

    def test_set_value_first_measure_number(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(0.5, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(1, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1b" in resp.lower()
        assert "0.5 unit1b = 1 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 2

    def test_set_value_second_measure_number(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(1, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(5, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1b" in resp.lower()
        assert "1 unit1b = 0.5 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 5

    def test_set_value_both_measures_one(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 17
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(1, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(1, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1b" in resp.lower()
        assert "1 unit1b = 1 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 1

    def test_set_value_both_measures_numbers(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 0
        measure_from = modules.convert.ConvertMeasure(2, self.test_unit1b)
        measure_to = modules.convert.ConvertMeasure(24, self.test_unit1a)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1b" in resp.lower()
        assert "2 unit1b = 24 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 12

    def test_set_value_not_from_base(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 2
        self.test_unit1b.offset = 0
        test_unit1c = modules.convert.ConvertUnit(self.test_type1, ["unit1c"], 1)
        self.test_type1.add_unit(test_unit1c)
        measure_from = modules.convert.ConvertMeasure(4, test_unit1c)
        measure_to = modules.convert.ConvertMeasure(12, self.test_unit1b)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1c" in resp.lower()
        assert "4 unit1c = 12 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 0
        assert self.test_unit1b.value == 2
        assert test_unit1c.offset == 0
        assert test_unit1c.value == 6

    def test_set_value_not_from_base_with_offset(self):
        self.test_unit1a.value = 1
        self.test_unit1a.offset = 0
        self.test_unit1b.value = 1
        self.test_unit1b.offset = 5
        test_unit1c = modules.convert.ConvertUnit(self.test_type1, ["unit1c"], 1)
        self.test_type1.add_unit(test_unit1c)
        measure_from = modules.convert.ConvertMeasure(4, test_unit1c)
        measure_to = modules.convert.ConvertMeasure(7, self.test_unit1b)
        resp = modules.convert.ConvertSet.set_unit(None, [measure_from], [measure_to])
        assert "set new value for unit1c" in resp.lower()
        assert "10 unit1c = 0 unit1a"
        assert self.test_unit1a.offset == 0
        assert self.test_unit1a.value == 1
        assert self.test_unit1b.offset == 5
        assert self.test_unit1b.value == 1
        assert test_unit1c.offset == 0
        assert test_unit1c.value == 3


# noinspection PyTypeChecker
class ConvertSetAddUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_no_ref_recognised(self):
        resp = modules.convert.ConvertSet.add_unit(None, "5 new_unit", [])
        assert "there is no defined unit matching the reference name" in resp.lower()

    def test_ambiguous_ref_specified(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        type2_units = len(self.test_type2.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        measure2 = modules.convert.ConvertMeasure(5, self.test_unit2b)
        resp = modules.convert.ConvertSet.add_unit(None, "5 new_unit", [measure1, measure2])
        assert "it is ambiguous which unit you are referring to" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units
        assert len(self.test_type2.get_full_unit_list()) == type2_units

    def test_no_amount_given(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        resp = modules.convert.ConvertSet.add_unit(None, "new_unit", [measure1])
        assert "please specify an amount when setting a new unit" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units

    def test_multiple_amounts_given(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        resp = modules.convert.ConvertSet.add_unit(None, "5 new_unit 7", [measure1])
        assert "please specify an amount when setting a new unit" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units

    def test_name_in_use(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        resp = modules.convert.ConvertSet.add_unit(None, "5 unit1a", [measure1])
        assert "there's already a unit of that type by that name" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units

    def test_name_in_use_in_different_type(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        resp = modules.convert.ConvertSet.add_unit(None, "5 unit2b", [measure1])
        assert "created new unit unit2b with value: 1 unit2b = 2.0 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("unit2b")
        assert new_unit is not None
        assert new_unit.offset == 0
        assert new_unit.value == 2
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["unit2b"]
        assert new_unit.type == self.test_type1

    def test_add_unit_with_value_first(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(1, self.test_unit1a)
        resp = modules.convert.ConvertSet.add_unit(None, "5 new_unit", [measure1])
        assert "created new unit new_unit with value: 1 new_unit = 0.2 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("new_unit")
        assert new_unit is not None
        assert new_unit.offset == 0
        assert new_unit.value == 0.2
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["new_unit"]
        assert new_unit.type == self.test_type1

    def test_add_unit_with_value_second(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1a)
        resp = modules.convert.ConvertSet.add_unit(None, "1 new_unit", [measure1])
        assert "created new unit new_unit with value: 1 new_unit = 5.0 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("new_unit")
        assert new_unit is not None
        assert new_unit.offset == 0
        assert new_unit.value == 5
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["new_unit"]
        assert new_unit.type == self.test_type1

    def test_add_unit_with_offset_first_zero(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1a)
        resp = modules.convert.ConvertSet.add_unit(None, "0 new_unit", [measure1])
        assert "created new unit new_unit with offset: 0 new_unit = 5.0 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("new_unit")
        assert new_unit is not None
        assert new_unit.offset == 5
        assert new_unit.value == 1
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["new_unit"]
        assert new_unit.type == self.test_type1

    def test_add_unit_with_offset_second_zero(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        measure1 = modules.convert.ConvertMeasure(0, self.test_unit1a)
        resp = modules.convert.ConvertSet.add_unit(None, "7 new_unit", [measure1])
        assert "created new unit new_unit with offset: 0 new_unit = -7.0 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("new_unit")
        assert new_unit is not None
        assert new_unit.offset == -7
        assert new_unit.value == 1
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["new_unit"]
        assert new_unit.type == self.test_type1

    def test_add_unit_not_from_base_with_value(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        self.test_unit1b.offset = 0
        self.test_unit1b.value = 5
        measure1 = modules.convert.ConvertMeasure(1, self.test_unit1b)
        resp = modules.convert.ConvertSet.add_unit(None, "2 new_unit", [measure1])
        assert "created new unit new_unit with value: 1 new_unit = 2.5 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("new_unit")
        assert new_unit is not None
        assert new_unit.offset == 0
        assert new_unit.value == 2.5
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["new_unit"]
        assert new_unit.type == self.test_type1

    def test_add_unit_not_from_base_with_offset(self):
        type1_units = len(self.test_type1.get_full_unit_list())
        self.test_unit1b.offset = -7
        self.test_unit1b.value = 1
        measure1 = modules.convert.ConvertMeasure(5, self.test_unit1b)
        resp = modules.convert.ConvertSet.add_unit(None, "0 new_unit", [measure1])
        assert "created new unit new_unit with offset: 0 new_unit = -2.0 unit1a" in resp.lower()
        assert len(self.test_type1.get_full_unit_list()) == type1_units + 1
        new_unit = self.test_type1.get_unit_by_name("new_unit")
        assert new_unit is not None
        assert new_unit.offset == -2
        assert new_unit.value == 1
        assert new_unit.abbr_list == []
        assert new_unit.name_list == ["new_unit"]
        assert new_unit.type == self.test_type1
