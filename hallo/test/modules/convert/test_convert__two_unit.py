import unittest
from datetime import datetime

import hallo.modules
from hallo.test.modules.convert.convert_function_test_base import ConvertFunctionTestBase


class ConvertConvertTwoUnitTest(ConvertFunctionTestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Get the Convert function object
        conv_cls = self.function_dispatcher.get_function_by_name("convert")
        self.conv_obj = self.function_dispatcher.get_function_object(conv_cls)

    def tearDown(self):
        super().tearDown()

    def test_one_measure_to_unit(self):
        self.test_unit1b.value = 2
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1a", False)
        assert len(resp.split("\n")) == 1
        assert "5.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "10.00 {}".format(self.test_unit1a.name_list[0]) in resp

    def test_one_measure_to_non_base_unit(self):
        self.test_unit1b.value = 2
        self.test_unit1c.value = 4
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(6, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1c", False)
        assert len(resp.split("\n")) == 1
        assert "6.00 {}".format(self.test_unit1b.name_list[0]) in resp
        assert "3.00 {}".format(self.test_unit1c.name_list[0]) in resp

    def test_measure_to_invalid_unit(self):
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "new_unit", False)
        assert "i don't understand your input" in resp.lower()
        assert "no units specified or found" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()

    def test_measure_to_invalid_unit_passive(self):
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "new_unit", True)
        assert resp is None

    def test_two_measures_to_unit(self):
        self.test_unit1b.value = 2
        self.test_unit1c.value = 3
        measures_list = [
            hallo.modules.convert.convert_repo.ConvertMeasure(2, self.test_unit1b),
            hallo.modules.convert.convert_repo.ConvertMeasure(2, self.test_unit1c),
        ]
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1a", False)
        assert len(resp.split("\n")) == 2
        assert (
            "2.00 {} = 4.00 {}".format(
                self.test_unit1b.name_list[0], self.test_unit1a.name_list[0]
            )
            in resp
        )
        assert (
            "2.00 {} = 6.00 {}".format(
                self.test_unit1c.name_list[0], self.test_unit1a.name_list[0]
            )
            in resp
        )

    def test_measure_to_unit_with_prefix(self):
        self.test_unit1a.valid_prefix_group = self.test_group1
        self.test_unit1b.value = 0.5
        self.test_unit1c.value = 0.3333333
        measures_list = [
            hallo.modules.convert.convert_repo.ConvertMeasure(60, self.test_unit1b),
            hallo.modules.convert.convert_repo.ConvertMeasure(60, self.test_unit1c),
        ]
        resp = self.conv_obj.convert_two_unit(measures_list, "prefix1aunit1a", False)
        assert len(resp.split("\n")) == 2
        assert (
            "60.00 {} = 6.00 prefix1aunit1a".format(self.test_unit1b.name_list[0])
            in resp
        )
        assert (
            "60.00 {} = 4.00 prefix1aunit1a".format(self.test_unit1c.name_list[0])
            in resp
        )

    def test_two_measures_different_types(self):
        self.test_unit1b.value = 0.5
        self.test_unit2b.value = 0.33333333
        measures_list = [
            hallo.modules.convert.convert_repo.ConvertMeasure(1, self.test_unit1a),
            hallo.modules.convert.convert_repo.ConvertMeasure(1, self.test_unit2a),
        ]
        resp = self.conv_obj.convert_two_unit(measures_list, "same_name", False)
        assert len(resp.split("\n")) == 2
        assert (
            "1.00 {} = 2.00 {}".format(
                self.test_unit1a.name_list[0], self.test_unit1b.name_list[0]
            )
            in resp
        )
        assert (
            "1.00 {} = 3.00 {}".format(
                self.test_unit2a.name_list[0], self.test_unit2b.name_list[0]
            )
            in resp
        )

    def test_measure_with_date_to_unit(self):
        self.test_unit1b.value = 2
        self.test_unit1b.last_updated_date = datetime(2019, 3, 20, 0, 15, 46)
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1a", False)
        assert len(resp.split("\n")) == 1
        assert (
            "5.00 {} = 10.00 {}".format(
                self.test_unit1b.name_list[0], self.test_unit1a.name_list[0]
            )
            in resp
        )
        assert "(last updated: 2019-03-20 00:15:46)" in resp.lower()

    def test_measure_to_unit_with_date(self):
        self.test_unit1b.value = 2
        self.test_unit1a.last_updated_date = datetime(2019, 3, 20, 0, 16, 26)
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1a", False)
        assert len(resp.split("\n")) == 1
        assert (
            "5.00 {} = 10.00 {}".format(
                self.test_unit1b.name_list[0], self.test_unit1a.name_list[0]
            )
            in resp
        )
        assert "(last updated: 2019-03-20 00:16:26)" in resp.lower()

    def test_zero_measures_to_unit(self):
        measures_list = []
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1a", False)
        assert "i don't understand your input" in resp.lower()
        assert "no units specified or found" in resp.lower()
        assert "convert <value> <old unit> to <new unit>" in resp.lower()

    def test_zero_measures_to_unit_passive(self):
        measures_list = []
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1a", True)
        assert resp is None

    def test_measure_to_same_unit(self):
        self.test_unit1b.value = 2
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(6, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "unit1b", False)
        assert len(resp.split("\n")) == 1
        assert (
            "6.00 {} = 6.00 {}".format(
                self.test_unit1b.name_list[0], self.test_unit1b.name_list[0]
            )
            in resp
        )

    def test_measure_to_same_unit_but_with_prefix(self):
        self.test_unit1b.value = 2
        self.test_unit1b.valid_prefix_group = self.test_group1
        measures_list = [hallo.modules.convert.convert_repo.ConvertMeasure(5, self.test_unit1b)]
        resp = self.conv_obj.convert_two_unit(measures_list, "prefix1aunit1b", False)
        assert len(resp.split("\n")) == 1
        assert (
            "5.00 {} = 1.00 prefix1aunit1b".format(self.test_unit1b.name_list[0])
            in resp
        )