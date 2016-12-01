import unittest

from Server import Server
from test.TestBase import TestBase


class LeaveChannelTest(TestBase, unittest.TestCase):

    def test_no_args(self):
        self.function_dispatcher.dispatch("leave", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()

    def test_channel_name(self):
        self.function_dispatcher.dispatch("leave "+self.test_chan.name, self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()

    def test_no_args_privmsg(self):
        self.function_dispatcher.dispatch("leave", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        self.server.get_left_channels(0)
        assert "error" in data[0][0].lower()

    def test_other_channel_name(self):
        other = self.server.get_channel_by_name("#other")
        self.function_dispatcher.dispatch("leave "+other.name, self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == other
        assert "left" in data[0][0].lower()
        assert other.name in data[0][0].lower()

    def test_channel_name_privmsg(self):
        self.function_dispatcher.dispatch("leave "+self.test_chan.name, self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        chans = self.server.get_left_channels(1)
        assert chans[0] == self.test_chan
        assert "left" in data[0][0].lower()
        assert self.test_chan.name in data[0][0].lower()

    def test_not_in_channel(self):
        self.function_dispatcher.dispatch("leave #not_in_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        self.server.get_left_channels(0)
        assert "error" in data[0][0].lower()
