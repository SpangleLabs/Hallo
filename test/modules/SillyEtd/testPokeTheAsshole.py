import unittest

from Server import Server
from test.TestBase import TestBase


class PokeTheAssholeTest(TestBase, unittest.TestCase):

    def test_poke_not_000242(self):
        user = self.server.get_user_by_name("lambdabot")
        self.function_dispatcher.dispatch("poke the asshole", user, user)
        data = self.server.get_send_data(1, user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Poke the asshole function should not be usable by non-000242 users."

    def test_poke_not_irc(self):
        self.server.type = "TEST"
        user = self.server.get_user_by_name("TEST000242")
        self.function_dispatcher.dispatch("poke the asshole", user, user)
        data = self.server.get_send_data(1, user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Poke the asshole function should not be usable on non-irc servers."

    def test_poke_not_channel(self):
        self.server.type = Server.TYPE_IRC
        user = self.server.get_user_by_name("TEST000242")
        self.function_dispatcher.dispatch("poke the asshole", user, user)
        data = self.server.get_send_data(1, user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Poke the asshole function should not work in private message."

    def test_poke_not_etd(self):
        self.server.type = Server.TYPE_IRC
        user = self.server.get_user_by_name("TEST000242")
        chan = self.server.get_channel_by_name("#hallotest")
        self.function_dispatcher.dispatch("poke the asshole", user, chan)
        data = self.server.get_send_data(1, chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Poke the asshole function should not work in non-ETD channels."

    def test_poke_etd(self):
        self.server.type = Server.TYPE_IRC
        user = self.server.get_user_by_name("TEST000242")
        chan = self.server.get_channel_by_name("#ecco-the-dolphin")
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
