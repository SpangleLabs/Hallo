import unittest

from Events import EventMessage, EventMode
from Server import Server
from test.TestBase import TestBase


class SilenceTheRabbleTest(TestBase, unittest.TestCase):

    def test_silence_not_000242(self):
        user = self.server.get_user_by_address("lambdabot".lower(), "lambdabot")
        self.function_dispatcher.dispatch(EventMessage(self.server, None, user, "silence the rabble"))
        data = self.server.get_send_data(1, user, EventMessage)
        assert "error" in data[0].text.lower(), "Silence the rabble function should not be usable by non-000242 users."

    def test_silence_not_irc(self):
        type_original = self.server.type
        try:
            self.server.type = "TEST"
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch(EventMessage(self.server, None, user, "silence the rabble"))
            data = self.server.get_send_data(1, user, EventMessage)
            assert "error" in data[0].text.lower(), "Silence the rabble function should not be usable on " \
                                                    "non-irc servers."
        finally:
            self.server.type = type_original

    def test_silence_not_channel(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch(EventMessage(self.server, None, user, "silence the rabble"))
            data = self.server.get_send_data(1, user, EventMessage)
            assert "error" in data[0].text.lower(), "Silence the rabble function should not work in private message."
        finally:
            self.server.type = type_original

    def test_silence_not_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            chan = self.server.get_channel_by_address("#hallotest".lower(), "#hallotest")
            self.function_dispatcher.dispatch(EventMessage(self.server, chan, user, "silence the rabble"))
            data = self.server.get_send_data(1, chan, EventMessage)
            assert "error" in data[0].text.lower(), "Silence the rabble function should not work in non-ETD channels."
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
            self.function_dispatcher.dispatch(EventMessage(self.server, chan, user, "silence the rabble"))
            data = self.server.get_send_data(6, chan)
            try:
                assert data[0].mode_changes == "-o lambdabot"
                assert data[1].mode_changes == "-v lambdabot"
                assert data[2].mode_changes == "-o robot"
                assert data[3].mode_changes == "-v robot"
            except AssertionError:
                assert data[0].mode_changes == "-o robot"
                assert data[1].mode_changes == "-v robot"
                assert data[2].mode_changes == "-o lambdabot"
                assert data[3].mode_changes == "-v lambdabot"
            assert data[0].__class__ == EventMode
            assert data[1].__class__ == EventMode
            assert data[2].__class__ == EventMode
            assert data[3].__class__ == EventMode
            assert data[4].mode_changes == "+m"
            assert data[4].__class__ == EventMode
            assert data[5].text == "I have done your bidding, master."
            assert data[5].__class__ == EventMessage
        finally:
            self.server.type = type_original
