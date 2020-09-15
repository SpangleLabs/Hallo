import unittest

from hallo.events import EventMessage
from hallo.server import Server
from hallo.test.server_mock import ServerMock
from hallo.test.test_base import TestBase


class ListServersTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        for server in self.hallo.server_list:
            server.disconnect(True)
        self.hallo.server_list.clear()

    def test_no_servers(self):
        # Send command
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "list servers")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        # Check response
        assert "do not" in data[0].text
        assert ":" not in data[0].text

    def test_one_server(self):
        # Add one server
        serv1 = ServerMock(self.hallo)

        serv1.name = "server_list_test"
        self.hallo.add_server(serv1)
        # Send command
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "list servers")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        # Check response
        server_list_text = data[0].text.split(":")[1]
        server_list = server_list_text.split("], ")
        assert len(server_list) == 1
        assert serv1.name in server_list[0]
        assert "type=" + serv1.type in server_list[0]
        assert "state=" + serv1.state in server_list[0]
        assert "nick=" + serv1.get_nick() in server_list[0]
        assert "auto_connect=" + str(serv1.auto_connect) in server_list[0]

    def test_two_mock_servers(self):
        # Add two servers
        serv1 = ServerMock(self.hallo)
        serv1.name = "server_list_test1"
        serv1.auto_connect = True
        serv1.nick = "hallo"
        serv1.disconnect()
        self.hallo.add_server(serv1)
        serv2 = ServerMock(self.hallo)
        serv2.name = "server_list_test2"
        serv2.auto_connect = False
        serv2.nick = "yobot"
        serv2.start()
        self.hallo.add_server(serv2)
        # Send command
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "list servers")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        # Check response
        server_list_text = data[0].text.split(": \n")[1]
        server_list = server_list_text.split("\n")
        assert len(server_list) == 2
        if serv1.name in server_list[0]:
            server_text1 = server_list[0]
            server_text2 = server_list[1]
        else:
            server_text1 = server_list[1]
            server_text2 = server_list[0]
        assert serv1.name in server_text1
        assert "type=" + serv1.type in server_text1
        assert "state=" + serv1.state in server_text1
        assert "nick=" + serv1.get_nick() in server_text1
        assert "auto_connect=" + str(serv1.auto_connect) in server_text1
        assert serv2.name in server_text2
        assert "type=" + serv2.type in server_text2
        assert "state=" + serv2.state in server_text2
        assert "nick=" + serv2.get_nick() in server_text2
        assert "auto_connect=" + str(serv2.auto_connect) in server_text2

    def test_irc_server(self):
        # Add one server
        serv1 = ServerMock(self.hallo)
        serv1.type = Server.TYPE_IRC
        serv1.server_address = "irc.example.org"
        serv1.server_port = 6789
        serv1.name = "irc_server_list_test"
        self.hallo.add_server(serv1)
        # Send command
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "list servers")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        # Check response
        server_list_text = data[0].text.split(":", 1)[1]
        server_list = server_list_text.split("], ")
        assert len(server_list) == 1
        assert serv1.name in server_list[0], (
            "Server name not found in output.\n"
            "Server name: " + serv1.name + "\nCommand output: " + server_list[0]
        )
        assert "type=" + serv1.type in server_list[0], (
            "Server type not found in output.\n"
            "Server type: " + serv1.type + "\nCommand output: " + server_list[0]
        )
        irc_address = serv1.server_address + ":" + str(serv1.server_port)
        assert irc_address in server_list[0], (
            "IRC server address not found in output.\n"
            "Server address: " + irc_address + "\nCommand output: " + server_list[0]
        )
        assert "state=" + serv1.state in server_list[0], (
            "Server state not found in output.\n"
            "Server name: " + serv1.state + "\nCommand output: " + server_list[0]
        )
        assert "nick=" + serv1.get_nick() in server_list[0], (
            "Server nick not found in output.\n"
            "Server nick: " + serv1.get_nick() + "\nCommand output: " + server_list[0]
        )
        assert "auto_connect=" + str(serv1.auto_connect) in server_list[0]
