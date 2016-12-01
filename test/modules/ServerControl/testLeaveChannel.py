import unittest

import time

from test.TestBase import TestBase


class LeaveChannelTest(TestBase, unittest.TestCase):

    def test_no_args(self):
        self.function_dispatcher.dispatch("leave", self.test_user, self.test_chan)
        time.sleep(5)
        data = self.server.get_send_data(2)
        time.sleep(5)
        assert data[0][1] is None
        assert data[1][1] == self.test_chan

    def test_channel_name(self):
        self.function_dispatcher.dispatch("leave "+self.test_chan.get_name(), self.test_user, self.test_chan)
        time.sleep(5)
        data = self.server.get_send_data(2)
        time.sleep(5)
        assert data[0][1] is None
        assert data[1][1] == self.test_chan
