import unittest

from modules.Convert import ConvertInputParser


class ConvertInputParserTest(unittest.TestCase):

    def test_no_args(self):
        p = ConvertInputParser("blah blah")
        assert p.remaining_text == "blah blah"
        assert len(p.args_dict) == 0

    def test_multiple_simple_args(self):
        p = ConvertInputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
        assert p.remaining_text == "blah blah"
        assert p.args_dict["arg1"] == "val1"
        assert p.args_dict["arg2"] == "val2"
        assert p.args_dict["arg3"] == "val3"

    def test_quoted_args_quoted_values(self):
        p = ConvertInputParser("yo 'base unit'=\"hello world\"")
        assert p.remaining_text == "yo"
        assert p.args_dict["base unit"] == "hello world"

    def test_quoted_args_unquoted_values(self):
        p = ConvertInputParser("yo 'base unit'=hello world")
        assert p.remaining_text == "yo world"
        assert p.args_dict["base unit"] == "hello"

    def test_unquoted_args_quoted_values(self):
        p = ConvertInputParser("yo base unit=\"hello world\"")
        assert p.remaining_text == "yo base"
        assert p.args_dict["unit"] == "hello world"

    def test_unquoted_args_unquoted_values(self):
        p = ConvertInputParser("yo base unit=hello world")
        assert p.remaining_text == "yo base world"
        assert p.args_dict["unit"] == "hello"

    def test_mismatched_quotes(self):
        p = ConvertInputParser("yo 'base unit\"=\"hello world\"")
        assert p.remaining_text == "yo 'base"
        assert p.args_dict["unit\""] == "hello world"
        p = ConvertInputParser("yo 'base unit'=\"hello's world\"")
        assert p.remaining_text == "yo"
        assert p.args_dict["base unit"] == "hello's world"

    def test_all_types(self):
        p = ConvertInputParser("yo 'base unit'=\"hello world\" arg1='value 1' 'arg 2'=val2 arg3=val3")
        assert p.remaining_text == "yo"
        assert p.args_dict["base unit"] == "hello world"
        assert p.args_dict["arg1"] == "value 1"
        assert p.args_dict["arg 2"] == "val2"
        assert p.args_dict["arg3"] == "val3"

    def test_remaining_text_start_and_end(self):
        p = ConvertInputParser("blah blah arg1=val1 arg2=val2 hey")
        assert p.remaining_text == "blah blah hey"
        assert p.args_dict["arg1"] == "val1"
        assert p.args_dict["arg2"] == "val2"

    def test_unstripped_input(self):
        p = ConvertInputParser("   blah blah ")
        assert p.remaining_text == "blah blah"

    def test_get_arg_by_names(self):
        p = ConvertInputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
        assert p.remaining_text == "blah blah"
        assert p.get_arg_by_names(["arg2"]) == "val2"
        assert p.args_dict["arg1"] == "val1"
        assert p.args_dict["arg2"] == "val2"
        assert p.args_dict["arg3"] == "val3"

    def test_get_arg_by_names_no_match(self):
        p = ConvertInputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
        assert p.remaining_text == "blah blah"
        assert p.get_arg_by_names(["arg4"]) is None
        assert p.args_dict["arg1"] == "val1"
        assert p.args_dict["arg2"] == "val2"
        assert p.args_dict["arg3"] == "val3"

    def test_get_arg_by_names_one_match(self):
        p = ConvertInputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
        assert p.remaining_text == "blah blah"
        assert p.get_arg_by_names(["arg4", "arg5", "arg3"]) == "val3"
        assert p.args_dict["arg1"] == "val1"
        assert p.args_dict["arg2"] == "val2"
        assert p.args_dict["arg3"] == "val3"

    def test_get_arg_by_names_first_match(self):
        p = ConvertInputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
        assert p.remaining_text == "blah blah"
        assert p.get_arg_by_names(["arg1", "arg2"]) == "val1"
        assert p.args_dict["arg1"] == "val1"
        assert p.args_dict["arg2"] == "val2"
        assert p.args_dict["arg3"] == "val3"
