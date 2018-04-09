import unittest

from Server import Server
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class ConnectTest(TestBase, unittest.TestCase):

    def setUp(self):
        # Clear servers

    def tearDown(self):
        for server in self.hallo.server_list:
            if server is not self.server:
                server.disconnect(True)
        self.hallo.server_list.clear()
        self.hallo.add_server(self.server)
        super().tearDown()

    def test_no_servers(self):
        self.function_dispatcher.dispatch("list servers ", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "do not currently have any servers" in data[0][0].lower()

    def test_one_server(self):
        # Add a mock server
        pass

    def test_two_mock_servers(self):
        pass

    def test_irc_server(self):
        pass
