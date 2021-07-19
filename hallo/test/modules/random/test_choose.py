from hallo.events import EventMessage


def test_no_options(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "more than 1 thing" in data[0].text.lower()
    ), "Not warning about single option."


def test_one_option(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "more than 1 thing" in data[0].text.lower()
    ), "Not warning about single option."


def test_x_or_y(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set mock value
    mock_chooser.choice = 0
    # Choose x
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or y")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"x"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 1
    # Choose y
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or y")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"y"' in data[0].text.lower()


def test_x_comma_y(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set mock value
    mock_chooser.choice = 0
    # Choose x
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x, y")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"x"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 1
    # Choose y
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x, y")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"y"' in data[0].text.lower()


def test_x_or_comma_y(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set mock value
    mock_chooser.choice = 0
    # Choose x
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or, y")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"x"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 1
    # Choose y
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or, y")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"y"' in data[0].text.lower()


def test_x_y_z(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set mock value
    mock_chooser.choice = 0
    # Choose x
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or y or z")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y", "z"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"x"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 1
    # Choose y
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or y or z")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y", "z"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"y"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 2
    # Choose z
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or y or z")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y", "z"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"z"' in data[0].text.lower()


def test_multiple_separators(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set mock value
    mock_chooser.choice = 0
    # Choose x
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x, y or z")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y", "z"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"x"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 1
    # Choose y
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x or y or, z")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y", "z"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"y"' in data[0].text.lower()
    # Set mock value
    mock_chooser.choice = 2
    # Choose z
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "choose x, y or, z")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert mock_chooser.last_choices == ["x", "y", "z"]
    assert mock_chooser.last_count == 1
    assert "i choose" in data[0].text.lower()
    assert '"z"' in data[0].text.lower()
