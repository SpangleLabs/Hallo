import unittest

from events import EventMessage
from test.test_base import TestBase


class ChangeOptionsTest(TestBase, unittest.TestCase):

    def test_change_options_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "change options 5"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "[5]" in data[0].text, "Option missing from results."
        assert "[2,2,1]" in data[0].text, "Option missing from results."
        assert "[2,1,1,1]" in data[0].text, "Option missing from results."
        assert "[1,1,1,1,1]" in data[0].text, "Option missing from results."

    def test_change_options_over_limit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "change options 21"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Change options size limit has not been enforced."

    def test_change_options_negative(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "change options -5"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Change options should fail with negative input."

    def test_change_options_float(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "change option 2.3"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Change options should fail with non-integer input."
