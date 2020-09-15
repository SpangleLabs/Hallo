from hallo.inc.input_parser import InputParser


def test_no_args():
    p = InputParser("blah blah")
    assert p.remaining_text == "blah blah"
    assert len(p.args_dict) == 0


def test_multiple_simple_args():
    p = InputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
    assert p.remaining_text == "blah blah"
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"
    assert p.args_dict["arg3"] == "val3"


def test_quoted_args_quoted_values():
    p = InputParser("yo 'base unit'=\"hello world\"")
    assert p.remaining_text == "yo"
    assert p.args_dict["base unit"] == "hello world"


def test_quoted_args_unquoted_values():
    p = InputParser("yo 'base unit'=hello world")
    assert p.remaining_text == "yo world"
    assert p.args_dict["base unit"] == "hello"


def test_unquoted_args_quoted_values():
    p = InputParser('yo base unit="hello world"')
    assert p.remaining_text == "yo base"
    assert p.args_dict["unit"] == "hello world"


def test_unquoted_args_unquoted_values():
    p = InputParser("yo base unit=hello world")
    assert p.remaining_text == "yo base world"
    assert p.args_dict["unit"] == "hello"


def test_mismatched_quotes():
    p = InputParser('yo \'base unit"="hello world"')
    assert p.remaining_text == "yo 'base"
    assert p.args_dict['unit"'] == "hello world"
    p = InputParser("yo 'base unit'=\"hello's world\"")
    assert p.remaining_text == "yo"
    assert p.args_dict["base unit"] == "hello's world"


def test_all_types():
    p = InputParser(
        "yo 'base unit'=\"hello world\" arg1='value 1' 'arg 2'=val2 arg3=val3"
    )
    assert p.remaining_text == "yo"
    assert p.args_dict["base unit"] == "hello world"
    assert p.args_dict["arg1"] == "value 1"
    assert p.args_dict["arg 2"] == "val2"
    assert p.args_dict["arg3"] == "val3"


def test_remaining_text_start_and_end():
    p = InputParser("blah blah arg1=val1 arg2=val2 hey")
    assert p.remaining_text == "blah blah hey"
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"


def test_unstripped_input():
    p = InputParser("   blah blah ")
    assert p.remaining_text == "blah blah"


def test_get_arg_by_names():
    p = InputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
    assert p.remaining_text == "blah blah"
    assert p.get_arg_by_names(["arg2"]) == "val2"
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"
    assert p.args_dict["arg3"] == "val3"


def test_get_arg_by_names_no_match():
    p = InputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
    assert p.remaining_text == "blah blah"
    assert p.get_arg_by_names(["arg4"]) is None
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"
    assert p.args_dict["arg3"] == "val3"


def test_get_arg_by_names_one_match():
    p = InputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
    assert p.remaining_text == "blah blah"
    assert p.get_arg_by_names(["arg4", "arg5", "arg3"]) == "val3"
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"
    assert p.args_dict["arg3"] == "val3"


def test_get_arg_by_names_first_match():
    p = InputParser("blah blah arg1=val1 arg2=val2 arg3=val3")
    assert p.remaining_text == "blah blah"
    assert p.get_arg_by_names(["arg1", "arg2"]) == "val1"
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"
    assert p.args_dict["arg3"] == "val3"


def test_parse_string_no_numbers():
    p = InputParser("blah bloo blee")
    assert p.remaining_text == "blah bloo blee"
    assert len(p.args_dict) == 0
    assert len(p.string_words) == 3
    assert len(p.number_words) == 0
    assert p.string_words == ["blah", "bloo", "blee"]


def test_parse_string_all_numbers():
    p = InputParser("5 421 8916 34.5 -3")
    assert p.remaining_text == "5 421 8916 34.5 -3"
    assert len(p.args_dict) == 0
    assert len(p.string_words) == 0
    assert len(p.number_words) == 5
    assert p.number_words == [5, 421, 8916, 34.5, -3]


def test_parse_string_mix_of_numbers_and_args():
    p = InputParser("blah blah arg1=val1 arg2=val2 5")
    assert p.remaining_text == "blah blah 5"
    assert p.args_dict["arg1"] == "val1"
    assert p.args_dict["arg2"] == "val2"
    assert p.string_words == ["blah", "blah"]
    assert p.number_words == [5]
