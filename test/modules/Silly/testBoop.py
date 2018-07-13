import unittest

from Server import Server
from test.TestBase import TestBase


class BoopTest(TestBase, unittest.TestCase):

    def test_boop_blank(self):
        self.function_dispatcher.dispatch("boop", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Boop function should return error if no arguments given."

    def test_boop_user_offline(self):
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = False
        self.test_chan.add_user(self.test_user)
        self.test_chan.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_user_not_in_channel(self):
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        self.test_chan.add_user(self.test_user)
        self.function_dispatcher.dispatch("boop another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_user(self):
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        self.test_chan.add_user(self.test_user)
        self.test_chan.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(2, self.test_chan, Server.MSG_MSG)
        assert data[0][0][0] == data[0][0][-1] == "\x01", "Boop did not send a CTCP message."
        assert "boop" in data[0][0].lower(), "Boop did not boop."
        assert "another_user" in data[0][0].lower(), "Boop did not mention the user to be booped."
        assert "done" in data[1][0].lower(), "Boop did not tell original user it was done."

    def test_boop_user_chan_offline(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = False
        test_chan2.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_user another_chan", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_user_chan_not_in_channel(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        self.function_dispatcher.dispatch("boop another_user another_chan", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_user_chan_hallo_not_in_channel(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = False
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        self.function_dispatcher.dispatch("boop another_user another_chan", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_user_chan_privmsg(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        test_chan2.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_user another_chan", self.test_user, self.test_user)
        data = self.server.get_send_data(2, None, Server.MSG_MSG)
        assert data[0][1] == test_chan2, "Boop did not go to correct channel."
        assert data[1][1] == self.test_user, "Confirmation did not go back to user's privmsg."
        assert data[0][0][0] == data[0][0][-1] == "\x01", "Boop did not send a CTCP message."
        assert "boop" in data[0][0].lower(), "Boop did not boop."
        assert "another_user" in data[0][0].lower(), "Boop did not mention the user to be booped."
        assert "done" in data[1][0].lower(), "Boop did not tell original user it was done."

    def test_boop_user_chan(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        test_chan2.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_user another_chan", self.test_user, self.test_chan)
        data = self.server.get_send_data(2, None, Server.MSG_MSG)
        assert data[0][1] == test_chan2, "Boop did not go to correct channel."
        assert data[1][1] == self.test_chan, "Confirmation did not go back to user's channel."
        assert data[0][0][0] == data[0][0][-1] == "\x01", "Boop did not send a CTCP message."
        assert "boop" in data[0][0].lower(), "Boop did not boop."
        assert "another_user" in data[0][0].lower(), "Boop did not mention the user to be booped."
        assert "done" in data[1][0].lower(), "Boop did not tell original user it was done."

    def test_boop_chan_user_offline(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = False
        test_chan2.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_chan another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_chan_user_not_in_channel(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        self.function_dispatcher.dispatch("boop another_chan another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_chan_user_hallo_not_in_channel(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = False
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        self.function_dispatcher.dispatch("boop another_chan another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_boop_chan_user_privmsg(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        test_chan2.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_chan another_user", self.test_user, self.test_user)
        data = self.server.get_send_data(2, None, Server.MSG_MSG)
        assert data[0][1] == test_chan2, "Boop did not go to correct channel."
        assert data[1][1] == self.test_user, "Confirmation did not go back to user's privmsg."
        assert data[0][0][0] == data[0][0][-1] == "\x01", "Boop did not send a CTCP message."
        assert "boop" in data[0][0].lower(), "Boop did not boop."
        assert "another_user" in data[0][0].lower(), "Boop did not mention the user to be booped."
        assert "done" in data[1][0].lower(), "Boop did not tell original user it was done."

    def test_boop_chan_user(self):
        self.test_chan.add_user(self.test_user)
        test_chan2 = self.server.get_channel_by_address("another_chan".lower(), "another_chan")
        test_chan2.in_channel = True
        test_user2 = self.server.get_user_by_address("another_user", "another_user")
        test_user2.online = True
        test_chan2.add_user(test_user2)
        self.function_dispatcher.dispatch("boop another_chan another_user", self.test_user, self.test_chan)
        data = self.server.get_send_data(2, None, Server.MSG_MSG)
        assert data[0][1] == test_chan2, "Boop did not go to correct channel."
        assert data[1][1] == self.test_chan, "Confirmation did not go back to user's channel."
        assert data[0][0][0] == data[0][0][-1] == "\x01", "Boop did not send a CTCP message."
        assert "boop" in data[0][0].lower(), "Boop did not boop."
        assert "another_user" in data[0][0].lower(), "Boop did not mention the user to be booped."
        assert "done" in data[1][0].lower(), "Boop did not tell original user it was done."
