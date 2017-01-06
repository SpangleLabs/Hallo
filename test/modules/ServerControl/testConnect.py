import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class ConnectTest(TestBase, unittest.TestCase):

    def tearDown(self):
        self.hallo.server_list.clear()
        self.hallo.add_server(self.server)

    def test_connect_to_known_server(self):
        # Set up an example server
        server_name = "known_server_name"
        test_server = ServerMock(self.hallo)
        test_server.auto_connect = False
        self.hallo.add_server(test_server)
        # Call connect function
        self.function_dispatcher.dispatch("connect "+server_name, self.test_user, self.test_chan)
        # Ensure response is correct
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "connected" in data[0][0].lower()
        assert server_name in data[0][0].lower()
        # Ensure auto connect was set
        assert test_server.auto_connect, "Auto connect should have been set to true."
        # Ensure server was ran
        assert test_server.open, "Test server was not started."

    def test_connect_to_known_server_fail_connected(self):
        # Set up example server
        server_name = "known_server_name"
        test_server = ServerMock(self.hallo)
        test_server.auto_connect = False
        test_server.open = True
        self.hallo.add_server(test_server)
        # Call connect function
        self.function_dispatcher.dispatch("connect "+server_name, self.test_user, self.test_chan)
        # Ensure error response is given
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert "already connected" in data[0][0].lower()
        # Ensure auto connect was still set
        assert test_server.auto_connect, "Auto connect should have still been set to true."
        # Ensure server is still running
        assert test_server.open, "Test server should not have been shut down."


# Todo, tests to write:
# test Connect fail unrecognised protocol
# test Connect default to current type
# test Connect specify irc
# port in url
# port by argument
# address by argument
# address in argument
# inherit port
# non-int port
# null address
# specified server name
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
