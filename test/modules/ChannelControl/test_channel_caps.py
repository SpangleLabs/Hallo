import unittest

from events import EventMessage
from test.test_base import TestBase


class ChannelCapsTest(TestBase, unittest.TestCase):

    def test_caps_toggle(self):
        self.test_chan.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "channel caps"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert self.test_chan.use_caps_lock
        # Try toggling again
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "channel caps"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert not self.test_chan.use_caps_lock

    def test_caps_on(self):
        self.test_chan.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "channel caps on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "caps lock set on" in data[0].text.lower()
        assert self.test_chan.use_caps_lock

    def test_caps_off(self):
        self.test_chan.use_caps_lock = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "channel caps off"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "caps lock set off" in data[0].text.lower()
        assert not self.test_chan.use_caps_lock

    def test_caps_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert test_chan1.use_caps_lock
        # Try toggling again
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "toggle" in data[0].text.lower()
        assert not test_chan1.use_caps_lock

    def test_caps_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "caps lock set on" in data[0].text.lower()
        assert test_chan1.use_caps_lock

    def test_caps_channel_off(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.use_caps_lock = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel off"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "caps lock set off" in data[0].text.lower()
        assert not test_chan1.use_caps_lock

    def test_caps_on_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps on other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "caps lock set on" in data[0].text.lower()
        assert test_chan1.use_caps_lock

    def test_caps_off_channel(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = True
        test_chan1.use_caps_lock = True
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps off other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "caps lock set off" in data[0].text.lower()
        assert not test_chan1.use_caps_lock

    def test_caps_not_in_channel_toggle(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.use_caps_lock

    def test_caps_not_in_channel_on(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel on"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.use_caps_lock

    def test_caps_no_bool(self):
        test_chan1 = self.server.get_channel_by_address("other_channel".lower(), "other_channel")
        test_chan1.in_channel = False
        test_chan1.use_caps_lock = False
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "channel caps other_channel word"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert not test_chan1.use_caps_lock