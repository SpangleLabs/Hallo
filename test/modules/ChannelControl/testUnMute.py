import unittest

from Events import EventMessage
from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class UnMuteTest(TestBase, unittest.TestCase):

    def test_unmute_not_irc(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = "NOT_IRC"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        chan1.add_user(user1)
        chan1.add_user(serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick()))
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "unmute"))
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "only available for irc" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_privmsg(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "unmute"))
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "can't unset mute on a private message" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_0_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "unmute"))
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_0(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "unmute"))
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan1.name+" -m" in data[0][0]
            assert "set mute in "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_1_not_known(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "unmute test_chan2"))
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "test_chan2 is not known" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_1_not_in_channel(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_address("test_chan2", "test_chan2")
        chan2.in_channel = False
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "unmute test_chan2"))
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "not in that channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_1_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "unmute test_chan1"))
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_unmute_1(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        user_hallo = serv1.get_user_by_address(serv1.get_nick().lower(), serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch(EventMessage(serv1, None, user1, "unmute test_chan1"))
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan1.name+" -m" in data[0][0]
            assert "set mute in "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)
