import unittest
from datetime import datetime

import hallo.modules
from hallo.test.modules.convert.convert_function_test_base import ConvertFunctionTestBase


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
        measures_list = [
            hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1a),
            hallo.modules.convert.convert_repo.ConvertMeasure(3, self.test_unit2a),
        ]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert "i don't understand your input" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()

    def test_only_base_measures_passive(self):
        measures_list = [
            hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1a),
            hallo.modules.convert.convert_repo.ConvertMeasure(3, self.test_unit2a),
        ]
        resp = self.conv_obj.convert_one_unit(measures_list, True)
        assert resp is None

    def test_one_measure(self):
        self.test_unit1b.value = 2
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp

    def test_two_measures(self):
        self.test_unit1b.value = 2
        measures_list = [
            hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b),
            hallo.modules.convert.convert_repo.ConvertMeasure(3, self.test_unit1b),
        ]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 2
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp
        assert "3.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "6.00 {}".format(self.test_unit1a.name_list[0]) in resp

    def test_one_measure_first_has_date(self):
        self.test_unit1b.value = 2
        self.test_unit1b.last_updated_date = datetime(2019, 3, 20, 0, 15, 46)
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp
        assert "(last updated: 2019-03-20 00:15:46)" in resp.lower()

    def test_one_measure_second_has_date(self):
        self.test_unit1b.value = 2
        self.test_unit1a.last_updated_date = datetime(2019, 3, 20, 0, 16, 26)
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_one_unit(measures_list, False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp
        assert "(last updated: 2019-03-20 00:16:26)" in resp.lower()