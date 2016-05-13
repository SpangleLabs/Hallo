import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class KickTest(TestBase, unittest.TestCase):

    def test_kick_not_irc(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = "NOT_IRC"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        chan1.add_user(user1)
        chan1.add_user(serv1.get_user_by_name(serv1.get_nick()))
        try:
            self.function_dispatcher.dispatch("kick", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "only available for irc" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_0_fail(self):
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
            self.function_dispatcher.dispatch("kick", user1, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "specify a user to kick and/or a channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_1priv_not_in_channel(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        try:
            self.function_dispatcher.dispatch("kick test_chan1", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "not in that channel" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_1priv_user_not_there(self):
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
            self.function_dispatcher.dispatch("kick test_chan1", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert user1.name+" is not in "+chan1.name in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_1priv_no_power(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = False
        try:
            self.function_dispatcher.dispatch("kick test_chan1", user1, user1)
            data = serv1.get_send_data(1, user1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            assert "don't have power" in data[0][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_1priv(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan1", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user1.name in data[0][0]
            assert "kicked "+user1.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_1chan_not_in_channel(self):
        pass

    def test_kick_1chan_user_not_there(self):
        pass

    def test_kick_1chan_no_power(self):
        pass

    def test_kick_1chan(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan2.add_user(user1)
        chan2.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user1.name in data[0][0]
            assert "kicked "+user1.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_1user_not_in_channel(self):
        """Placeholder: Does not make sense, hallo must be in channel to receive message on it."""
        pass

    def test_kick_1user_user_not_there(self):
        pass

    def test_kick_1user_no_power(self):
        pass

    def test_kick_1user(self):
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
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2privchanuser_not_in_channel(self):
        pass

    def test_kick_2privchanuser_user_not_there(self):
        pass

    def test_kick_2privchanuser_no_power(self):
        pass

    def test_kick_2privchanuser(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan1 test_user2", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2privchanmsg_not_in_channel(self):
        pass

    def test_kick_2privchanmsg_user_not_there(self):
        pass

    def test_kick_2privchanmsg_no_power(self):
        pass

    def test_kick_2privchanmsg(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan1 goodbye", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user1.name+" goodbye" in data[0][0]
            assert "kicked "+user1.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2privuserchan_not_in_channel(self):
        pass

    def test_kick_2privuserchan_user_not_there(self):
        pass

    def test_kick_2privuserchan_no_power(self):
        pass

    def test_kick_2privuserchan(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2 test_chan1", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2chanuser_not_in_channel(self):
        pass

    def test_kick_2chanuser_user_not_there(self):
        pass

    def test_kick_2chanuser_no_power(self):
        pass

    def test_kick_2chanuser(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan2 test_user2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user2.name in data[0][0]
            assert "kicked "+user2.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2chanmsg_not_in_channel(self):
        pass

    def test_kick_2chanmsg_user_not_there(self):
        pass

    def test_kick_2chanmsg_no_power(self):
        pass

    def test_kick_2chanmsg(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user1)
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan2 goodbye", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user1.name+" goodbye" in data[0][0]
            assert "kicked "+user1.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2userchan_not_in_channel(self):
        pass

    def test_kick_2userchan_user_not_there(self):
        pass

    def test_kick_2userchan_no_power(self):
        pass

    def test_kick_2userchan(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2 test_chan2", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user2.name in data[0][0]
            assert "kicked "+user2.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_2usermsg_not_in_channel(self):
        """Placeholder: Does not make sense, hallo must be in channel to receive message on it."""
        pass

    def test_kick_2usermsg_user_not_there(self):
        pass

    def test_kick_2usermsg_no_power(self):
        pass

    def test_kick_2usermsg(self):
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
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2 goodbye", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name+" goodbye" in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3privchanusermsg_not_in_channel(self):
        pass

    def test_kick_3privchanusermsg_user_not_there(self):
        pass

    def test_kick_3privchanusermsg_no_power(self):
        pass

    def test_kick_3privchanusermsg(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan1 test_user2 goodbye now", user1, user1)
            data = serv1.get_send_data(2)
            print(data)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name+" goodbye now" in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3privchanmsg_not_in_channel(self):
        pass

    def test_kick_3privchanmsg_user_not_there(self):
        pass

    def test_kick_3privchanmsg_no_power(self):
        pass

    def test_kick_3privchanmsg(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan1 goodbye now", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user1.name+" goodbye now" in data[0][0]
            assert "kicked "+user1.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3privuserchanmsg_not_in_channel(self):
        pass

    def test_kick_3privuserchanmsg_user_not_there(self):
        pass

    def test_kick_3privuserchanmsg_no_power(self):
        pass

    def test_kick_3privuserchanmsg(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user2 = serv1.get_user_by_name("test_user2")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2 test_chan1 goodbye now", user1, user1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == user1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name+" goodbye now" in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3chanusermsg_not_in_channel(self):
        pass

    def test_kick_3chanusermsg_user_not_there(self):
        pass

    def test_kick_3chanusermsg_no_power(self):
        pass

    def test_kick_3chanusermsg(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan2 test_user2 goodbye now", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user2.name+" goodbye now" in data[0][0]
            assert "kicked "+user2.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3chanmsg_not_in_channel(self):
        pass

    def test_kick_3chanmsg_user_not_there(self):
        pass

    def test_kick_3chanmsg_no_power(self):
        pass

    def test_kick_3chanmsg(self):
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        serv1.type = Server.TYPE_IRC
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan1.in_channel = True
        chan2 = serv1.get_channel_by_name("test_chan2")
        chan2.in_channel = True
        user1 = serv1.get_user_by_name("test_user1")
        user_hallo = serv1.get_user_by_name(serv1.get_nick())
        chan1.add_user(user1)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user1)
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_chan2 goodbye now", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user1.name+" goodbye now" in data[0][0]
            assert "kicked "+user1.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3userchanmsg_not_in_channel(self):
        pass

    def test_kick_3userchanmsg_user_not_there(self):
        pass

    def test_kick_3userchanmsg_no_power(self):
        pass

    def test_kick_3userchanmsg(self):
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
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        chan2.add_user(user2)
        chan2.add_user(user_hallo)
        chan2_hallo = chan2.get_membership_by_user(user_hallo)
        chan2_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2 test_chan2 goodbye now", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan2.name+" "+user2.name+" goodbye now" in data[0][0]
            assert "kicked "+user2.name+" from "+chan2.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)

    def test_kick_3usermsg_not_in_channel(self):
        """Placeholder: Does not make sense, hallo must be in channel to receive message on it."""
        pass

    def test_kick_3usermsg_user_not_there(self):
        pass

    def test_kick_3usermsg_no_power(self):
        pass

    def test_kick_3usermsg(self):
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
        chan1.add_user(user2)
        chan1.add_user(user_hallo)
        chan1_hallo = chan1.get_membership_by_user(user_hallo)
        chan1_hallo.is_op = True
        try:
            self.function_dispatcher.dispatch("kick test_user2 goodbye now", user1, chan1)
            data = serv1.get_send_data(2)
            assert "error" not in data[0][0].lower()
            assert data[0][1] is None
            assert data[1][1] == chan1
            assert data[0][2] == Server.MSG_RAW
            assert data[1][2] == Server.MSG_MSG
            assert data[0][0][:4] == "KICK"
            assert chan1.name+" "+user2.name+" goodbye now" in data[0][0]
            assert "kicked "+user2.name+" from "+chan1.name in data[1][0].lower()
        finally:
            self.hallo.remove_server(serv1)
