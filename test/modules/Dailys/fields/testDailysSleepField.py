import unittest

from Events import EventMessage
from modules.Dailys import DailysSleepField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysSleepFieldTest(TestBase, unittest.TestCase):

    def test_create_from_input_col_found(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col: "sleep times", "AG": "world"})
        # Create from input
        field = DailysSleepField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns

    def test_create_from_input_col_specified(self):
        # Setup
        col = "AF"
        cmd_name = "setup dailys field"
        cmd_args = "sleep {}".format(col)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysSleepField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns

    def test_create_from_input_col_not_found(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", "AF": "wonderful", "AG": "world"})
        # Create from input
        try:
            DailysSleepField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a column."

    def test_create_from_input_col_not_unique(self):
        # Setup
        col1 = "AF"
        col2 = "AG"
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col1: "sleep",
                                                        col2: "sleep times", "AH": "world"})
        # Create from input
        try:
            DailysSleepField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to find suitable column title."
        except DailysException as e:
            assert "could not find" in str(e).lower(), "Exception didn't tell me it couldn't find a unique column."

    def test_telegram_time(self):
        pass

    def test_now_time(self):
        pass

    def test_sleep_wake(self):
        pass

    def test_sleep_midnight_wake(self):
        pass

    def test_midnight_sleep_wake(self):
        pass

    def test_sleep_wake_sleep_wake(self):
        pass

    def test_two_interruptions(self):
        pass

    def test_sleep_wake_sleep_midnight_wake(self):
        pass

    def test_sleep_wake_midnight_sleep_wake(self):
        pass

    def test_sleep_midnight_wake_sleep_wake(self):
        pass
