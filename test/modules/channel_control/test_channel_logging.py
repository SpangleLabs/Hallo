from events import EventMessage


def test_logs_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(test_server, test_chan, test_user, "channel logging"))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_chan.logging
    # Try toggling again
    hallo.function_dispatcher.dispatch(EventMessage(test_server, test_chan, test_user, "channel logging"))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_chan.logging


def test_logs_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging on"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set on" in data[0].text.lower()
    assert test_chan.logging


def test_logs_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.logging = True
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging off"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set off" in data[0].text.lower()
    assert not test_chan.logging


def test_logs_channel_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_chan1.logging
    # Try toggling again
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_chan1.logging


def test_logs_channel_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel on"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set on" in data[0].text.lower()
    assert test_chan1.logging


def test_logs_channel_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.logging = True
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel off"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set off" in data[0].text.lower()
    assert not test_chan1.logging


def test_logs_on_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging on other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set on" in data[0].text.lower()
    assert test_chan1.logging


def test_logs_off_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.logging = True
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging off other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "logging set off" in data[0].text.lower()
    assert not test_chan1.logging


def test_logs_not_in_channel_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = False
    test_chan1.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.logging


def test_logs_not_in_channel_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = False
    test_chan1.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel on"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.logging


def test_logs_no_bool(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = False
    test_chan1.logging = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel logging other_channel word"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.logging
