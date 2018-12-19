import json
import os
import unittest

from Events import EventMessage, EventDay
from modules.Dailys import DailysFAField, DailysException
from modules.UserData import UserDataParser, FAKeyData
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysFAFieldTest(TestBase, unittest.TestCase):

    def test_day_rollover_no_data(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysFAField(spreadsheet, spreadsheet.test_column_key)
        # Send a new day event
        try:
            field.passive_trigger(EventDay())
            assert False, "Should have failed to check FA data."
        except DailysException as e:
            assert "no fa data" in str(e).lower(), "Exception should say there's no FA data."

    def test_day_rollover(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup FA key
        udp = UserDataParser()
        key = FAKeyData(os.getenv("test_cookie_a"), os.getenv("test_cookie_b"))
        udp.set_user_data(self.test_user, key)
        # Setup field
        field = DailysFAField(spreadsheet, spreadsheet.test_column_key)
        # Send a new day event
        field.passive_trigger(EventDay())
        assert 0 not in spreadsheet.saved_data
        notif_str = spreadsheet.saved_data[-1]
        notif_dict = json.loads(notif_str)
        assert "submissions" in notif_dict
        assert "comments" in notif_dict
        assert "journals" in notif_dict
        assert "favourites" in notif_dict
        assert "watches" in notif_dict
        assert "notes" in notif_dict
        assert len(self.server.send_data) == 1
        assert isinstance(self.server.send_data[0], EventMessage)
        assert self.server.send_data[0].text == notif_str
        assert self.server.send_data[0].channel == self.test_chan
        assert self.server.send_data[0].user == self.test_user

    def test_create_from_input_no_fa_data(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "furaffinity AF"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        try:
            DailysFAField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysFAField due to missing FA login info."
        except DailysException as e:
            assert "no fa data" in str(e).lower(), "Exception did not mention that there was no FA data set up."

    def test_create_from_input_with_column_specified(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "furaffinity {}".format(col)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup an FA key, doesn't matter if it works
        udp = UserDataParser()
        key = FAKeyData("cookie_a", "cookie_b")
        udp.set_user_data(self.test_user, key)
        # Create from input
        field = DailysFAField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns

    def test_create_from_input_with_column_found(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "furaffinity"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col: "furaffinity", "AG": "world"})
        # Setup an FA key, doesn't matter if it works
        udp = UserDataParser()
        key = FAKeyData("cookie_a", "cookie_b")
        udp.set_user_data(self.test_user, key)
        # Create from input
        field = DailysFAField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns

    def test_create_from_input_with_column_not_found(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "furaffinity"
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
            DailysFAField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a column."

    def test_create_from_input_with_column_not_unique(self):
        # Setup
        col1 = "AF"
        col2 = "AG"
        cmd_name = "setup dailys field"
        cmd_args = "furaffinity"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col1: "furaffinity",
                                                        col2: "furaffinity", "AH": "world"})
        # Setup an FA key, doesn't matter if it works
        udp = UserDataParser()
        key = FAKeyData("cookie_a", "cookie_b")
        udp.set_user_data(self.test_user, key)
        # Create from input
        try:
            DailysFAField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a unique column."
