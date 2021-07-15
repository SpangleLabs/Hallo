from hallo.events import EventMessage


def test_logs_toggle(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_hallo.test_chan.logging
    # Try toggling again
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_hallo.test_chan.logging


def test_logs_on(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging on")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set on" in data[0].text.lower()
    assert test_hallo.test_chan.logging


def test_logs_off(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.logging = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging off")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set off" in data[0].text.lower()
    assert not test_hallo.test_chan.logging


def test_logs_channel_toggle(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_hallo.test_chan1.logging
    # Try toggling again
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_hallo.test_chan1.logging


def test_logs_channel_on(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel on"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set on" in data[0].text.lower()
    assert test_hallo.test_chan1.logging


def test_logs_channel_off(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.logging = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel off"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set off" in data[0].text.lower()
    assert not test_hallo.test_chan1.logging


def test_logs_on_channel(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging on other_channel"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set on" in data[0].text.lower()
    assert test_hallo.test_chan1.logging


def test_logs_off_channel(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.logging = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging off other_channel"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set off" in data[0].text.lower()
    assert not test_hallo.test_chan1.logging


def test_logs_not_in_channel_toggle(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = False
    test_hallo.test_chan1.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_hallo.test_chan1.logging


def test_logs_not_in_channel_on(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = False
    test_hallo.test_chan1.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel on"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_hallo.test_chan1.logging


def test_logs_no_bool(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = False
    test_hallo.test_chan1.logging = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel logging other_channel word"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_hallo.test_chan1.logging
