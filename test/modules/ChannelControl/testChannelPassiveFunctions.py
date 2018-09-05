import unittest

from Events import EventMessage
from test.TestBase import TestBase


class ChannelPassiveFunctionsTest(TestBase, unittest.TestCase):

    def test_passive_toggle(self):
        self.test_chan.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert self.test_chan.passive_enabled
        # Try toggling again
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert not self.test_chan.passive_enabled

    def test_passive_on(self):
        self.test_chan.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "passive functions set enabled" in data[0].text.lower()
        assert self.test_chan.passive_enabled

    def test_passive_off(self):
        self.test_chan.passive_enabled = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions off"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "passive functions set disabled" in data[0].text.lower()
        assert not self.test_chan.passive_enabled

    def test_passive_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert test_chan1.passive_enabled
        # Try toggling again
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert not test_chan1.passive_enabled

    def test_passive_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "passive functions set enabled" in data[0].text.lower()
        assert test_chan1.passive_enabled

    def test_passive_channel_off(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.passive_enabled = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel off"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "passive functions set disabled" in data[0].text.lower()
        assert not test_chan1.passive_enabled

    def test_passive_on_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions on other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "passive functions set enabled" in data[0].text.lower()
        assert test_chan1.passive_enabled

    def test_passive_off_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.passive_enabled = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions off other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "passive functions set disabled" in data[0].text.lower()
        assert not test_chan1.passive_enabled

    def test_passive_not_in_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.passive_enabled

    def test_passive_not_in_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.passive_enabled

    def test_passive_no_bool(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.passive_enabled = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel passive functions other_channel word"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.passive_enabled
