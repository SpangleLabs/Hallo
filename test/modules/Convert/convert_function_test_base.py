import os
from contextlib import contextmanager

from modules.convert import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup, ConvertPrefix, Convert


@contextmanager
def test_convert_repo(hallo):
    # Create test repo
    test_repo = ConvertRepo()
    test_type1 = ConvertType(test_repo, "test_type1")
    test_repo.add_type(test_type1)
    test_unit1a = ConvertUnit(test_type1, ["unit1a"], 1)
    test_type1.base_unit = test_unit1a
    test_unit1b = ConvertUnit(test_type1, ["unit1b", "same_name"], 2)
    test_unit1b.abbr_list = ["abbr1b", "abbr1bz"]
    test_type1.add_unit(test_unit1b)
    test_unit1c = ConvertUnit(test_type1, ["unit1c"], 4)
    test_unit1b.abbr_list = ["abbr1c"]
    test_type1.add_unit(test_unit1c)
    # Add a second type
    test_type2 = ConvertType(test_repo, "test_type2")
    test_repo.add_type(test_type2)
    test_unit2a = ConvertUnit(test_type2, ["unit2a"], 1)
    test_type2.base_unit = test_unit2a
    test_unit2b = ConvertUnit(test_type2, ["unit2b", "same_name"], 5)
    test_type2.add_unit(test_unit2b)
    # Add a prefix group
    test_group1 = ConvertPrefixGroup(test_repo, "test_group1")
    test_repo.add_prefix_group(test_group1)
    test_prefix1a = ConvertPrefix(test_group1, "prefix1a", "pref1a", 5)
    test_group1.add_prefix(test_prefix1a)
    test_prefix1b = ConvertPrefix(test_group1, "prefixb", "pref1b", 15)
    test_group1.add_prefix(test_prefix1b)
    # Add a second prefix group
    test_group2 = ConvertPrefixGroup(test_repo, "test_group2")
    test_repo.add_prefix_group(test_group2)
    test_prefix2a = ConvertPrefix(test_group2, "prefix2a", "pref2a", 7)
    test_group2.add_prefix(test_prefix2a)
    test_prefix2b = ConvertPrefix(test_group2, "prefixb", "pref2b", 42)
    test_group2.add_prefix(test_prefix2b)
    # Move current convert.json
    try:
        os.rename("store/convert.json", "store/convert.json.tmp")
    except OSError:
        pass
    # Put this test repo into the Convert object
    convert_function = hallo.function_dispatcher.get_function_by_name("convert")
    convert_function_obj = hallo.function_dispatcher.get_function_object(convert_function)  # type: Convert
    convert_function_obj.convert_repo = test_repo
    # Yield
    yield test_repo, test_type1, test_unit1a, test_unit1b, test_unit1c, test_type2, test_unit2a, test_unit2b, \
        test_group1, test_prefix1a, test_prefix1b, test_group2, test_prefix2a, test_prefix2b
    # Put all the normal convert json back where it should be
    try:
        os.remove("store/convert.json")
    except OSError:
        pass
    try:
        os.rename("store/convert.json.tmp", "store/convert.json")
    except OSError:
        pass
