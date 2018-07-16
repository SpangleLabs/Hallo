import threading
import unittest

from Server import Server
from ServerIRC import ServerIRC
from UserGroup import UserGroup
from test.TestBase import TestBase


class ConnectIRCTest(TestBase, unittest.TestCase):

    def tearDown(self):
        for server in self.hallo.server_list:
            if server is not self.server:
                server.disconnect(True)
        self.hallo.server_list.clear()
        self.hallo.add_server(self.server)
        super().tearDown()

    def test_connect_specify_irc(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response is given
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])

    def test_port_in_url(self):
        test_port = 80
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:"+str(test_port), self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.get_server_port() == test_port, "Port incorrect"

    def test_port_by_argument(self):
        test_port = 80
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com server_port="+str(test_port),
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.get_server_port() == test_port, "Port incorrect"

    def test_address_in_argument(self):
        test_url = "www.example.com"
        # Run command
        self.function_dispatcher.dispatch("connect irc "+test_url+" server_port=80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance"
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_address == test_url, "Address incorrect"

    def test_address_by_argument(self):
        test_url = "www.example.com"
        # Run command
        self.function_dispatcher.dispatch("connect irc server_address="+test_url+" server_port=80",
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance"
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_address == test_url, "Address incorrect"

    def test_inherit_port(self):
        # Set things up
        test_port = 80
        test_serv_irc = ServerIRC(self.hallo)
        test_serv_irc.name = "test_serv_irc"
        test_serv_irc.server_port = test_port
        test_chan_irc = test_serv_irc.get_channel_by_address("test_chan".lower(), "test_chan")
        test_user_irc = test_serv_irc.get_user_by_address("test_user".lower(), "test_user")
        # Run command
        self.function_dispatcher.dispatch("connect irc example.com", test_user_irc, test_chan_irc)
        # Can't check response because I'm using a ServerIRC instead of a ServerMock
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance"
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_port == test_port, "Port incorrect"

    def test_non_int_port_failure(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc example.com server_port=abc", self.test_user, self.test_chan)
        # Check response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Connect didn't respond with an error."
        assert "invalid port" in data[0][0].lower(), "Connect returned the wrong error ("+str(data[0][0])+")"

    def test_null_address(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc", self.test_user, self.test_chan)
        # Check response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Connect didn't respond with an error."
        assert "no server address" in data[0][0].lower(), "Connect returned the wrong error ("+str(data[0][0])+")"

    def test_specified_server_name(self):
        # Test vars
        test_name = "test_server"
        test_server = "www.example.com"
        # Run command
        self.function_dispatcher.dispatch("connect irc "+test_server+" server_port=80 server_name="+test_name,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_address == test_server, "Address incorrect"
        assert right_server.get_name() == test_name, "Name incorrect"

    def test_get_server_name_from_domain(self):
        # Test vars
        test_name = "example"
        test_server = "www."+test_name+".com"
        # Run command
        self.function_dispatcher.dispatch("connect irc "+test_server+" server_port=80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_address == test_server, "Address incorrect"
        assert right_server.get_name() == test_name, "Name incorrect"

    def test_auto_connect_default(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.auto_connect, "Auto connect didn't default to true"

    def test_auto_connect_true(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 auto_connect=true", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.auto_connect, "Auto connect didn't set to true"

    def test_auto_connect_false(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 auto_connect=false", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert not right_server.auto_connect, "Auto connect didn't set to false"

    def test_server_nick_inherit(self):
        # Set up
        test_nick = "test_hallo"
        self.server.nick = test_nick
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nick == test_nick, "Nick did not inherit from other server"

    def test_server_nick_specified(self):
        # Set up
        test_nick = "test_hallo2"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 nick="+test_nick,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nick == test_nick, "Specified nick was not used"

    def test_server_prefix_specified_string(self):
        # Set up
        test_prefix = "robot"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 prefix="+test_prefix,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.prefix == test_prefix, "Specified prefix was not used"

    def test_server_prefix_specified_none(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 prefix=none",
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.prefix is None, "Prefix wasn't set to None as specified"

    def test_server_prefix_inherit_string(self):
        # Set up
        test_prefix = "robot"
        self.server.prefix = test_prefix
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.prefix == test_prefix, "Inherited prefix was not used"

    def test_server_prefix_inherit_none(self):
        # Set up
        self.server.prefix = None
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.prefix is None, "Prefix wasn't inherited as None"

    def test_full_name_specified_string(self):
        # Set up
        test_name = "Hallo_Robot"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 full_name="+test_name,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.full_name == test_name, "Specified full name was not used"

    def test_full_name_inherit_string(self):
        # Set up
        test_name = "Hallo_Robot"
        self.server.full_name = test_name
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.full_name == test_name, "Inherited full name was not used"

    def test_nickserv_nick_default(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_nick == "nickserv", "Default nickserv nick incorrect"

    def test_nickserv_nick_inherit(self):
        # Set up
        test_nickserv_name = "nameserv"
        test_serv_irc = ServerIRC(self.hallo)
        test_serv_irc.name = "test_serv_irc"
        test_serv_irc.nickserv_nick = test_nickserv_name
        test_chan_irc = test_serv_irc.get_channel_by_address("test_chan".lower(), "test_chan")
        test_user_irc = test_serv_irc.get_user_by_address("test_user".lower(), "test_user")
        # Run command
        self.function_dispatcher.dispatch("connect irc example.com:80", test_user_irc, test_chan_irc)
        # Can't check response because I'm using a ServerIRC instead of a ServerMock
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_nick == test_nickserv_name, "Nickserv nick wasn't inherited"

    def test_nickserv_nick_specify(self):
        # Set up
        test_nickserv_name = "nameserv"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 nickserv_nick="+test_nickserv_name,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_nick == test_nickserv_name, "Specified nickserv nick wasn't set"

    def test_nickserv_identity_command_default(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_ident_command == "status", "Default nickserv identity command incorrect"

    def test_nickserv_identity_command_inherit(self):
        # Set up
        test_nickserv_command = "identity"
        test_serv_irc = ServerIRC(self.hallo)
        test_serv_irc.name = "test_serv_irc"
        test_serv_irc.nickserv_ident_command = test_nickserv_command
        test_chan_irc = test_serv_irc.get_channel_by_address("test_chan".lower(), "test_chan")
        test_user_irc = test_serv_irc.get_user_by_address("test_user".lower(), "test_user")
        # Run command
        self.function_dispatcher.dispatch("connect irc example.com:80", test_user_irc, test_chan_irc)
        # Can't check response because I'm using a ServerIRC instead of a ServerMock
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_ident_command == test_nickserv_command, \
            "Nickserv identity command wasn't inherited"

    def test_nickserv_identity_command_specify(self):
        # Set up
        test_nickserv_command = "identity"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 nickserv_identity_command=" +
                                          test_nickserv_command,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_ident_command == test_nickserv_command, \
            "Specified nickserv identity command wasn't set"

    def test_nickserv_identity_resp_default(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_ident_response == "^status [^ ]+ 3$", \
            "Default nickserv identity response incorrect"

    def test_nickserv_identity_response_inherit(self):
        # Set up
        test_nickserv_response = "identity"
        test_serv_irc = ServerIRC(self.hallo)
        test_serv_irc.name = "test_serv_irc"
        test_serv_irc.nickserv_ident_response = test_nickserv_response
        test_chan_irc = test_serv_irc.get_channel_by_address("test_chan".lower(), "test_chan")
        test_user_irc = test_serv_irc.get_user_by_address("test_user".lower(), "test_user")
        # Run command
        self.function_dispatcher.dispatch("connect irc example.com:80", test_user_irc, test_chan_irc)
        # Can't check response because I'm using a ServerIRC instead of a ServerMock
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_ident_response == test_nickserv_response, \
            "Nickserv identity response wasn't inherited"

    def test_nickserv_identity_response_specify(self):
        # Set up
        test_nickserv_response = "identity"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 nickserv_identity_resp=" +
                                          test_nickserv_response,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_ident_response == test_nickserv_response, \
            "Specified nickserv identity response wasn't set"

    def test_nickserv_password_default(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_pass is None, "Default nickserv password incorrect"

    def test_nickserv_password_inherit(self):
        # Set up
        test_nickserv_pass = "hunter2"
        test_serv_irc = ServerIRC(self.hallo)
        test_serv_irc.name = "test_serv_irc"
        test_serv_irc.nickserv_pass = test_nickserv_pass
        test_chan_irc = test_serv_irc.get_channel_by_address("test_chan".lower(), "test_chan")
        test_user_irc = test_serv_irc.get_user_by_address("test_user".lower(), "test_user")
        # Run command
        self.function_dispatcher.dispatch("connect irc example.com:80", test_user_irc, test_chan_irc)
        # Can't check response because I'm using a ServerIRC instead of a ServerMock
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_pass == test_nickserv_pass, "Nickserv password wasn't inherited"

    def test_nickserv_password_specify(self):
        # Set up
        test_nickserv_pass = "hunter2"
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 nickserv_password=" + test_nickserv_pass,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.nickserv_pass == test_nickserv_pass, "Specified nickserv password wasn't set"

    def test_inherit_user_groups_default(self):
        # Set up
        test_user_group = UserGroup("test_group", self.hallo)
        self.test_user.add_user_group(test_user_group)
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        # Check user groups
        new_user = right_server.get_user_by_address(self.test_user.get_name().lower(), self.test_user.get_name())
        assert test_user_group in new_user.user_group_list

    def test_inherit_user_groups_specify_nick(self):
        # Set up
        test_user = "AzureDiamond"
        test_user_group = UserGroup("test_group", self.hallo)
        self.test_user.add_user_group(test_user_group)
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80 god="+test_user,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        # Check user groups
        new_user = right_server.get_user_by_address(test_user.lower(), test_user)
        assert test_user_group in new_user.user_group_list

    def test_server_added(self):
        # Pre flight check
        assert len(self.hallo.server_list) == 1, "Too many servers when starting test."
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."

    def test_thread_started(self):
        # Pre flight calc
        thread_count = threading.active_count()
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        # Ensure thread count is up
        assert threading.active_count() == thread_count+1, "Incorrect number of running threads."

    def test_server_started(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com:80", self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            if server is not self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        # Ensure new server is started
        assert right_server.state != Server.STATE_CLOSED, "New server was not started."
