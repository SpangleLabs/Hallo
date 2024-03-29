from hallo.events import EventMessage
from hallo.server import Server
from hallo.test.server_mock import ServerMock


def test_no_servers(hallo_getter):
    test_hallo = hallo_getter({"server_control"}, disconnect_servers=True)
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "list servers")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    # Check response
    assert "do not" in data[0].text
    assert ":" not in data[0].text


def test_one_server(hallo_getter):
    test_hallo = hallo_getter({"server_control"}, disconnect_servers=True)
    # Add one server
    serv1 = ServerMock(test_hallo)

    serv1.name = "server_list_test"
    test_hallo.add_server(serv1)
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "list servers")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    # Check response
    server_list_text = data[0].text.split(":")[1]
    server_list = server_list_text.split("], ")
    assert len(server_list) == 1
    assert serv1.name in server_list[0]
    assert "type=" + serv1.type in server_list[0]
    assert "state=" + serv1.state in server_list[0]
    assert "nick=" + serv1.get_nick() in server_list[0]
    assert "auto_connect=" + str(serv1.auto_connect) in server_list[0]


def test_two_mock_servers(hallo_getter):
    test_hallo = hallo_getter({"server_control"}, disconnect_servers=True)
    # Add two servers
    serv1 = ServerMock(test_hallo)
    serv1.name = "server_list_test1"
    serv1.auto_connect = True
    serv1.nick = "hallo"
    serv1.disconnect()
    test_hallo.add_server(serv1)
    serv2 = ServerMock(test_hallo)
    serv2.name = "server_list_test2"
    serv2.auto_connect = False
    serv2.nick = "yobot"
    serv2.start()
    test_hallo.add_server(serv2)
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "list servers")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
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


def test_irc_server(hallo_getter):
    test_hallo = hallo_getter({"server_control"}, disconnect_servers=True)
    # Add one server
    serv1 = ServerMock(test_hallo)
    serv1.type = Server.TYPE_IRC
    serv1.server_address = "irc.example.org"
    serv1.server_port = 6789
    serv1.name = "irc_server_list_test"
    test_hallo.add_server(serv1)
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "list servers")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
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
