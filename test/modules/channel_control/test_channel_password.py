from events import EventMessage


def test_pass_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.password = "test_pass"
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel password")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password disabled" in data[0].text.lower()
    assert test_chan.password is None


def test_pass_null(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.password = "test_pass"
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel password none")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password disabled" in data[0].text.lower()
    assert test_chan.password is None


def test_pass_set(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.password = None
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel password test_pass")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password set" in data[0].text.lower()
    assert test_chan.password == "test_pass"


def test_pass_chan_null(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.password = "test_pass"
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, test_chan, test_user, "channel password other_channel none"
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password disabled" in data[0].text.lower()
    assert "other_channel" in data[0].text.lower()
    assert test_chan1.password is None


def test_pass_chan_set(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.password = None
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel password other_channel test_pass",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password set" in data[0].text.lower()
    assert "other_channel" in data[0].text.lower()
    assert test_chan1.password == "test_pass"
