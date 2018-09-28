import unittest

from Events import EventMessage, EventMode
from Server import Server
from test.TestBase import TestBase


class PokeTheAssholeTest(TestBase, unittest.TestCase):

    def test_poke_not_000242(self):
        user = self.server.get_user_by_address("lambdabot".lower(), "lambdabot")
        self.function_dispatcher.dispatch(EventMessage(self.server, None, user, "poke the asshole"))
        data = self.server.get_send_data(1, user, EventMessage)
        assert "error" in data[0].text.lower(), "Poke the asshole function should not be usable by non-000242 users."

    def test_poke_not_irc(self):
        type_original = self.server.type
        try:
            self.server.type = "TEST"
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch(EventMessage(self.server, None, user, "poke the asshole"))
            data = self.server.get_send_data(1, user, EventMessage)
            assert "error" in data[0].text.lower(), "Poke the asshole function should not be usable on non-irc servers."
        finally:
            self.server.type = type_original

    def test_poke_not_channel(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch(EventMessage(self.server, None, user, "poke the asshole"))
            data = self.server.get_send_data(1, user, EventMessage)
            assert "error" in data[0].text.lower(), "Poke the asshole function should not work in private message."
        finally:
            self.server.type = type_original

    def test_poke_not_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            chan = self.server.get_channel_by_address("#hallotest".lower(), "#hallotest")
            self.function_dispatcher.dispatch(EventMessage(self.server, chan, user, "poke the asshole"))
            data = self.server.get_send_data(1, chan, EventMessage)
            assert "error" in data[0].text.lower(), "Poke the asshole function should not work in non-ETD channels."
        finally:
            self.server.type = type_original

    def test_poke_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            chan = self.server.get_channel_by_address("#ecco-the-dolphin".lower(), "#ecco-the-dolphin")
            self.function_dispatcher.dispatch(EventMessage(self.server, chan, user, "poke the asshole"))
            data = self.server.get_send_data(11)  # 11, chan, EventMessage)
            for x in range(10):
                assert data[x].channel == chan, "Ten mode events should have been sent to ETD."
                assert data[x].__class__ == EventMode, "Ten mode events should have been sent to ETD."
                if x % 2 == 0:
                    assert data[x].mode_changes == "+v Dolphin", "Adding voice incorrect."
                else:
                    assert data[x].mode_changes == "-v Dolphin", "Removing voice incorrect."
            assert data[10].text == "Dolphin: You awake yet?", "Final output line incorrect."
            assert data[10].channel == chan, "Final output channel incorrect."
            assert data[10].__class__ == EventMessage, "Final output message type incorrect."
        finally:
            self.server.type = type_original
