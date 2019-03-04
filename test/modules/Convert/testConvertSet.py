import unittest

import modules.Convert
from Events import EventMessage
from test.modules.Convert.ConvertFunctionTestBase import ConvertFunctionTestBase
from test.modules.Convert.testConvertViewRepo import MockMethod


class ConvertSetRunTest(ConvertFunctionTestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.output_add = "{added unit}"
        self.output_set = "{updated unit}"
        self.mock_add = MockMethod(self.output_add)
        self.mock_set = MockMethod(self.output_set)
        self.unit_add = modules.Convert.ConvertSet.add_unit
        self.unit_set = modules.Convert.ConvertSet.set_unit
        modules.Convert.ConvertSet.add_unit = self.mock_add.method
        modules.Convert.ConvertSet.set_unit = self.mock_set.method

    def tearDown(self):
        super().tearDown()
        modules.Convert.ConvertSet.add_unit = self.unit_add
        modules.Convert.ConvertSet.set_unit = self.unit_set

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
            self.server, None, self.test_user, "convert set 7 unit1c = 1 unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_add
        assert self.mock_add.arg is not None
        assert self.mock_set.arg is None
        (input_add, measures_to) = self.mock_add.arg
        assert input_add.strip() == "7 unit1c"
        assert len(measures_to) == 1
        assert measures_to[0].unit == self.test_unit1a
        assert measures_to[0].amount == 1

    def test_add_new_unit_not_base(self):
        "35 unit1c = 5 unit1b"
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert set 35 unit1c = 5 unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_add
        assert self.mock_add.arg is not None
        assert self.mock_set.arg is None
        (input_add, measures_to) = self.mock_add.arg
        assert input_add.strip() == "35 unit1c"
        assert len(measures_to) == 1
        assert measures_to[0].unit == self.test_unit1b
        assert measures_to[0].amount == 5


class ConvertSetSetUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_not_same_type(self):
        assert False
        pass

    def test_none_same_type(self):
        assert False
        pass

    def test_multiple_options(self):
        assert False
        pass

    def test_base_unit_fixed(self):
        assert False
        pass

    def test_set_offset_first_measure_zero(self):
        assert False
        pass

    def test_set_offset_second_measure_zero(self):
        assert False
        pass

    def test_set_offset_both_measures_zero(self):
        assert False
        pass

    def test_set_value_first_measure_number(self):
        assert False
        pass

    def test_set_value_second_measure_number(self):
        assert False
        pass

    def test_set_value_both_measures_one(self):
        assert False
        pass

    def test_set_value_both_measures_numbers(self):
        assert False
        pass

    def test_set_value_not_from_base(self):
        assert False
        pass

    def test_set_value_not_from_base_with_offset(self):
        assert False
        pass


class ConvertSetAddUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_no_ref_recognised(self):
        assert False
        pass

    def test_ambiguous_ref_specified(self):
        assert False
        pass

    def test_no_amount_given(self):
        assert False
        pass

    def test_multiple_amounts_given(self):
        assert False
        pass

    def test_name_in_use(self):
        assert False
        pass

    def test_name_in_use_in_different_type(self):
        assert False
        pass

    def test_add_unit_with_value(self):
        assert False
        pass

    def test_add_unit_with_offset(self):
        assert False
        pass

    def test_add_unit_not_from_base_with_value(self):
        assert False
        pass

    def test_add_unit_not_from_base_with_offset(self):
        assert False
        pass
