import unittest

from Server import Server
from test.TestBase import TestBase


class SilenceTheRabbleTest(TestBase, unittest.TestCase):

    def test_silence_not_000242(self):
        user = self.server.get_user_by_address("lambdabot".lower(), "lambdabot")
        self.function_dispatcher.dispatch("silence the rabble", user, user)
        data = self.server.get_send_data(1, user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Silence the rabble function should not be usable by non-000242 users."

    def test_silence_not_irc(self):
        type_original = self.server.type
        try:
            self.server.type = "TEST"
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch("silence the rabble", user, user)
            data = self.server.get_send_data(1, user, Server.MSG_MSG)
            assert "error" in data[0][0].lower(), "Silence the rabble function should not be usable on non-irc servers."
        finally:
            self.server.type = type_original

    def test_silence_not_channel(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch("silence the rabble", user, user)
            data = self.server.get_send_data(1, user, Server.MSG_MSG)
            assert "error" in data[0][0].lower(), "Silence the rabble function should not work in private message."
        finally:
            self.server.type = type_original

    def test_silence_not_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            chan = self.server.get_channel_by_address("#hallotest".lower(), "#hallotest")
            self.function_dispatcher.dispatch("silence the rabble", user, chan)
            data = self.server.get_send_data(1, chan, Server.MSG_MSG)
            assert "error" in data[0][0].lower(), "Silence the rabble function should not work in non-ETD channels."
        finally:
            self.server.type = type_original

    def test_silence_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            user1 = self.server.get_user_by_address("lambdabot".lower(), "lambdabot")
            user2 = self.server.get_user_by_address("robot".lower(), "robot")
            chan = self.server.get_channel_by_address("#ecco-the-dolphin".lower(), "#ecco-the-dolphin")
            chan.add_user(user)
            chan.add_user(user1)
            chan.add_user(user2)
            self.function_dispatcher.dispatch("silence the rabble", user, chan)
            data = self.server.get_send_data(6)
            try:
                assert data[0][0] == "MODE #ecco-the-dolphin -o lambdabot"
                assert data[1][0] == "MODE #ecco-the-dolphin -v lambdabot"
                assert data[2][0] == "MODE #ecco-the-dolphin -o robot"
                assert data[3][0] == "MODE #ecco-the-dolphin -v robot"
            except AssertionError:
                assert data[0][0] == "MODE #ecco-the-dolphin -o robot"
                assert data[1][0] == "MODE #ecco-the-dolphin -v robot"
                assert data[2][0] == "MODE #ecco-the-dolphin -o lambdabot"
                assert data[3][0] == "MODE #ecco-the-dolphin -v lambdabot"
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_RAW
            assert data[2][2] == Server.MSG_RAW
            assert data[3][2] == Server.MSG_RAW
            assert data[4][0] == "MODE #ecco-the-dolphin +m"
            assert data[4][2] == Server.MSG_RAW
            assert data[5][0] == "I have done your bidding, master."
            assert data[5][1] == chan
            assert data[5][2] == Server.MSG_MSG
        finally:
            self.server.type = type_original
