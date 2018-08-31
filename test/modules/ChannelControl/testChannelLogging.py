import unittest

from Events import EventMessage
from test.TestBase import TestBase


class ChannelLoggingTest(TestBase, unittest.TestCase):

    def test_logs_toggle(self):
        self.test_chan.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "channel logging"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert self.test_chan.logging
        # Try toggling again
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "channel logging"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert not self.test_chan.logging

    def test_logs_on(self):
        self.test_chan.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "logging set on" in data[0].text.lower()
        assert self.test_chan.logging

    def test_logs_off(self):
        self.test_chan.logging = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging off"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "logging set off" in data[0].text.lower()
        assert not self.test_chan.logging

    def test_logs_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert test_chan1.logging
        # Try toggling again
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert not test_chan1.logging

    def test_logs_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "logging set on" in data[0].text.lower()
        assert test_chan1.logging

    def test_logs_channel_off(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel off"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "logging set off" in data[0].text.lower()
        assert not test_chan1.logging

    def test_logs_on_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging on other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "logging set on" in data[0].text.lower()
        assert test_chan1.logging

    def test_logs_off_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.logging = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging off other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "logging set off" in data[0].text.lower()
        assert not test_chan1.logging

    def test_logs_not_in_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.logging

    def test_logs_not_in_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.logging

    def test_logs_no_bool(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.logging = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel logging other_channel word"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.logging
