from hallo.events import EventMessage


def test_passive_toggle(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_hallo.test_chan.passive_enabled
    # Try toggling again
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_hallo.test_chan.passive_enabled


def test_passive_on(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions on")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set enabled" in data[0].text.lower()
    assert test_hallo.test_chan.passive_enabled


def test_passive_off(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan.passive_enabled = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions off")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set disabled" in data[0].text.lower()
    assert not test_hallo.test_chan.passive_enabled


def test_passive_channel_toggle(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions other_channel"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert test_hallo.test_chan1.passive_enabled
    # Try toggling again
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions other_channel"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "toggle" in data[0].text.lower()
    assert not test_hallo.test_chan1.passive_enabled


def test_passive_channel_on(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel passive functions other_channel on",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set enabled" in data[0].text.lower()
    assert test_hallo.test_chan1.passive_enabled


def test_passive_channel_off(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.passive_enabled = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel passive functions other_channel off",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set disabled" in data[0].text.lower()
    assert not test_hallo.test_chan1.passive_enabled


def test_passive_on_channel(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel passive functions on other_channel",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set enabled" in data[0].text.lower()
    assert test_hallo.test_chan1.passive_enabled


def test_passive_off_channel(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = True
    test_hallo.test_chan1.passive_enabled = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel passive functions off other_channel",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "passive functions set disabled" in data[0].text.lower()
    assert not test_hallo.test_chan1.passive_enabled


def test_passive_not_in_channel_toggle(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = False
    test_hallo.test_chan1.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "channel passive functions other_channel"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_hallo.test_chan1.passive_enabled


def test_passive_not_in_channel_on(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = False
    test_hallo.test_chan1.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel passive functions other_channel on",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_hallo.test_chan1.passive_enabled


def test_passive_no_bool(hallo_getter):
    test_hallo = hallo_getter({"channel_control"})
    test_hallo.test_chan1 = test_hallo.test_server.get_channel_by_address(
        "other_channel".lower(), "other_channel"
    )
    test_hallo.test_chan1.in_channel = False
    test_hallo.test_chan1.passive_enabled = False
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "channel passive functions other_channel word",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert not test_hallo.test_chan1.passive_enabled
