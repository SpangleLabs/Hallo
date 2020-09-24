from hallo.modules.convert.convert_repo import ConvertRepo, ConvertPrefixGroup, ConvertPrefix


def test_init():
    test_repo = ConvertRepo()
    prefix_group = ConvertPrefixGroup(test_repo, "test_group")
    prefix_name = "test_name"
    prefix_abbr = "test_abbr"
    prefix_mult = 1337
    test_prefix = ConvertPrefix(prefix_group, prefix_name, prefix_abbr, prefix_mult)
    assert test_prefix.prefix_group == prefix_group
    assert test_prefix.prefix == "test_name"
    assert test_prefix.abbreviation == "test_abbr"
    assert test_prefix.multiplier == 1337


def test_json():
    test_repo = ConvertRepo()
    prefix_group = ConvertPrefixGroup(test_repo, "test_group")
    prefix_name = "test_name"
    prefix_abbr = "test_abbr"
    prefix_mult = 1337
    test_prefix = ConvertPrefix(prefix_group, prefix_name, prefix_abbr, prefix_mult)
    json = test_prefix.to_json()
    rebuild_prefix = ConvertPrefix.from_json(prefix_group, json, )
    assert rebuild_prefix.prefix == test_prefix.prefix
    assert rebuild_prefix.abbreviation == test_prefix.abbreviation
    assert rebuild_prefix.multiplier == test_prefix.multiplier
