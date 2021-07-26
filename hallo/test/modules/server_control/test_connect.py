from hallo.events import EventMessage
from hallo.server import Server
from hallo.test.server_mock import ServerMock


def test_connect_to_known_server(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Set up an example server
    server_name = "known_server_name"
    test_server = ServerMock(test_hallo)
    test_server.name = server_name
    test_server.auto_connect = False
    test_hallo.add_server(test_server)
    # Call connect function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "connect " + server_name
        )
    )
    # Ensure response is correct
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower(), data[0].text.lower()
    assert "connected" in data[0].text.lower(), data[0].text.lower()
    assert server_name in data[0].text.lower(), data[0].text.lower()
    # Ensure auto connect was set
    assert test_server.auto_connect, "Auto connect should have been set to true."
    # Ensure server was ran
    assert test_server.is_connected(), "Test server was not started."


def test_connect_to_known_server_fail_connected(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Set up example server
    server_name = "known_server_name"
    test_server = ServerMock(test_hallo)
    test_server.name = server_name
    test_server.auto_connect = False
    test_server.state = Server.STATE_OPEN
    test_hallo.add_server(test_server)
    # Call connect function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "connect " + server_name
        )
    )
    # Ensure error response is given
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower(), data[0].text.lower()
    assert "already connected" in data[0].text.lower(), data[0].text.lower()
    # Ensure auto connect was still set
    assert (
        test_server.auto_connect
    ), "Auto connect should have still been set to true."
    # Ensure server is still running
    assert (
            test_server.state == Server.STATE_OPEN
    ), "Test server should not have been shut down."


def test_connect_fail_unrecognised_protocol(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "connect www.example.com"
        )
    )
    # Ensure error response is given
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert "unrecognised server protocol" in data[0].text.lower()


def test_connect_default_current_protocol(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Set up some mock methods
    test_hallo.test_server.type = Server.TYPE_IRC
    # Run command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "connect www.example.com:80",
        )
    )
    # Ensure correct response is given
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert (
            "connected to new irc server" in data[0].text.lower()
    ), "Incorrect output: " + str(data[0].text)
