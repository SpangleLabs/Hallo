import unittest

from Server import Server
from test.TestBase import TestBase


class AlarmTest(TestBase, unittest.TestCase):

    def test_alarm_simple(self):
        self.function_dispatcher.dispatch("alarm", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "wooo" in data[0][0].lower(), "Alarm function not going woo."

    def test_alarm_word(self):
        self.function_dispatcher.dispatch("alarm nerd", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "wooo" in data[0][0].lower(), "Alarm function not going woo."
        assert "nerd" in data[0][0].lower(), "Alarm function not going responding with word input."
