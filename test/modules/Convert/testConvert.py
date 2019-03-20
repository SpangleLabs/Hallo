import unittest
from datetime import datetime

import modules.Convert
from Events import EventMessage
from test.TestBase import TestBase
from test.modules.Convert.ConvertFunctionTestBase import ConvertFunctionTestBase
from test.modules.Convert.testConvertViewRepo import MockMethod


class ConvertTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.output_parse = "{parse called}"
        self.mock_parse = MockMethod(self.output_parse)
        self.conv_parse = modules.Convert.Convert.convert_parse
        modules.Convert.Convert.convert_parse = self.mock_parse.method

    def tearDown(self):
        modules.Convert.Convert.convert_parse = self.conv_parse
        super().tearDown()

    def test_passive_run(self):
        self.function_dispatcher.dispatch_passive(EventMessage(
            self.server, self.test_chan, self.test_user,
            "1 unit1b to unit1a"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert data[0].text == self.output_parse
        assert self.mock_parse.arg == ("1 unit1b to unit1a", True)

    def test_run(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "convert 1 unit1b to unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text == self.output_parse
        assert self.mock_parse.arg == ("1 unit1b to unit1a",)

    def test_load_repo(self):
        conv_cls = self.function_dispatcher.get_function_by_name("convert")
        conv_obj = self.function_dispatcher.get_function_object(conv_cls)
        assert conv_obj.convert_repo is not None
        assert isinstance(conv_obj.convert_repo, modules.Convert.ConvertRepo)
        assert len(conv_obj.convert_repo.type_list) > 0


class ConvertConvertParseTest(ConvertFunctionTestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Mock out convert_one_unit and convert_two_unit methods
        self.output_one = "{convert one called}"
        self.output_two = "{convert two called}"
        self.mock_one = MockMethod(self.output_one)
        self.mock_two = MockMethod(self.output_two)
        self.conv_one = modules.Convert.Convert.convert_one_unit
        self.conv_two = modules.Convert.Convert.convert_two_unit
        modules.Convert.Convert.convert_one_unit = self.mock_one.method
        modules.Convert.Convert.convert_two_unit = self.mock_two.method
        # Get the Convert function object
        conv_cls = self.function_dispatcher.get_function_by_name("convert")
        self.conv_obj = self.function_dispatcher.get_function_object(conv_cls)

    def tearDown(self):
        modules.Convert.Convert.convert_one_unit = self.conv_one
        modules.Convert.Convert.convert_two_unit = self.conv_two
        super().tearDown()

    def test_no_split_words(self):
        resp = self.conv_obj.convert_parse("5 unit1b")
        assert resp == self.output_one
        assert self.mock_one.arg is not None
        assert isinstance(self.mock_one.arg[0], list)
        assert len(self.mock_one.arg[0]) == 1
        measure = self.mock_one.arg[0][0]
        assert isinstance(measure, modules.Convert.ConvertMeasure)
        assert measure.amount == 5
        assert measure.unit == self.test_unit1b

    def test_no_split_words_failed_to_build(self):
        resp = self.conv_obj.convert_parse("unit1b")
        assert "i don't understand your input" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()
        assert self.mock_one.arg is None

    def test_no_split_words_failed_to_build_passive(self):
        resp = self.conv_obj.convert_parse("unit1b", True)
        assert resp is None
        assert self.mock_one.arg is None

    def test_too_many_split_words(self):
        resp = self.conv_obj.convert_parse("3 unit1b to unit1a to unit1b")
        assert "i don't understand your input" in resp.lower()
        assert "are you specifying 3 units?" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()
        assert self.mock_one.arg is None

    def test_too_many_split_words_passive(self):
        resp = self.conv_obj.convert_parse("3 unit1b to unit1a to unit1b", True)
        assert resp is None
        assert self.mock_one.arg is None

    def test_measure_first(self):
        resp = self.conv_obj.convert_parse("3 unit1b in unit1a")
        assert resp == self.output_two
        assert self.mock_one.arg is None
        assert self.mock_two.arg is not None
        assert isinstance(self.mock_two.arg[0], list)
        assert isinstance(self.mock_two.arg[1], str)
        assert isinstance(self.mock_two.arg[2], bool)
        assert len(self.mock_two.arg[0]) == 1
        measure = self.mock_two.arg[0][0]
        assert isinstance(measure, modules.Convert.ConvertMeasure)
        assert measure.amount == 3
        assert measure.unit == self.test_unit1b
        assert self.mock_two.arg[1].strip() == "unit1a"
        assert self.mock_two.arg[2] is False

    def test_measure_second(self):
        resp = self.conv_obj.convert_parse("unit1a in 3 unit1b")
        assert resp == self.output_two
        assert self.mock_one.arg is None
        assert self.mock_two.arg is not None
        assert isinstance(self.mock_two.arg[0], list)
        assert isinstance(self.mock_two.arg[1], str)
        assert isinstance(self.mock_two.arg[2], bool)
        assert len(self.mock_two.arg[0]) == 1
        measure = self.mock_two.arg[0][0]
        assert isinstance(measure, modules.Convert.ConvertMeasure)
        assert measure.amount == 3
        assert measure.unit == self.test_unit1b
        assert self.mock_two.arg[1].strip() == "unit1a"
        assert self.mock_two.arg[2] is False

    def test_neither_measures(self):
        resp = self.conv_obj.convert_parse("unit1b to unit1a")
        assert "i don't understand your input" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()
        assert self.mock_one.arg is None
        assert self.mock_two.arg is None

    def test_neither_measures_passive(self):
        resp = self.conv_obj.convert_parse("unit1b to unit1a", True)
        assert resp is None
        assert self.mock_one.arg is None
        assert self.mock_two.arg is None


class ConvertConvertOneUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Get the Convert function object
        conv_cls = self.function_dispatcher.get_function_by_name("convert")
        self.conv_obj = self.function_dispatcher.get_function_object(conv_cls)

    def tearDown(self):
        super().tearDown()

    def test_zero_entries(self):
        resp = self.conv_obj.convert_one_unit([], False)
        assert "i don't understand your input" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()

    def test_zero_entries_passive(self):
        resp = self.conv_obj.convert_one_unit([], True)
        assert resp is None

    def test_only_base_measures(self):
        measures_list = [modules.Convert.ConvertMeasure(5, self.test_unit1a),
                         modules.Convert.ConvertMeasure(3, self.test_unit2a)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert "i don't understand your input" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()

    def test_only_base_measures_passive(self):
        measures_list = [modules.Convert.ConvertMeasure(5, self.test_unit1a),
                         modules.Convert.ConvertMeasure(3, self.test_unit2a)]
        resp = self.conv_obj.convert_one_unit(measures_list, True)
        assert resp is None

    def test_one_measure(self):
        self.test_unit1b.value = 2
        measures_list = [modules.Convert.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp

    def test_two_measures(self):
        self.test_unit1b.value = 2
        measures_list = [modules.Convert.ConvertMeasure(5, self.test_unit1b),
                         modules.Convert.ConvertMeasure(3, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 2
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp
        assert "3.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "6.00 {}".format(self.test_unit1a.name_list[0]) in resp

    def test_one_measure_first_has_date(self):
        self.test_unit1b.value = 2
        self.test_unit1b.last_updated_date = datetime(2019, 3, 20, 0, 15, 46)
        measures_list = [modules.Convert.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp
        assert "(last updated: 2019-03-20 00:15:46)" in resp.lower()

    def test_one_measure_second_has_date(self):
        self.test_unit1b.value = 2
        self.test_unit1a.last_updated_date = datetime(2019, 3, 20, 0, 16, 26)
        measures_list = [modules.Convert.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp
        assert "(last updated: 2019-03-20 00:16:26)" in resp.lower()


class ConvertConvertTwoUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_one_measure_to_unit(self):
        assert False
        pass

    def test_measure_to_invalid_unit(self):
        assert False
        pass

    def test_measure_to_invalid_unit_passive(self):
        assert False
        pass

    def test_two_measures_to_unit(self):
        assert False
        pass

    def test_measure_to_unit_with_prefix(self):
        assert False
        pass

    def test_measure_with_date_to_unit(self):
        assert False
        pass

    def test_measure_to_unit_with_date(self):
        assert False
        pass

    def test_zero_measures_to_unit(self):
        assert False
        pass

    def test_measure_to_same_unit(self):
        assert False
        pass

    def test_measure_to_same_unit_but_with_prefix(self):
        assert False
        pass
