import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class OperatorTest(TestBase, unittest.TestCase):

    def test_op_not_irc(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = "NOT_IRC"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        chan1.add_user(user1)
        chan1.add_user(serv1.get_user_by_name(serv1.get_nick()))
        try:
            self.function_dispatcher.dispatch("op", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "only available for irc" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_0_privmsg(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        chan1.add_user(user1)
        chan1.add_user(serv1.get_user_by_name(serv1.get_nick()))
        try:
            self.function_dispatcher.dispatch("op", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "in a privmsg" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_0_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        chan1.add_user(user1)
        chan1.add_user(serv1.get_user_by_name(serv1.get_nick()))
        try:
            self.function_dispatcher.dispatch("op", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_0(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan1.name+" +o "+user1.name in data[0][0]
            assert "status given" in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1priv_not_in_channel(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op other_channel", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "not in that channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1priv_user_not_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_chan1", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "you are not in that channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1priv_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch("op test_chan1", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1priv(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_chan1", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan1.name+" +o "+user1.name in data[0][0]
            assert "status given" in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1_chan_user_not_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user2)
        chan2.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_user2 = chan2.get_membership_by_user(user2)
        chan2_user2.is_op = False
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_chan2", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "you are not in that channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1_chan_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user1)
        chan2.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_user1 = chan2.get_membership_by_user(user1)
        chan2_user1.is_op = False
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch("op test_chan2", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1_chan(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user1)
        chan2.add_user(user_hallo)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_user1 = chan2.get_membership_by_user(user1)
        chan2_user1.is_op = False
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_chan2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan2.name+" +o "+user1.name in data[0][0]
            assert "status given" in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1_user_not_here(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_user2", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "user is not in this channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1_user_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        chan1.add_user(user2)
        chan1_user2 = chan1.get_membership_by_user(user2)
        chan1_user2.is_op = False
        try:
            self.function_dispatcher.dispatch("op test_user2", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_1_user(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan1.add_user(user2)
        chan1_user2 = chan1.get_membership_by_user(user2)
        chan1_user2.is_op = False
        try:
            self.function_dispatcher.dispatch("op test_user2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan1.name+" +o "+user2.name in data[0][0]
            assert "status given" in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_2_chan_user_not_there(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_chan2 test_user3", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "test_user3 is not in test_chan2" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_2_chan_no_power(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch("op test_chan2 test_user2", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_2_chan(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("op test_chan2 test_user2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "MODE"
            assert chan2.name+" +o "+user2.name in data[0][0]
            assert "status given" in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_2_user_not_in_channel(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = False
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1_user1 = chan1.get_membership_by_user(user1)
        chan1_user1.is_op = False
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2_user1 = chan2.get_membership_by_user(user2)
        chan2_user1.is_op = False
        try:
            self.function_dispatcher.dispatch("op test_chan2 test_user2", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "i'm not in that channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_op_2_user_user_not_there(self):
        pass

    def test_op_2_user_no_power(self):
        pass

    def test_op_2_user(self):
        pass
