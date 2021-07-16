from hallo.events import EventMessage


def test_pass_off(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.password = "test_pass"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel password")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password disabled" in data[0].text.lower()
    assert test_hallo.test_chan.password is None


def test_pass_null(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.password = "test_pass"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel password none")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password disabled" in data[0].text.lower()
    assert test_hallo.test_chan.password is None


def test_pass_set(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.password = None
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel password test_pass")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password set" in data[0].text.lower()
    assert test_hallo.test_chan.password == "test_pass"


def test_pass_chan_null(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.password = "test_pass"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel password other_channel none"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password disabled" in data[0].text.lower()
    assert "other_channel" in data[0].text.lower()
    assert test_hallo.test_chan1.password is None


def test_pass_chan_set(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.password = None
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel password other_channel test_pass",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "password set" in data[0].text.lower()
    assert "other_channel" in data[0].text.lower()
    assert test_hallo.test_chan1.password == "test_pass"
