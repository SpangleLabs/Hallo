import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit, ConvertMeasure, ConvertException, ConvertPrefixGroup, \
    ConvertPrefix


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
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit1 = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_unit2 = ConvertUnit(test_type, ["name3"], 505)
        measure1 = ConvertMeasure(17.5, test_unit1)
        # Convert to base
        test_result = measure1.convert_to(test_unit2)
        # Check
        assert test_result.unit.name_list[0] == "name3"
        assert test_result.amount == 17.5*1337/505

    def test_convert_to_offset(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit1 = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_unit1.update_offset(54)
        test_unit2 = ConvertUnit(test_type, ["name3"], 505)
        test_unit2.update_offset(10)
        measure1 = ConvertMeasure(17.5, test_unit1)
        # Convert to base
        test_result = measure1.convert_to(test_unit2)
        # Check
        assert test_result.unit.name_list[0] == "name3"
        assert test_result.amount == ((17.5*1337)+54-10)/505

    def test_convert_to_different_types(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_type1.base_unit = ConvertUnit(test_type1, ["base_unit"], 1)
        test_unit1 = ConvertUnit(test_type1, ["name1", "name2"], 1337)
        test_type2 = ConvertType(test_repo, "test_type2")
        test_type2.base_unit = ConvertUnit(test_type2, ["another_base"], 1)
        test_unit2 = ConvertUnit(test_type2, ["name3"], 505)
        measure1 = ConvertMeasure(17.5, test_unit1)
        # Convert to base
        try:
            test_result = measure1.convert_to(test_unit2)
            assert False
        except ConvertException as e:
            assert "not the same unit type" in str(e)

    def test_convert_to_base(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        measure1 = ConvertMeasure(17.5, test_unit)
        # Convert to base
        test_result = measure1.convert_to_base()
        # Check
        assert test_result.unit.name_list[0] == "base_unit"
        assert test_result.amount == 17.5*1337

    def test_to_string_no_prefix(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_type.decimals = 3
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        measure1 = ConvertMeasure(17.5, test_unit)
        # Get string
        measure_str = measure1.to_string()
        # Check
        assert str(measure1) == measure_str
        assert measure_str == "17.500 name1"

    def test_to_string(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_type.decimals = 3
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        test_prefix = ConvertPrefix(prefix_group, "ten", "10", 10)
        prefix_group.add_prefix(test_prefix)
        test_unit.valid_prefix_group = prefix_group
        measure1 = ConvertMeasure(17.5, test_unit)
        # Get string
        measure_str = measure1.to_string()
        # Check
        assert str(measure1) == measure_str
        assert measure_str == "1.750 tenname1"

    def test_to_string_with_prefix(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_type.decimals = 3
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        test_prefix1 = ConvertPrefix(prefix_group, "ten", "10", 10)
        test_prefix2 = ConvertPrefix(prefix_group, "hundred", "100", 100)
        prefix_group.add_prefix(test_prefix1)
        prefix_group.add_prefix(test_prefix2)
        test_unit.valid_prefix_group = prefix_group
        measure1 = ConvertMeasure(17.5, test_unit)
        # Get string
        measure_str = measure1.to_string_with_prefix(test_prefix2)
        # Check
        assert measure_str == "0.175 hundredname1"

    def test_build_list_from_user_input_start(self):
        pass

    def test_build_list_from_user_input_end(self):
        pass

    def test_build_list_from_user_input_middle(self):
        pass  # Will fail

    def test_build_list_from_user_input_no_match(self):
        pass

    def test_build_list_from_user_input_multi_match(self):
        pass

    def test_build_list_from_user_input_prefix(self):
        pass
