import unittest

from Events import EventMessage
from modules.Dailys import DailysFAField, DailysException
from modules.UserData import UserDataParser, FAKeyData
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysFAFieldTest(TestBase, unittest.TestCase):

    def test_day_rollover(self):
        pass

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
        cmd_name = "setup dailys field"
        cmd_args = "furaffinity AF"
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

    def test_create_from_input_with_column_found(self):
        pass

    def test_create_from_input_with_column_not_found(self):
        pass
