import unittest

from Events import EventMessage
from Server import Server
from test.TestBase import TestBase


class AlarmTest(TestBase, unittest.TestCase):

    def test_alarm_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "alarm"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "wooo" in data[0].text.lower(), "Alarm function not going woo."

    def test_alarm_word(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "alarm nerd"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "wooo" in data[0].text.lower(), "Alarm function not going woo."
        assert "nerd" in data[0].text.lower(), "Alarm function not going responding with word input."
