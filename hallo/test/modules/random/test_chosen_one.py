from hallo.events import EventMessage


def test_not_a_channel(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "can only be used in a channel" in data[0].text.lower()
    ), "Not warning about using in private message."


def test_one_person_in_channel(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.test_chan.remove_user(test_hallo.hallo_user)
    try:
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "chosen one")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert mock_chooser.last_choices == [
            test_hallo.test_user.name
        ], "User list should just be test user"
        assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
                "{} is the chosen one".format(test_hallo.test_user.name)
                in data[0].text.lower()
        ), "Should have chosen user"
    finally:
        test_hallo.test_chan.add_user(test_hallo.hallo_user)


def test_two_people_in_channel(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set chooser option
    mock_chooser.choice = 0
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == {
        test_hallo.test_user.name,
        test_hallo.hallo_user.name,
    }, "User list should just be test user and hallo"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[0]) in data[0].text
    )
    # Set chooser option
    mock_chooser.choice = 1
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == {
        test_hallo.test_user.name,
        test_hallo.hallo_user.name,
    }, "User list should just be test user and hallo"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[1]) in data[0].text
    )


def test_five_in_channel(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    chan = test_hallo.test_server.get_channel_by_address("test_chan", "test_chan")
    user1 = test_hallo.test_server.get_user_by_address("user1", "user1")
    user2 = test_hallo.test_server.get_user_by_address("user2", "user2")
    user3 = test_hallo.test_server.get_user_by_address("user3", "user3")
    user4 = test_hallo.test_server.get_user_by_address("user4", "user4")
    user5 = test_hallo.test_server.get_user_by_address("user5", "user5")
    users = [user1, user2, user3, user4, user5]
    for x in users:
        chan.add_user(x)
    # Set chooser option
    mock_chooser.choice = 0
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == set(
        [x.name for x in users]
    ), "User list wrong"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[0]) in data[0].text
    )
    # Set chooser option
    mock_chooser.choice = 1
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == set(
        [x.name for x in users]
    ), "User list wrong"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[1]) in data[0].text
    )
    # Set chooser option
    mock_chooser.choice = 2
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == set(
        [x.name for x in users]
    ), "User list wrong"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[2]) in data[0].text
    )
    # Set chooser option
    mock_chooser.choice = 3
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == set(
        [x.name for x in users]
    ), "User list wrong"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[3]) in data[0].text
    )
    # Set chooser option
    mock_chooser.choice = 4
    # Choose user
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, chan, test_hallo.test_user, "chosen one")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert set(mock_chooser.last_choices) == set(
        [x.name for x in users]
    ), "User list wrong"
    assert mock_chooser.last_count == 1, "Should have only asked to choose 1"
    assert (
            "{} is the chosen one".format(mock_chooser.last_choices[4]) in data[0].text
    )
