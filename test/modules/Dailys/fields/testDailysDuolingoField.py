import json
import unittest
from datetime import timedelta

from Events import EventMessage, EventDay
from modules.Dailys import DailysException, DailysDuolingoField
from modules.UserData import UserDataParser, FAKeyData
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysDuolingoFieldTest(TestBase, unittest.TestCase):
    TEST_USERNAME = "Deer-Spangle"

    def test_day_rollover(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysDuolingoField(spreadsheet, spreadsheet.test_column_key, self.TEST_USERNAME)
        # Send a new day event
        evt = EventDay()
        field.passive_trigger(evt)
        assert evt.get_send_time().date() not in spreadsheet.saved_data
        notif_str = spreadsheet.saved_data[evt.get_send_time().date()-timedelta(1)]
        notif_dict = json.loads(notif_str)
        assert len(notif_dict) > 0, "No results appeared in dict."
        for key in notif_dict:
            assert isinstance(notif_dict[key], int), "Value for {} is not an int.".format(key)
        # Check sent data
        assert len(self.server.send_data) == 1
        assert isinstance(self.server.send_data[0], EventMessage)
        assert self.server.send_data[0].text == notif_str
        assert self.server.send_data[0].channel == self.test_chan
        assert self.server.send_data[0].user == self.test_user

    def test_create_from_input_no_username(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        try:
            DailysDuolingoField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysDuolingoField due to missing username."
        except DailysException as e:
            assert "provide your duolingo username" in str(e).lower(), \
                "Exception did not mention that there was no username specified."

    def test_create_from_input_with_column_specified(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {} {}".format(self.TEST_USERNAME, col)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns
        assert field.username == self.TEST_USERNAME

    def test_create_from_input_with_column_specified_first(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {} {}".format(col, self.TEST_USERNAME)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns
        assert field.username == self.TEST_USERNAME

    def test_create_from_input_with_column_found(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {}".format(self.TEST_USERNAME)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col: "duolingo", "AG": "world"})
        # Create from input
        field = DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns
        assert field.username == self.TEST_USERNAME

    def test_create_from_input_with_column_not_found(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {}".format(self.TEST_USERNAME)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", "AF": "wonderful", "AG": "world"})
        # Setup an FA key, doesn't matter if it works
        udp = UserDataParser()
        key = FAKeyData("cookie_a", "cookie_b")
        udp.set_user_data(self.test_user, key)
        # Create from input
        try:
            DailysDuolingoField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a column."

    def test_create_from_input_with_column_not_unique(self):
        # Setup
        col1 = "AF"
        col2 = "AG"
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {}".format(self.TEST_USERNAME)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col1: "duolingo",
                                                        col2: "duolingo", "AH": "world"})
        # Create from input
        try:
            DailysDuolingoField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a unique column."
