import unittest

from Server import Server
from Server import ServerIRC
from test.TestBase import TestBase


class ConnectIRCTest(TestBase, unittest.TestCase):

    def tearDown(self):
        for server in self.hallo.server_list:
            if server is not self.server:
                server.open = False
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
        test_chan_irc = test_serv_irc.get_channel_by_name("test_chan")
        test_user_irc = test_serv_irc.get_user_by_name("test_user")
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


# Todo, tests to write:
# full name specified
# full name inherit
# nickserv nick default
# nickserv nick inherit
# nickserv nick specified
# nickserv identity command default
# nickserv identity command inherit
# nickserv identity command specified
# nickserv identity resp default
# nickserv identity resp inherit
# nickserv identity resp specified
# nickserv password default
# nickserv password inherit
# nickserv password specified
# set groups of current user on other server
# check server added
# check thread started
# check server started
