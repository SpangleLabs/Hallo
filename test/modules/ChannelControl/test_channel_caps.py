from events import EventMessage


def test_caps_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(test_server, test_chan, test_user, "channel caps"))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_chan.use_caps_lock
    # Try toggling again
    hallo.function_dispatcher.dispatch(EventMessage(test_server, test_chan, test_user, "channel caps"))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_chan.use_caps_lock


def test_caps_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(test_server, test_chan, test_user, "channel caps on"))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "caps lock set on" in data[0].text.lower()
    assert test_chan.use_caps_lock


def test_caps_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.use_caps_lock = True
    hallo.function_dispatcher.dispatch(EventMessage(test_server, test_chan, test_user, "channel caps off"))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "caps lock set off" in data[0].text.lower()
    assert not test_chan.use_caps_lock


def test_caps_channel_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_chan1.use_caps_lock
    # Try toggling again
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_chan1.use_caps_lock


def test_caps_channel_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel on"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "caps lock set on" in data[0].text.lower()
    assert test_chan1.use_caps_lock


def test_caps_channel_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.use_caps_lock = True
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel off"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "caps lock set off" in data[0].text.lower()
    assert not test_chan1.use_caps_lock


def test_caps_on_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps on other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "caps lock set on" in data[0].text.lower()
    assert test_chan1.use_caps_lock


def test_caps_off_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = True
    test_chan1.use_caps_lock = True
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps off other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "caps lock set off" in data[0].text.lower()
    assert not test_chan1.use_caps_lock


def test_caps_not_in_channel_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = False
    test_chan1.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.use_caps_lock


def test_caps_not_in_channel_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = False
    test_chan1.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel on"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.use_caps_lock


def test_caps_no_bool(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address("other_channel".lower(), "other_channel")
    test_chan1.in_channel = False
    test_chan1.use_caps_lock = False
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, test_chan, test_user, "channel caps other_channel word"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.use_caps_lock
