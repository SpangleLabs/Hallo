import unittest

from Server import Server
from test.TestBase import TestBase


class ChannelPasswordTest(TestBase, unittest.TestCase):

    def test_pass_off(self):
        self.test_chan.password = "test_pass"
        self.function_dispatcher.dispatch("channel password", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "password disabled" in data[0][0].lower()
        assert self.test_chan.password is None

    def test_pass_null(self):
        self.test_chan.password = "test_pass"
        self.function_dispatcher.dispatch("channel password none", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "password disabled" in data[0][0].lower()
        assert self.test_chan.password is None

    def test_pass_set(self):
        self.test_chan.password = None
        self.function_dispatcher.dispatch("channel password test_pass", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "password set" in data[0][0].lower()
        assert self.test_chan.password == "test_pass"

    def test_pass_chan_null(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.password = "test_pass"
        self.function_dispatcher.dispatch("channel password other_channel none", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "password disabled" in data[0][0].lower()
        assert "other_channel" in data[0][0].lower()
        assert test_chan1.password is None

    def test_pass_chan_set(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.password = None
        self.function_dispatcher.dispatch("channel password other_channel test_pass", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "password set" in data[0][0].lower()
        assert "other_channel" in data[0][0].lower()
        assert test_chan1.password == "test_pass"
