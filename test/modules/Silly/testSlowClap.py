import unittest

import time

from Server import Server
from test.TestBase import TestBase


class SlowClapTest(TestBase, unittest.TestCase):

    def test_slowclap(self):
        time_start = time.time()
        self.function_dispatcher.dispatch("slowclap", self.test_user, self.test_chan)
        time_end = time.time()
        data = self.server.get_send_data(3, self.test_chan, Server.MSG_MSG)
        assert time_end-time_start > 2, "Slowclap should take at least 2 seconds."
        assert "clap" in data[0][0].lower()
        assert "clap" in data[1][0].lower()
        assert "clap." in data[2][0].lower(), "Final clap needs a fullstop."

    def test_slowclap_privmsg(self):
        time_start = time.time()
        self.function_dispatcher.dispatch("slowclap", self.test_user, self.test_user)
        time_end = time.time()
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert time_end-time_start < 2, "Slowclap error should take less than 2 seconds."
        assert "error" in data[0][0].lower()

    def test_slowclap_chan(self):
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        time_start = time.time()
        self.function_dispatcher.dispatch("slowclap "+test_chan2.name, self.test_user, self.test_user)
        time_end = time.time()
        data = self.server.get_send_data(4, None, Server.MSG_MSG)
        assert time_end-time_start > 2, "Slowclap should take at least 2 seconds."
        assert data[0][1] == test_chan2
        assert data[1][1] == test_chan2
        assert data[2][1] == test_chan2
        assert data[3][1] == self.test_user, "Done response should go to user."
        assert "clap" in data[0][0].lower()
        assert "clap" in data[1][0].lower()
        assert "clap." in data[2][0].lower(), "Final clap needs a fullstop."
        assert "done" in data[3][0].lower(), "Done message should be sent to original user."

    def test_slowclap_chan_not_in_chan(self):
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = False
        time_start = time.time()
        self.function_dispatcher.dispatch("slowclap "+test_chan2.name, self.test_user, self.test_user)
        time_end = time.time()
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert time_end-time_start < 2, "Slowclap error should take less than 2 seconds."
        assert "error" in data[0][0].lower()
