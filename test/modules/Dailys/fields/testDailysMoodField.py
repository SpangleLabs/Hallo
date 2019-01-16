import unittest

from Events import EventMessage
from modules.Dailys import DailysMoodField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysMoodFieldTest(TestBase, unittest.TestCase):

    def test_create_from_input_no_args(self):
        # Setup stuff
        command_name = "setup dailys field"
        command_args = "mood"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_chan, self.test_user)
        # Try and create dailys field
        try:
            DailysMoodField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysMoodField"
        except DailysException as e:
            assert "must contain" in str(e).lower()
            assert "times" in str(e).lower()
            assert "mood measurements" in str(e).lower()

    def test_create_from_input_no_semicolon(self):
        # Setup stuff
        pass

    def test_create_from_input_one_semicolon(self):
        pass

    def test_create_from_input_with_col_title(self):
        pass

    def test_create_from_input_col_not_found(self):
        pass

    def test_create_from_input_col_found(self):
        pass

    def test_create_from_input_invalid_time(self):
        pass

    def test_create_from_input_not_a_time(self):
        pass

    def test_trigger_morning_query(self):
        pass

    def test_trigger_sleep_query(self):
        pass

    def test_trigger_sleep_no_query_if_already_given(self):
        pass

    def test_trigger_sleep_after_midnight(self):
        pass

    def test_trigger_time_exactly_once(self):
        pass

    def test_process_reply_to_query(self):
        pass

    def test_process_most_recent_query(self):
        pass

    def test_process_most_recent_sleep_query_after_midnight(self):
        pass

    def test_process_no_mood_query(self):
        pass

    def test_process_time_specified(self):
        pass

    def test_process_wake_specified(self):
        pass
