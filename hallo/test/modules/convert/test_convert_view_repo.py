import unittest
from datetime import datetime

import hallo.modules.convert
from hallo.events import EventMessage
from hallo.test.modules.convert.convert_function_test_base import ConvertFunctionTestBase


class MockMethod:
    def __init__(self, response):
        self.response = response
        self.arg = None
        self.args = []

    def method(self, *arg):
        self.arg = arg
        self.args.append(arg)
        return self.response


# noinspection PyArgumentList
class ConvertViewRepoTest(ConvertFunctionTestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Mock out methods
        self.output_repo = "{repo output}"
        self.output_type = "{type output}"
        self.output_unit = "{unit output}"
        self.output_group = "{group output}"
        self.output_prefix = "{prefix output}"
        self.mock_view_repo = MockMethod(self.output_repo)
        self.mock_view_type = MockMethod(self.output_type)
        self.mock_view_unit = MockMethod(self.output_unit)
        self.mock_view_group = MockMethod(self.output_group)
        self.mock_view_prefix = MockMethod(self.output_prefix)
        self.view_repo = hallo.modules.convert.ConvertViewRepo.output_repo_as_string
        self.view_type = hallo.modules.convert.ConvertViewRepo.output_type_as_string
        self.view_unit = hallo.modules.convert.ConvertViewRepo.output_unit_as_string
        self.view_group = hallo.modules.convert.ConvertViewRepo.output_prefix_group_as_string
        self.view_prefix = hallo.modules.convert.ConvertViewRepo.output_prefix_as_string
        hallo.modules.convert.ConvertViewRepo.output_repo_as_string = (
            self.mock_view_repo.method
        )
        hallo.modules.convert.ConvertViewRepo.output_type_as_string = (
            self.mock_view_type.method
        )
        hallo.modules.convert.ConvertViewRepo.output_unit_as_string = (
            self.mock_view_unit.method
        )
        hallo.modules.convert.ConvertViewRepo.output_prefix_group_as_string = (
            self.mock_view_group.method
        )
        hallo.modules.convert.ConvertViewRepo.output_prefix_as_string = (
            self.mock_view_prefix.method
        )

    def tearDown(self):
        super().tearDown()
        hallo.modules.convert.ConvertViewRepo.output_repo_as_string = self.view_repo
        hallo.modules.convert.ConvertViewRepo.output_type_as_string = self.view_type
        hallo.modules.convert.ConvertViewRepo.output_unit_as_string = self.view_unit
        hallo.modules.convert.ConvertViewRepo.output_prefix_group_as_string = self.view_group
        hallo.modules.convert.ConvertViewRepo.output_prefix_as_string = self.view_prefix

    def test_specified_type_invalid(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo type=no_type"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised type specified" in data[0].text.lower()
        assert self.mock_view_type.arg is None

    def test_type_specified_unit_incorrect(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo type=test_type1 unit=no_unit",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised unit specified" in data[0].text.lower()
        assert self.mock_view_type.arg is None
        assert self.mock_view_unit.arg is None

    def test_type_specified_unit_different_type(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo type=test_type1 unit=unit2a",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised unit specified" in data[0].text.lower()
        assert self.mock_view_type.arg is None
        assert self.mock_view_unit.arg is None

    def test_type_and_unit_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo type=test_type1 unit=unit1b",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_unit in data[0].text.lower()
        assert self.mock_view_unit.arg == (self.test_unit1b,)
        assert self.mock_view_type.arg is None

    def test_type_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo type=test_type1"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_type in data[0].text.lower()
        assert self.mock_view_type.arg == (self.test_type1,)

    def test_specified_group_invalid(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo group=no_group"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix group specified" in data[0].text.lower()
        assert self.mock_view_group.arg is None

    def test_group_specified_prefix_incorrect(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo group=test_group1 prefix=no_prefix",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix specified" in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg is None

    def test_group_specified_prefix_different_group(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo group=test_group1 prefix=prefix2a",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix specified" in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg is None

    def test_group_and_prefix_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo group=test_group1 prefix=prefix1a",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg == (self.test_prefix1a,)

    def test_group_and_prefix_abbr_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert view repo group=test_group1 prefix=pref1a",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg == (self.test_prefix1a,)

    def test_group_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo group=test_group1"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_group in data[0].text.lower()
        assert self.mock_view_group.arg == (self.test_group1,)

    def test_specified_unit_incorrect(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo unit=no_unit"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised unit specified" in data[0].text.lower()
        assert self.mock_view_unit.arg is None

    def test_specified_unit_multiple(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo unit=same_name"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_unit in data[0].text.lower()
        assert (self.test_unit1b,) in self.mock_view_unit.args
        assert (self.test_unit2b,) in self.mock_view_unit.args

    def test_unit_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo unit=unit1b"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_unit in data[0].text.lower()
        assert self.mock_view_unit.arg == (self.test_unit1b,)

    def test_specified_prefix_incorrect(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo prefix=no_prefix"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix specified" in data[0].text.lower()
        assert self.mock_view_prefix.arg is None

    def test_specified_prefix_multiple(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo prefix=prefixb"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert (self.test_prefix1b,) in self.mock_view_prefix.args
        assert (self.test_prefix2b,) in self.mock_view_prefix.args

    def test_prefix_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert view repo prefix=prefix1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.mock_view_prefix.arg == (self.test_prefix1a,)

    def test_nothing_specified(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "convert view repo")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_repo in data[0].text.lower()
        assert self.mock_view_repo.arg == (self.test_repo,)

    def test_output_repo_as_string(self):
        output = self.view_repo(None, self.test_repo).lower()
        assert "conversion repo" in output
        assert "unit types" in output
        assert self.test_type1.name in output
        assert self.test_type2.name in output
        assert "prefix groups" in output
        assert self.test_group1.name in output
        assert self.test_group2.name in output

    def test_output_type_as_string(self):
        output = self.view_type(None, self.test_type1).lower()
        assert "conversion type" in output
        assert self.test_type1.name in output
        assert "decimals: {}".format(self.test_type1.decimals) in output
        assert "base unit: {}".format(self.test_type1.base_unit.name_list[0]) in output
        assert "other units" in output
        assert self.test_unit1b.name_list[0] in output

    def test_output_unit_as_string(self):
        self.test_unit1b.valid_prefix_group = self.test_group2
        self.test_unit1b.last_updated_date = datetime(2019, 3, 2, 22, 24, 15)
        output = self.view_unit(None, self.test_unit1b).lower()
        assert "conversion unit:" in output
        assert "type: {}".format(self.test_type1.name) in output
        assert all([x in output for x in self.test_unit1b.name_list])
        assert all([x in output for x in self.test_unit1b.abbr_list])
        assert (
            "1 {} = {} {}".format(
                self.test_unit1b.name_list[0],
                self.test_unit1b.value,
                self.test_unit1a.name_list[0],
            )
            in output
        )
        assert (
            "0 {} = {} {}".format(
                self.test_unit1b.name_list[0],
                self.test_unit1b.offset,
                self.test_unit1a.name_list[0],
            )
            in output
        )
        assert "last updated: 2019-03-02 22:24:15" in output
        assert "prefix group: {}".format(self.test_group2.name) in output

    def test_output_prefix_group_as_string(self):
        output = self.view_group(None, self.test_group2).lower()
        assert "prefix group" in output
        assert self.test_group2.name in output
        assert "prefix list:" in output
        assert self.test_prefix2a.prefix in output
        assert self.test_prefix2b.prefix in output

    def test_output_prefix_as_string(self):
        output = self.view_prefix(None, self.test_prefix2b).lower()
        assert "prefix" in output
        assert self.test_prefix2b.prefix in output
        assert "abbreviation: {}".format(self.test_prefix2b.abbreviation) in output
        assert "multiplier: {}".format(self.test_prefix2b.multiplier) in output
