import unittest

from events import EventMessage
from test.test_base import TestBase


class BlankTest(TestBase, unittest.TestCase):

    def test_blank_empty(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, ""))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "yes?" == data[0].text.lower(), "Blank function not working."

    def test_blank_channel(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, ""))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "yes?" == data[0].text.lower(), "Blank function not working in channel."
