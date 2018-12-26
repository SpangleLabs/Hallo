from Events import EventMessage
from modules.Dailys import DailysMoodField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysMoodFieldTest(unittest.TestCase, TestBase):

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

    def test_create_from_input_2_args(self):
        # Setup stuff
        pass
