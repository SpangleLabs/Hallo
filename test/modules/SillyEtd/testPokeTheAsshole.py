import unittest

from Server import Server
from test.TestBase import TestBase


class PokeTheAssholeTest(TestBase, unittest.TestCase):

    def test_poke_not_000242(self):
        user = self.server.get_user_by_address("lambdabot".lower(), "lambdabot")
        self.function_dispatcher.dispatch("poke the asshole", user, user)
        data = self.server.get_send_data(1, user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Poke the asshole function should not be usable by non-000242 users."

    def test_poke_not_irc(self):
        type_original = self.server.type
        try:
            self.server.type = "TEST"
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch("poke the asshole", user, user)
            data = self.server.get_send_data(1, user, Server.MSG_MSG)
            assert "error" in data[0][0].lower(), "Poke the asshole function should not be usable on non-irc servers."
        finally:
            self.server.type = type_original

    def test_poke_not_channel(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            self.function_dispatcher.dispatch("poke the asshole", user, user)
            data = self.server.get_send_data(1, user, Server.MSG_MSG)
            assert "error" in data[0][0].lower(), "Poke the asshole function should not work in private message."
        finally:
            self.server.type = type_original

    def test_poke_not_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            chan = self.server.get_channel_by_address("#hallotest".lower(), "#hallotest")
            self.function_dispatcher.dispatch("poke the asshole", user, chan)
            data = self.server.get_send_data(1, chan, Server.MSG_MSG)
            assert "error" in data[0][0].lower(), "Poke the asshole function should not work in non-ETD channels."
        finally:
            self.server.type = type_original

    def test_poke_etd(self):
        type_original = self.server.type
        try:
            self.server.type = Server.TYPE_IRC
            user = self.server.get_user_by_address("TEST000242".lower(), "TEST000242")
            chan = self.server.get_channel_by_address("#ecco-the-dolphin".lower(), "#ecco-the-dolphin")
            self.function_dispatcher.dispatch("poke the asshole", user, chan)
            data = self.server.get_send_data(11)  # 11, chan, Server.MSG_MSG)
            for x in range(10):
                assert data[x][1] is None, "Ten mode events should have been sent to ETD."
                assert data[x][2] == Server.MSG_RAW, "Ten raw lines should have been sent to ETD."
                if x % 2 == 0:
                    assert data[x][0] == "MODE #ecco-the-dolphin +v Dolphin", "Adding voice incorrect."
                else:
                    assert data[x][0] == "MODE #ecco-the-dolphin -v Dolphin", "Removing voice incorrect."
            assert data[10][0] == "Dolphin: You awake yet?", "Final output line incorrect."
            assert data[10][1] == chan, "Final output channel incorrect."
            assert data[10][2] == Server.MSG_MSG, "Final output message type incorrect."
        finally:
            self.server.type = type_original
