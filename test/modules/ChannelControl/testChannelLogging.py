import unittest

from Server import Server
from test.TestBase import TestBase


class ChannelLoggingTest(TestBase, unittest.TestCase):

    def test_logs_toggle(self):
        self.test_chan.logging = False
        self.function_dispatcher.dispatch("channel logging", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "toggle" in data[0][0].lower()
        assert self.test_chan.logging
        # Try toggling again
        self.function_dispatcher.dispatch("channel logging", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "toggle" in data[0][0].lower()
        assert not self.test_chan.logging

    def test_logs_on(self):
        self.test_chan.logging = False
        self.function_dispatcher.dispatch("channel logging on", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "logging set on" in data[0][0].lower()
        assert self.test_chan.logging

    def test_logs_off(self):
        self.test_chan.logging = True
        self.function_dispatcher.dispatch("channel logging off", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "logging set off" in data[0][0].lower()
        assert not self.test_chan.logging

    def test_logs_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = False
        self.function_dispatcher.dispatch("channel logging other_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "toggle" in data[0][0].lower()
        assert test_chan1.logging
        # Try toggling again
        self.function_dispatcher.dispatch("channel logging other_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "toggle" in data[0][0].lower()
        assert not test_chan1.logging

    def test_logs_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = False
        self.function_dispatcher.dispatch("channel logging other_channel on", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "logging set on" in data[0][0].lower()
        assert test_chan1.logging

    def test_logs_channel_off(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = True
        self.function_dispatcher.dispatch("channel logging other_channel off", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "logging set off" in data[0][0].lower()
        assert not test_chan1.logging

    def test_logs_on_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = False
        self.function_dispatcher.dispatch("channel logging on other_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "logging set on" in data[0][0].lower()
        assert test_chan1.logging

    def test_logs_off_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = True
        self.function_dispatcher.dispatch("channel logging off other_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "logging set off" in data[0][0].lower()
        assert not test_chan1.logging

    def test_logs_not_in_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.logging = False
        self.function_dispatcher.dispatch("channel logging other_channel", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert not test_chan1.logging

    def test_logs_not_in_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.logging = False
        self.function_dispatcher.dispatch("channel logging other_channel on", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert not test_chan1.logging

    def test_logs_no_bool(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.logging = False
        self.function_dispatcher.dispatch("channel logging other_channel word", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert not test_chan1.logging
