import unittest

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

    def test_no_split_words(self):
        "5 unit1b"
        assert False
        pass

    def test_no_split_words_failed_to_build(self):
        "unit1b"
        assert False
        pass

    def test_no_split_words_failed_to_build_passive(self):
        "unit1b", True
        assert False
        pass

    def test_too_many_split_words(self):
        "3 unit1b to unit1a to unit1b"
        assert False
        pass

    def test_too_many_split_words_passive(self):
        "3 unit1b to unit1a to unit1b", True
        assert False
        pass

    def test_measure_first(self):
        "3 unit1b in unit1a"
        assert False
        pass

    def test_measure_second(self):
        "unit1a in 3 unit1b"
        assert False
        pass

    def test_neither_measures(self):
        "unit1b to unit1a"
        assert False
        pass

    def test_neither_measures_passive(self):
        "unit1b to unit1a", True
        assert False
        pass


class ConvertConvertOneUnitTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_zero_entries(self):
        assert False
        pass

    def test_zero_entries_passive(self):
        assert False
        pass

    def test_only_base_measures(self):
        assert False
        pass

    def test_only_base_measures_passive(self):
        assert False
        pass

    def test_one_measure(self):
        assert False
        pass

    def test_two_measures(self):
        assert False
        pass

    def test_one_measure_first_has_date(self):
        assert False
        pass

    def test_one_measure_second_has_date(self):
        assert False
        pass


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
