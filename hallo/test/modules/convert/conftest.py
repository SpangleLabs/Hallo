from hallo.modules.convert.convert_repo import ConvertRepo, ConvertType, ConvertUnit, ConvertPrefixGroup, ConvertPrefix
from hallo.test.conftest import TestHallo


class TestConvertRepo(ConvertRepo):
    def __init__(self):
        super().__init__()
        self.test_type1 = ConvertType(self, "test_type1")
        self.add_type(self.test_type1)
        self.test_unit1a = ConvertUnit(self.test_type1, ["unit1a"], 1)
        self.test_type1.base_unit = self.test_unit1a
        self.test_unit1b = ConvertUnit(self.test_type1, ["unit1b", "same_name"], 2)
        self.test_unit1b.abbr_list = ["abbr1b", "abbr1bz"]
        self.test_type1.add_unit(self.test_unit1b)
        self.test_unit1c = ConvertUnit(self.test_type1, ["unit1c"], 4)
        self.test_unit1b.abbr_list = ["abbr1c"]
        self.test_type1.add_unit(self.test_unit1c)
        # Add a second type
        self.test_type2 = ConvertType(self, "test_type2")
        self.add_type(self.test_type2)
        self.test_unit2a = ConvertUnit(self.test_type2, ["unit2a"], 1)
        self.test_type2.base_unit = self.test_unit2a
        self.test_unit2b = ConvertUnit(self.test_type2, ["unit2b", "same_name"], 5)
        self.test_type2.add_unit(self.test_unit2b)
        # Add a prefix group
        self.test_group1 = ConvertPrefixGroup(self, "test_group1")
        self.add_prefix_group(self.test_group1)
        self.test_prefix1a = ConvertPrefix(self.test_group1, "prefix1a", "pref1a", 5)
        self.test_group1.add_prefix(self.test_prefix1a)
        self.test_prefix1b = ConvertPrefix(self.test_group1, "prefixb", "pref1b", 15)
        self.test_group1.add_prefix(self.test_prefix1b)
        # Add a second prefix group
        self.test_group2 = ConvertPrefixGroup(self, "test_group2")
        self.add_prefix_group(self.test_group2)
        self.test_prefix2a = ConvertPrefix(self.test_group2, "prefix2a", "pref2a", 7)
        self.test_group2.add_prefix(self.test_prefix2a)
        self.test_prefix2b = ConvertPrefix(self.test_group2, "prefixb", "pref2b", 42)
        self.test_group2.add_prefix(self.test_prefix2b)


def test_repo(tmp_path, test_hallo: TestHallo) -> TestConvertRepo:
    # Create test repo
    repo = TestConvertRepo()
    repo.STORE_FILE = tmp_path / "convert.json"
    # Put this test repo into the Convert object
    convert_function = test_hallo.function_dispatcher.get_function_by_name("convert")
    convert_function_obj = test_hallo.function_dispatcher.get_function_object(
        convert_function
    )  # type: Convert
    convert_function_obj.convert_repo = repo
    return repo
