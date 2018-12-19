import unittest

from Events import EventMessage
from modules.Dailys import DailysFAField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysFAFieldTest(TestBase, unittest.TestCase):

    def test_day_rollover(self):
        pass

    def test_create_from_input_no_fa_data(self):
        # Setup
        evt = EventMessage(self.server, self.test_chan, self.test_user, "setup FA dailys field")
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        try:
            DailysFAField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysFAField due to missing FA login info."
        except DailysException as e:
            assert "no fa data" in str(e).lower(), "Exception did not mention that there was no FA data set up."

    def test_create_from_input_with_column_specified(self):
        pass

    def test_create_from_input_with_column_found(self):
        pass

    def test_create_from_input_with_column_not_found(self):
        pass
