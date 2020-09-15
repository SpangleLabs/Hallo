import unittest

from hallo.events import EventMessage
from hallo.test.modules.convert.convert_function_test_base import ConvertFunctionTestBase


class ConvertUnitAddNameTest(ConvertFunctionTestBase, unittest.TestCase):
    def test_specify_invalid_type(self):
        names_1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit add name type=new_type unit=unit1a new_name",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised type" in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a
        ), "Shouldn't have added new name"

    def test_specified_unit_wrong(self):
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit add name type=test_type1 unit=new_unit new_name",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no unit found by that name" in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a
        ), "Shouldn't have added new name anywhere"
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name anywhere"

    def test_specified_unit_ambiguous(self):
        names_1b = len(self.test_unit1b.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit add name unit=same_name new_name",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unit name is too ambiguous" in data[0].text.lower()
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name anywhere"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name anywhere"

    def test_specified_unit_ambiguous_but_type_specified(self):
        names_1b = len(self.test_unit1b.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit add name type=test_type1 unit=same_name new_name",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "new_name"' in data[0].text.lower()
        assert 'the "unit1b" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1b.name_list) == names_1b + 1
        ), "Should have added new name to type1 same_name"
        assert "new_name" in self.test_unit1b.name_list
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to type2 same_name"

    def test_specified_new_name(self):
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit add name unit=unit1a new_name=u1a",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_specified_new_name_not_unit(self):
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                'convert unit add name unit1a "new name"=u1a',
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_new_name_first(self):
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name u1a unit1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_new_name_last(self):
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name unit1a u1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_multi_word_new_name(self):
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name unit1a u 1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u 1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u 1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_multi_word_unit(self):
        # Add name with a space in it for unit1a
        self.test_unit1a.add_name("unit 1a")
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        # Check it works
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name unit 1a u1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_multi_word_unit_and_new_name(self):
        # Add name with a space in it for unit1a
        self.test_unit1a.add_name("unit 1a")
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        names_2a = len(self.test_unit2a.name_list)
        names_2b = len(self.test_unit2b.name_list)
        # Check it works
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name unit 1a u 1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert 'added "u 1a"' in data[0].text.lower()
        assert 'the "unit1a" unit' in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a + 1
        ), "Should have added new name to unit1a"
        assert "u 1a" in self.test_unit1a.name_list
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"
        assert (
            len(self.test_unit2a.name_list) == names_2a
        ), "Shouldn't have added new name to unit2a"
        assert (
            len(self.test_unit2b.name_list) == names_2b
        ), "Shouldn't have added new name to unit2b"

    def test_multi_word_ambiguous(self):
        # Setup 'unit1a second' as alt name for unit1b
        self.test_unit1b.add_name("unit1a second")
        names_1a = len(self.test_unit1a.name_list)
        names_1b = len(self.test_unit1b.name_list)
        # Check it fails to find correct unit
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert unit add name unit1a second new name",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "could not parse where unit name ends and new name begins"
            in data[0].text.lower()
        )
        assert "please specify with unit=<name>" in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a
        ), "Shouldn't have added new name to unit1a"
        assert (
            len(self.test_unit1b.name_list) == names_1b
        ), "Shouldn't have added new name to unit1b"

    def test_no_new_name(self):
        names_1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name unit1a"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "must specify both a unit name and a new name" in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a
        ), "Shouldn't have added any new name to unit1a"

    def test_no_new_name_specified(self):
        names_1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert unit add name unit1a new="
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "new name cannot be blank" in data[0].text.lower()
        assert (
            len(self.test_unit1a.name_list) == names_1a
        ), "Shouldn't have added any new name to unit1a"
