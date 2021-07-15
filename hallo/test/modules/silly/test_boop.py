from hallo.events import EventMessage, EventCTCP


def test_boop_blank(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "boop")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Boop function should return error if no arguments given."


def test_boop_user_offline(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = False
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_user_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_user(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user")
    )
    data = test_hallo.test_server.get_send_data(2, test_hallo.test_chan)
    assert data[0].__class__ == EventCTCP
    assert data[1].__class__ == EventMessage
    assert "boop" in data[0].text.lower(), "Boop did not boop."
    assert (
        "another_user" in data[0].text.lower()
    ), "Boop did not mention the user to be booped."
    assert (
        "done" in data[1].text.lower()
    ), "Boop did not tell original user it was done."


def test_boop_user_chan_offline(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = False
    test_hallo.test_chan2.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user another_chan"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_user_chan_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user another_chan"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_user_chan_hallo_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = False
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user another_chan"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_user_chan_privmsg(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.test_chan2.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "boop another_user another_chan")
    )
    data = test_hallo.test_server.get_send_data(2)
    assert data[0].__class__ == EventCTCP
    assert data[1].__class__ == EventMessage
    assert data[0].channel == test_hallo.test_chan2, "Boop did not go to correct channel."
    assert data[1].user == test_hallo.test_user, "Confirmation did not go back to user's privmsg."
    assert "boop" in data[0].text.lower(), "Boop did not boop."
    assert (
        "another_user" in data[0].text.lower()
    ), "Boop did not mention the user to be booped."
    assert (
        "done" in data[1].text.lower()
    ), "Boop did not tell original user it was done."


def test_boop_user_chan(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.test_chan2.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_user another_chan"
        )
    )
    data = test_hallo.test_server.get_send_data(2)
    assert data[0].__class__ == EventCTCP
    assert data[1].__class__ == EventMessage
    assert data[0].channel == test_hallo.test_chan2, "Boop did not go to correct channel."
    assert (
        data[1].channel == test_hallo.test_chan
    ), "Confirmation did not go back to user's channel."
    assert "boop" in data[0].text.lower(), "Boop did not boop."
    assert (
        "another_user" in data[0].text.lower()
    ), "Boop did not mention the user to be booped."
    assert (
        "done" in data[1].text.lower()
    ), "Boop did not tell original user it was done."


def test_boop_chan_user_offline(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = False
    test_hallo.test_chan2.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_chan another_user"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_chan_user_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_chan another_user"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_chan_user_hallo_not_in_channel(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = False
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_chan another_user"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()


def test_boop_chan_user_privmsg(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.test_chan2.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "boop another_chan another_user")
    )
    data = test_hallo.test_server.get_send_data(2)
    assert data[0].__class__ == EventCTCP
    assert data[1].__class__ == EventMessage
    assert data[0].channel == test_hallo.test_chan2, "Boop did not go to correct channel."
    assert data[1].user == test_hallo.test_user, "Confirmation did not go back to user's privmsg."
    assert "boop" in data[0].text.lower(), "Boop did not boop."
    assert (
        "another_user" in data[0].text.lower()
    ), "Boop did not mention the user to be booped."
    assert (
        "done" in data[1].text.lower()
    ), "Boop did not tell original user it was done."


def test_boop_chan_user(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.test_chan.add_user(test_hallo.test_user)
    test_hallo.test_chan2 = test_hallo.test_server.get_channel_by_address(
        "another_chan".lower(), "another_chan"
    )
    test_hallo.test_chan2.in_channel = True
    test_hallo.test_user2 = test_hallo.test_server.get_user_by_address("another_user", "another_user")
    test_hallo.test_user2.online = True
    test_hallo.test_chan2.add_user(test_hallo.test_user2)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "boop another_chan another_user"
        )
    )
    data = test_hallo.test_server.get_send_data(2)
    assert data[0].__class__ == EventCTCP
    assert data[1].__class__ == EventMessage
    assert data[0].channel == test_hallo.test_chan2, "Boop did not go to correct channel."
    assert (
        data[1].channel == test_hallo.test_chan
    ), "Confirmation did not go back to user's channel."
    assert "boop" in data[0].text.lower(), "Boop did not boop."
    assert (
        "another_user" in data[0].text.lower()
    ), "Boop did not mention the user to be booped."
    assert (
        "done" in data[1].text.lower()
    ), "Boop did not tell original user it was done."
