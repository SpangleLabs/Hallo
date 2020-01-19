import unittest

from events import EventMessage
from test.modules.Convert.convert_function_test_base import ConvertFunctionTestBase


class ConvertUnitRemoveNameTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_invalid_type_specified(self):
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user,
            "convert unit remove name type=new_type unit=unit1a del=added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "invalid type specified" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_no_units_match_specified_unit_and_specified_del_name_1(self):
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1a remove=not_a_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_no_units_match_specified_unit_and_specified_del_name_2(self):
        self.test_unit1a.add_name("added_name")
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1aa remove=added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_no_units_match_specified_unit_and_specified_del_name_3(self):
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1aa remove=not_a_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_no_units_match_specified_del_name(self):
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name remove=not_a_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()

    def test_no_units_match_specified_unit_and_del_name_1(self):
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1a not_a_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_no_units_match_specified_unit_and_del_name_2(self):
        self.test_unit1a.add_name("added_name")
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1aa added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_no_units_match_specified_unit_and_del_name_3(self):
        names1a = len(self.test_unit1a.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1aa not_a_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "there are no units matching that description" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == names1a

    def test_multiple_units_match_name(self):
        names1b = len(self.test_unit1b.name_list)
        names2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name del=same_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "it is ambiguous which unit you refer to" in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b
        assert len(self.test_unit2b.name_list) == names2b

    def test_cant_remove_last_name(self):
        assert len(self.test_unit1a.name_list) == 1
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name del=unit1a"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unit only has 1 name" in data[0].text.lower()
        assert "cannot remove its last name" in data[0].text.lower()
        assert len(self.test_unit1a.name_list) == 1

    def test_remove_by_just_del_name_1(self):
        names1b = len(self.test_unit1b.name_list)
        fallback_name = self.test_unit1b.name_list[1]
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name del=unit1b"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed name \"unit1b\"" in data[0].text.lower()
        assert "from \"{}\" unit".format(fallback_name) in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b - 1

    def test_remove_by_just_del_name_2(self):
        names1b = len(self.test_unit1b.name_list)
        fallback_name = self.test_unit1b.name_list[1]
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit1b"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed name \"unit1b\"" in data[0].text.lower()
        assert "from \"{}\" unit".format(fallback_name) in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b - 1

    def test_remove_by_unit_and_del_name_1(self):
        self.test_unit1b.add_name("added_name")
        names1b = len(self.test_unit1b.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1b del=added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed name \"added_name\"" in data[0].text.lower()
        assert "from \"unit1b\" unit" in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b - 1

    def test_remove_by_unit_and_del_name_2(self):
        self.test_unit1b.add_name("added_name")
        names1b = len(self.test_unit1b.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit1b del=added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed name \"added_name\"" in data[0].text.lower()
        assert "from \"unit1b\" unit" in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b - 1

    def test_remove_by_unit_and_del_name_3(self):
        self.test_unit1b.add_name("added_name")
        names1b = len(self.test_unit1b.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=unit1b added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed name \"added_name\"" in data[0].text.lower()
        assert "from \"unit1b\" unit" in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b - 1

    def test_remove_by_unit_and_del_name_specifying_type(self):
        self.test_unit1b.add_name("added_name")
        self.test_unit2b.add_name("added_name")
        names1b = len(self.test_unit1b.name_list)
        names2b = len(self.test_unit2b.name_list)
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user, "convert unit remove name unit=same_name del=added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "it is ambiguous which unit you refer to" in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b
        assert len(self.test_unit2b.name_list) == names2b
        self.function_dispatcher.dispatch(EventMessage(
            self.server, None, self.test_user,
            "convert unit remove name type=test_type1 unit=same_name del=added_name"
        ))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "removed name \"added_name\"" in data[0].text.lower()
        assert "from \"unit1b\" unit" in data[0].text.lower()
        assert len(self.test_unit1b.name_list) == names1b - 1
        assert len(self.test_unit2b.name_list) == names2b
