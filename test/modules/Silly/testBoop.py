import unittest

from Server import Server
from test.TestBase import TestBase


class BoopTest(TestBase, unittest.TestCase):

    def test_boop_blank(self):
        self.function_dispatcher.dispatch("boop", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Boop function should return error if no arguments given."

    def test_boop_user(self):
        self.test_user2 = self.server.get_user_by_name("another_test")
        self.test_chan.add_user(self.test_user)
        self.test_chan.add_user(self.test_user2)
        self.function_dispatcher.dispatch("boop another_test", self.test_user, self.test_chan)
        data = self.server.get_send_data(2, self.test_chan, Server.MSG_MSG)
        assert data[0][0][0] == data[0][0][-1] == "\x01", "Boop did not send a CTCP message."
        assert "boop" in data[0][0].lower(), "Boop did not boop."
        assert "another_test" in data[0][0].lower(), "Boop did not mention the user to be booped."
        assert "done" in data[1][0].lower(), "Boop did not tell original user it was done."

    def test_boop_user_privmsg(self):
        pass

    def test_boop_user_chan(self):
        pass

    def test_boop_user_not_in_channel(self):
        pass

    def test_boop_user_not_in_specified_channel(self):
        pass
