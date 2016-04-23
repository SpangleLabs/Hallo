import unittest

from Server import Server
from test.TestBase import TestBase


class BlankTest(TestBase, unittest.TestCase):

    def test_blank_empty(self):
        self.function_dispatcher.dispatch("", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "yes?" == data[0][0].lower(), "Blank function not working."

    def test_blank_channel(self):
        self.function_dispatcher.dispatch("", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "yes?" == data[0][0].lower(), "Blank function not working in channel."
