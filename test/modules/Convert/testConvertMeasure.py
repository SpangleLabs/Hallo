import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup, ConvertMeasure


class ConvertMeasureTest(unittest.TestCase):

    def test_init(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        # Init
        test_measure = ConvertMeasure(12.34, test_unit)
        # Check
        assert test_measure.amount == 12.34
        assert test_measure.unit == test_unit

    def test_is_equal(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        measure1 = ConvertMeasure(17.5, test_unit)
        measure2 = ConvertMeasure(17.5, test_unit)
        # Check not the same object
        assert not measure1 == measure2
        # Check is equal
        assert measure1.is_equal(measure2)
        assert measure2.is_equal(measure1)

    def test_convert_to(self):
        pass

    def test_convert_to_base(self):
        pass

    def test_to_string(self):
        pass

    def test_to_string_with_prefix(self):
        pass

    def test_build_list_from_user_input(self):
        pass
