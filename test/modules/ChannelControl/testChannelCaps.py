import unittest

from Server import Server
from test.TestBase import TestBase


class ChannelCapsTest(TestBase, unittest.TestCase):

    def test_caps_toggle(self):
        self.test_chan.use_caps_lock = False
        self.function_dispatcher.dispatch("channel caps", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "toggle" in data[0][0].lower()
        assert self.test_chan.use_caps_lock
        # Try toggling again
        self.function_dispatcher.dispatch("channel caps", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "toggle" in data[0][0].lower()
        assert not self.test_chan.use_caps_lock

    def test_caps_on(self):
        self.test_chan.use_caps_lock = False
        self.function_dispatcher.dispatch("channel caps on", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "caps lock set on" in data[0][0].lower()
        assert self.test_chan.use_caps_lock

    def test_caps_off(self):
        self.test_chan.use_caps_lock = True
        self.function_dispatcher.dispatch("channel caps off", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "caps lock set off" in data[0][0].lower()
        assert not self.test_chan.use_caps_lock

    def test_caps_channel_toggle(self):
        pass

    def test_caps_channel_bool(self):
        pass

    def test_caps_bool_channel(self):
        pass
