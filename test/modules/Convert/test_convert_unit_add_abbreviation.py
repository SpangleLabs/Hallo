import unittest

from events import EventMessage
from test.modules.Convert.convert_function_test_base import ConvertFunctionTestBase


class ConvertUnitAddAbbreviationTest(ConvertFunctionTestBase, unittest.TestCase):

    def test_specify_invalid_type(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation type=new_type unit=unit1a abbr"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised type" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a, "Shouldn't have added abbreviation"

    def test_specified_unit_wrong(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user,
                         "convert unit add abbreviation type=test_type1 unit=new_unit abbr"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no unit found by that name" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a, "Shouldn't have added abbreviation anywhere"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation anywhere"

    def test_specified_unit_ambiguous(self):
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit=same_name abbr"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unit name is too ambiguous" in data[0].text.lower()
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation anywhere"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation anywhere"

    def test_specified_unit_ambiguous_but_type_specified(self):
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user,
                         "convert unit add abbreviation type=test_type1 unit=same_name abbr"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"abbr\"" in data[0].text.lower()
        assert "the \"unit1b\" unit" in data[0].text.lower()
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b + 1, "Should have added abbreviation to type1 same_name"
        assert "abbr" in self.test_unit1b.abbr_list[0]
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to type2 same_name"

    def test_specified_abbreviation(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user,
                         "convert unit add abbreviation unit=unit1a abbr=u1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_specified_abbreviation_not_unit(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user,
                         "convert unit add abbreviation unit1a abbr=u1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_abbr_first(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation u1a unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_abbr_last(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit1a u1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_multi_word_abbr(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit1a u 1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u 1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u 1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_multi_word_unit(self):
        # Add name with a space in it for unit1a
        self.test_unit1a.add_name("unit 1a")
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        # Check it works
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit 1a u1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_multi_word_unit_and_abbr(self):
        # Add name with a space in it for unit1a
        self.test_unit1a.add_name("unit 1a")
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        abbr_unit2a = len(self.test_unit1a.abbr_list)
        abbr_unit2b = len(self.test_unit2b.abbr_list)
        # Check it works
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit 1a u 1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "added \"u 1a\"" in data[0].text.lower()
        assert "the \"unit1a\" unit" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a + 1, "Should have added abbreviation to unit1a"
        assert self.test_unit1a.abbr_list[0] == "u 1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"
        assert len(self.test_unit2a.abbr_list) == abbr_unit2a, "Shouldn't have added abbreviation to unit2a"
        assert len(self.test_unit2b.abbr_list) == abbr_unit2b, "Shouldn't have added abbreviation to unit2b"

    def test_multi_word_ambiguous(self):
        # Setup 'unit1a second' as alt name for unit1b
        self.test_unit1b.add_name("unit1a second")
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        abbr_unit1b = len(self.test_unit1b.abbr_list)
        # Check it fails to find correct unit
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit1a second abbr"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "could not parse where unit name ends and abbreviation begins" in data[0].text.lower()
        assert "please specify with unit=<name>" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a, "Shouldn't have added abbreviation to unit1a"
        assert len(self.test_unit1b.abbr_list) == abbr_unit1b, "Shouldn't have added abbreviation to unit1b"

    def test_no_abbreviation(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "must specify both a unit name and an abbreviation" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a, "Shouldn't have added any abbreviation to unit1a"

    def test_no_abbreviation_specified(self):
        abbr_unit1a = len(self.test_unit1a.abbr_list)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert unit add abbreviation unit1a abbr="))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "abbreviation name cannot be blank" in data[0].text.lower()
        assert len(self.test_unit1a.abbr_list) == abbr_unit1a, "Shouldn't have added any abbreviation to unit1a"
