import unittest

import hallo.modules
from hallo.test.modules.convert.convert_function_test_base import ConvertFunctionTestBase
from hallo.test.modules.convert.test_convert_view_repo import MockMethod


class ConvertConvertParseTest(ConvertFunctionTestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Mock out convert_one_unit and convert_two_unit methods
        self.output_one = "{convert one called}"
        self.output_two = "{convert two called}"
        self.mock_one = MockMethod(self.output_one)
        self.mock_two = MockMethod(self.output_two)
        self.conv_one = hallo.modules.convert.convert.Convert.convert_one_unit
        self.conv_two = hallo.modules.convert.convert.Convert.convert_two_unit
        hallo.modules.convert.convert.Convert.convert_one_unit = self.mock_one.method
        hallo.modules.convert.convert.Convert.convert_two_unit = self.mock_two.method
        # Get the Convert function object
        conv_cls = self.function_dispatcher.get_function_by_name("convert")
        self.conv_obj = self.function_dispatcher.get_function_object(conv_cls)

    def tearDown(self):
        hallo.modules.convert.convert.Convert.convert_one_unit = self.conv_one
        hallo.modules.convert.convert.Convert.convert_two_unit = self.conv_two
        super().tearDown()

    def test_no_split_words(self):
        resp = self.conv_obj.convert_parse("5 unit1b")
        assert resp == self.output_one
        assert self.mock_one.arg is not None
        assert isinstance(self.mock_one.arg[0], list)
        assert len(self.mock_one.arg[0]) == 1
        measure = self.mock_one.arg[0][0]
        assert isinstance(measure, hallo.modules.convert.convert_repo.ConvertMeasure)
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
        assert isinstance(measure, hallo.modules.convert.convert_repo.ConvertMeasure)
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
        assert isinstance(measure, hallo.modules.convert.convert_repo.ConvertMeasure)
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