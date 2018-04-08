import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class ConnectTest(TestBase, unittest.TestCase):

    def tearDown(self):
        for server in self.hallo.server_list:
            if server is not self.server:
                server.disconnect(True)
        self.hallo.server_list.clear()
        self.hallo.add_server(self.server)
        super().tearDown()

    def test_no_servers(self):
        pass

    def test_one_server(self):
        pass

    def test_two_mock_servers(self):
        pass

    def test_irc_server(self):
        pass
