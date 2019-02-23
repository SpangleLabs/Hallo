import unittest

from modules.Convert import ConvertRepo, ConvertType, ConvertUnit, ConvertMeasure, \
    ConvertPrefixGroup, ConvertPrefix


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
        except Exception as e:
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
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_repo.add_type(test_type)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_type.add_unit(test_unit)
        # Run method
        data = ConvertMeasure.build_list_from_user_input(test_repo, "15 name1")
        # Check results
        assert len(data) == 1
        assert data[0].amount == 15
        assert data[0].unit == test_unit

    def test_build_list_from_user_input_end(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_repo.add_type(test_type)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_type.add_unit(test_unit)
        # Run method
        data = ConvertMeasure.build_list_from_user_input(test_repo, "name2 27")
        # Check results
        assert len(data) == 1
        assert data[0].amount == 27
        assert data[0].unit == test_unit

    def test_build_list_from_user_input_no_amount(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_repo.add_type(test_type)
        test_unit = ConvertUnit(test_type, ["name_a", "name_b"], 1337)
        test_type.add_unit(test_unit)
        # Run method
        try:
            ConvertMeasure.build_list_from_user_input(test_repo, "name_a")
            assert False, "Should have failed to create convert measures."
        except Exception as e:
            assert "cannot find amount" in str(e).lower()

    def test_build_list_from_user_input_middle(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_repo.add_type(test_type)
        test_unit = ConvertUnit(test_type, ["name_a", "name_b"], 1337)
        test_type.add_unit(test_unit)
        # Run method
        try:
            ConvertMeasure.build_list_from_user_input(test_repo, "name_b 15 name_a")
            assert False, "Should have failed to find amount."
        except Exception as e:
            assert "cannot find amount" in str(e).lower()

    def test_build_list_from_user_input_no_match(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_repo.add_type(test_type)
        test_unit = ConvertUnit(test_type, ["name_a", "name_b"], 1337)
        test_type.add_unit(test_unit)
        # Run method
        try:
            ConvertMeasure.build_list_from_user_input(test_repo, "32 name_c")
            assert False, "Should have failed to find a valid unit."
        except Exception as e:
            assert "unrecognised unit" in str(e).lower()

    def test_build_list_from_user_input_multi_match(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type1 = ConvertType(test_repo, "test_type1")
        test_type1.base_unit = ConvertUnit(test_type1, ["base_unit1"], 1)
        test_type2 = ConvertType(test_repo, "test_type2")
        test_type2.base_unit = ConvertUnit(test_type2, ["base_unit2"], 1)
        test_repo.add_type(test_type1)
        test_repo.add_type(test_type2)
        test_unit1 = ConvertUnit(test_type1, ["name1", "name2"], 1337)
        test_unit2 = ConvertUnit(test_type2, ["name2", "name3"], 567)
        test_type1.add_unit(test_unit1)
        test_type2.add_unit(test_unit2)
        # Run method
        data = ConvertMeasure.build_list_from_user_input(test_repo, "7 name2")
        # Check results
        assert len(data) == 2
        assert data[0].amount == 7
        assert data[1].amount == 7
        assert test_unit1 in [data[x].unit for x in [0, 1]]
        assert test_unit2 in [data[x].unit for x in [0, 1]]

    def test_build_list_from_user_input_prefix(self):
        # Setup test objects
        test_repo = ConvertRepo()
        test_type = ConvertType(test_repo, "test_type")
        test_type.base_unit = ConvertUnit(test_type, ["base_unit"], 1)
        test_repo.add_type(test_type)
        test_unit = ConvertUnit(test_type, ["name1", "name2"], 1337)
        test_type.add_unit(test_unit)
        prefix_group = ConvertPrefixGroup(test_repo, "test_group")
        test_prefix = ConvertPrefix(prefix_group, "ten", "10", 10)
        prefix_group.add_prefix(test_prefix)
        test_unit.valid_prefix_group = prefix_group
        # Run method
        data = ConvertMeasure.build_list_from_user_input(test_repo, "tenname2 27")
        # Check results
        assert len(data) == 1
        assert data[0].amount == 270
        assert data[0].unit == test_unit
