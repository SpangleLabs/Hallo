import unittest

from events import EventMessage
from test.modules.convert.convert_function_test_base import ConvertFunctionTestBase


class ConvertUnitSetPrefixGroupTest(ConvertFunctionTestBase, unittest.TestCase):
    def test_type_specified_1(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 unit=same_name prefix_group=test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group == self.test_group1

    def test_type_specified_2(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 same_name prefix_group=test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group == self.test_group1

    def test_type_specified_3(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 unit=same_name test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group == self.test_group1

    def test_type_specified_4(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 same_name test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group == self.test_group1

    def test_type_specified_set_group_none_1(self):
        self.test_unit1b.valid_prefix_group = self.test_group1
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 unit=same_name prefix_group=none",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "none" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group is None

    def test_type_specified_set_group_none_2(self):
        self.test_unit1b.valid_prefix_group = self.test_group1
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 same_name prefix_group=none",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "none" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group is None

    def test_type_specified_set_group_none_3(self):
        self.test_unit1b.valid_prefix_group = self.test_group1
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 unit=same_name none",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "none" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group is None

    def test_type_specified_set_group_none_4(self):
        self.test_unit1b.valid_prefix_group = self.test_group1
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group type=test_type1 same_name none",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "none" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1b" unit' in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group is None

    def test_blank_message(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "convert unit prefix group")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "you must specify both a unit name and a prefix group to set"
            in data[0].text.lower()
        )

    def test_one_word_1(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit prefix group unit1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "you must specify both a unit name and a prefix group to set"
            in data[0].text.lower()
        )

    def test_one_word_2(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "you must specify both a unit name and a prefix group to set"
            in data[0].text.lower()
        )

    def test_no_args_specified_1(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit1a test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1a" unit' in data[0].text.lower()
        assert self.test_unit1a.valid_prefix_group is self.test_group1

    def test_no_args_specified_2(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group test_group1 unit1a",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit1a" unit' in data[0].text.lower()
        assert self.test_unit1a.valid_prefix_group is self.test_group1

    def test_unit_specified_1(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=unit2a test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit2a" unit' in data[0].text.lower()
        assert self.test_unit2a.valid_prefix_group is self.test_group1

    def test_unit_specified_2(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=unit2a group=test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "test_group1" as the prefix group' in data[0].text.lower()
        assert 'for the "unit2a" unit' in data[0].text.lower()
        assert self.test_unit2a.valid_prefix_group is self.test_group1

    def test_extra_word_split(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit1a test_group1 blah",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "could not parse where unit name ends and prefix group begins"
            in data[0].text.lower()
        )
        assert (
            "please specify with unit=<name> prefix_group=<name>"
            in data[0].text.lower()
        )
        assert self.test_unit1a.valid_prefix_group is None

    def test_ambiguous_unit(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=same_name test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unit name is too ambiguous" in data[0].text.lower()
        assert "please specify with unit= and type=" in data[0].text.lower()
        assert self.test_unit1b.valid_prefix_group is None
        assert self.test_unit2b.valid_prefix_group is None

    def test_prefix_group_none_1(self):
        self.test_unit2b.valid_prefix_group = self.test_group1
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=unit2b none",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "none" as the prefix group' in data[0].text.lower()
        assert 'for the "unit2b" unit' in data[0].text.lower()
        assert self.test_unit2b.valid_prefix_group is None

    def test_prefix_group_none_2(self):
        self.test_unit2b.valid_prefix_group = self.test_group1
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=unit2b prefixes=none",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'set "none" as the prefix group' in data[0].text.lower()
        assert 'for the "unit2b" unit' in data[0].text.lower()
        assert self.test_unit2b.valid_prefix_group is None

    def test_unknown_group(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=unit2b 'prefix group'='no group'",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "prefix group not recognised" in data[0].text.lower()
        assert self.test_unit2b.valid_prefix_group is None

    def test_unknown_unit(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit prefix group unit=no_unit group=test_group1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no unit found by that name" in data[0].text.lower()
