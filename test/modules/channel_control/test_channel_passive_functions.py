from events import EventMessage


def test_passive_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel passive functions")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_chan.passive_enabled
    # Try toggling again
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel passive functions")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_chan.passive_enabled


def test_passive_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel passive functions on")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set enabled" in data[0].text.lower()
    assert test_chan.passive_enabled


def test_passive_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan.passive_enabled = True
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, test_chan, test_user, "channel passive functions off")
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set disabled" in data[0].text.lower()
    assert not test_chan.passive_enabled


def test_passive_channel_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, test_chan, test_user, "channel passive functions other_channel"
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_chan1.passive_enabled
    # Try toggling again
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, test_chan, test_user, "channel passive functions other_channel"
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_chan1.passive_enabled


def test_passive_channel_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel passive functions other_channel on",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set enabled" in data[0].text.lower()
    assert test_chan1.passive_enabled


def test_passive_channel_off(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.passive_enabled = True
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel passive functions other_channel off",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set disabled" in data[0].text.lower()
    assert not test_chan1.passive_enabled


def test_passive_on_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel passive functions on other_channel",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set enabled" in data[0].text.lower()
    assert test_chan1.passive_enabled


def test_passive_off_channel(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = True
    test_chan1.passive_enabled = True
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel passive functions off other_channel",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set disabled" in data[0].text.lower()
    assert not test_chan1.passive_enabled


def test_passive_not_in_channel_toggle(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = False
    test_chan1.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, test_chan, test_user, "channel passive functions other_channel"
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.passive_enabled


def test_passive_not_in_channel_on(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = False
    test_chan1.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel passive functions other_channel on",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.passive_enabled


def test_passive_no_bool(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"channel_control"})
    test_chan1 = test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_chan1.in_channel = False
    test_chan1.passive_enabled = False
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server,
            test_chan,
            test_user,
            "channel passive functions other_channel word",
        )
    )
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_chan1.passive_enabled
