import unittest

from test.modules.Convert.ConvertFunctionTestBase import ConvertFunctionTestBase


class ConvertTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_passive_run(self):
        assert False
        pass

    def test_run(self):
        assert False
        pass

    def test_load_repo(self):
        assert False
        pass


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
