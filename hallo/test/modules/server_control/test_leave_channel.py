from hallo.events import EventMessage
from hallo.test.server_mock import ServerMock


def test_no_args(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "leave")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    chans = test_hallo.test_server.get_left_channels(1)
    assert chans[0] == test_hallo.test_chan
    assert "left" in data[0].text.lower()
    assert test_hallo.test_chan.name in data[0].text.lower()


def test_channel_name(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "leave " + test_hallo.test_chan.name)
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    chans = test_hallo.test_server.get_left_channels(1)
    assert chans[0] == test_hallo.test_chan
    assert "left" in data[0].text.lower()
    assert test_hallo.test_chan.name in data[0].text.lower()


def test_no_args_privmsg(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "leave")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    test_hallo.test_server.get_left_channels(0)
    assert "error" in data[0].text.lower()


def test_other_channel_name(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    other = test_hallo.test_server.get_channel_by_address("#other".lower(), "#other")
    other.in_channel = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "leave " + other.name)
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    chans = test_hallo.test_server.get_left_channels(1)
    assert chans[0] == other
    assert "left" in data[0].text.lower()
    assert other.name in data[0].text.lower()


def test_channel_name_privmsg(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "leave " + test_hallo.test_chan.name)
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    chans = test_hallo.test_server.get_left_channels(1)
    assert chans[0] == test_hallo.test_chan
    assert "left" in data[0].text.lower()
    assert test_hallo.test_chan.name in data[0].text.lower()


def test_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "leave #not_in_channel")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    test_hallo.test_server.get_left_channels(0)
    assert "error" in data[0].text.lower()


def test_server_specified_first(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Set up test resources
    test_serv = ServerMock(test_hallo)
    test_serv.name = "TestServer1"
    test_hallo.add_server(test_serv)
    test_chan1 = test_serv.get_channel_by_address("#other_serv".lower(), "#other_serv")
    test_chan1.in_channel = True
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "leave server=" + test_serv.name + " " + test_chan1.name,
        )
    )
    # Check response data
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    test_hallo.test_server.get_left_channels(0)
    chans = test_serv.get_left_channels(1)
    assert chans[0] == test_chan1
    assert "left" in data[0].text.lower()
    assert test_chan1.name in data[0].text.lower()


def test_server_specified_second(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Set up test resources
    test_serv = ServerMock(test_hallo)
    test_serv.name = "TestServer1"
    test_hallo.add_server(test_serv)
    test_chan1 = test_serv.get_channel_by_address("#other_serv".lower(), "#other_serv")
    test_chan1.in_channel = True
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "leave " + test_chan1.name + " server=" + test_serv.name,
        )
    )
    # Check response data
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    test_hallo.test_server.get_left_channels(0)
    chans = test_serv.get_left_channels(1)
    assert chans[0] == test_chan1
    assert "left" in data[0].text.lower()
    assert test_chan1.name in data[0].text.lower()


def test_server_specified_no_channel(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Set up test resources
    test_serv = ServerMock(test_hallo)
    test_serv.name = "TestServer1"
    test_hallo.add_server(test_serv)
    test_chan1 = test_serv.get_channel_by_address(
        "#not_in_channel".lower(), "#not_in_channel"
    )
    test_chan1.in_channel = False
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "leave server=" + test_serv.name + " " + test_chan1.name,
        )
    )
    # Check response data
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    test_hallo.test_server.get_left_channels(0)
    test_serv.get_left_channels(0)
    assert "error" in data[0].text.lower()


def test_server_not_on_server(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "leave server=not_a_server " + test_hallo.test_chan.name,
        )
    )
    # Check response data
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    test_hallo.test_server.get_left_channels(0)
    assert "error" in data[0].text.lower()


def test_not_auto_join(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Make test channel auto join
    test_hallo.test_chan.auto_join = True
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "leave " + test_hallo.test_chan.name)
    )
    # Check response data
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    chans = test_hallo.test_server.get_left_channels(1)
    assert chans[0] == test_hallo.test_chan
    assert "left" in data[0].text.lower()
    assert test_hallo.test_chan.name in data[0].text.lower()
    # Check that test channel is not auto join anymore
    assert not test_hallo.test_chan.auto_join


def test_post_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"server_control"})
    # Assert in channel
    assert test_hallo.test_chan.in_channel
    # Send command
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "leave " + test_hallo.test_chan.name)
    )
    # Check response data
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    chans = test_hallo.test_server.get_left_channels(1)
    assert chans[0] == test_hallo.test_chan
    assert "left" in data[0].text.lower()
    assert test_hallo.test_chan.name in data[0].text.lower()
    # Check that test channel is not in the channel anymore
    assert not test_hallo.test_chan.in_channel
