import unittest

from Server import Server
from Server import ServerIRC
from test.TestBase import TestBase


class ConnectTest(TestBase, unittest.TestCase):

    def tearDown(self):
        self.hallo.server_list.clear()
        self.hallo.add_server(self.server)
        super().tearDown()

    def return_irc(self):
        return Server.TYPE_IRC

    def test_connect_specify_irc(self):
        # Run command
        self.function_dispatcher.dispatch("connect irc www.example.com", self.test_user, self.test_chan)
        # Ensure correct response is given
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Kill the server
        for server in self.hallo.server_list:
            server.open = False

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
            server.open = False
            if server != self.server:
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
            server.open = False
            if server != self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.get_server_port() == test_port, "Port incorrect"

    def test_address_in_argument(self):
        test_url = "www.example.com"
        # Run command
        self.function_dispatcher.dispatch("connect irc "+test_url, self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance"
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            server.open = False
            if server != self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_address == test_url, "Address incorrect"

    def test_address_by_argument(self):
        test_url = "www.example.com"
        # Run command
        self.function_dispatcher.dispatch("connect irc server_address="+test_url, self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance"
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            server.open = False
            if server != self.server:
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
            server.open = False
            if server != self.server:
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
        self.function_dispatcher.dispatch("connect irc "+test_server+" server_name="+test_name,
                                          self.test_user, self.test_chan)
        # Ensure correct response
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "connected to new irc server" in data[0][0].lower(), "Incorrect output: "+str(data[0][0])
        # Find the right server
        assert len(self.hallo.server_list) == 2, "Incorrect number of servers in hallo instance."
        right_server = None  # type: ServerIRC
        for server in self.hallo.server_list:
            server.open = False
            if server != self.server:
                right_server = server
        assert right_server is not None, "New server wasn't found."
        assert right_server.server_address == test_server, "Address incorrect"
        assert right_server.get_name() == test_name, "Name incorrect"


# Todo, tests to write:
# get server name from domain
# auto connect true
# auto connect false
# auto connect default true
# server nick specified
# server nick inherit
# server prefix specified
# server prefix inherit
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
