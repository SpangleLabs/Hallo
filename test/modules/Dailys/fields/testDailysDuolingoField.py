import json
import unittest
from datetime import timedelta

from Events import EventMessage, EventDay
from modules.Dailys import DailysException, DailysDuolingoField
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysDuolingoFieldTest(TestBase, unittest.TestCase):
    TEST_USERNAME = "Deer-Spangle"

    def test_day_rollover(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysDuolingoField(spreadsheet, self.TEST_USERNAME)
        # Send a new day event
        evt = EventDay()
        field.passive_trigger(evt)
        assert field.type_name not in spreadsheet.saved_data or evt.get_send_time().date() not in spreadsheet.saved_data[field.type_name]
        notif_str = spreadsheet.saved_data[field.type_name][evt.get_send_time().date()-timedelta(1)]
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
            assert "could not find a duolingo account with that username" in str(e).lower(), \
                "Exception did not mention that there was no username specified."

    def test_create_from_input(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {}".format(self.TEST_USERNAME)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.username == self.TEST_USERNAME
