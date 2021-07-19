from hallo.events import EventMessage


def test_invalid_dice(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll fd6")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "please give input in the form" in data[0].text.lower()
    ), "Should ask for correct format."
    assert "x-y" in data[0].text.lower(), "Should offer range format."
    assert "xdy" in data[0].text.lower(), "Should offer dice format."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 6df")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "please give input in the form" in data[0].text.lower()
    ), "Should ask for correct format."
    assert "x-y" in data[0].text.lower(), "Should offer range format."
    assert "xdy" in data[0].text.lower(), "Should offer dice format."


def test_invalid_range(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 1-f")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "please give input in the form" in data[0].text.lower()
    ), "Should ask for correct format."
    assert "x-y" in data[0].text.lower(), "Should offer range format."
    assert "xdy" in data[0].text.lower(), "Should offer dice format."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll b-16")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "please give input in the form" in data[0].text.lower()
    ), "Should ask for correct format."
    assert "x-y" in data[0].text.lower(), "Should offer range format."
    assert "xdy" in data[0].text.lower(), "Should offer dice format."


def test_zero_dice(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 0d6")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "invalid number of dice" in data[0].text.lower()
    ), "Should say dice number is wrong."


def test_too_many_dice(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 100000d6")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "invalid number of dice" in data[0].text.lower()
    ), "Should say dice number is wrong."


def test_zero_sides(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 4d0")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "invalid number of sides" in data[0].text.lower()
    ), "Should say side number is wrong."


def test_too_many_sides(hallo_getter):
    test_hallo = hallo_getter({"random"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 4d99999999")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "invalid number of sides" in data[0].text.lower()
    ), "Should say side number is wrong."


def test_one_die(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 4
    # Check function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 1d6")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "i roll 4" in data[0].text.lower(), "Should say it rolled 4."
    assert (
            mock_roller.last_min == 1
    ), "1 should be the minimum value for a die roll."
    assert (
            mock_roller.last_max == 6
    ), "6 Should be the maximum value for the d6 roll."
    assert mock_roller.last_count == 1, "Should have only rolled 1 die."


def test_many_dice(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = [1, 2, 6]
    # Check function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 3d10")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "i roll 1, 2, 6" in data[0].text.lower()
    ), "Should say it rolled 1, 2 and 6."
    assert (
            "total is 9" in data[0].text.lower()
    ), "Should have totalled the dice rolls to 9."
    assert (
            mock_roller.last_min == 1
    ), "1 should be the minimum value for any dice roll."
    assert (
            mock_roller.last_max == 10
    ), "6 Should be the maximum value for the d6 roll."
    assert mock_roller.last_count == 3, "Should have rolled 3 dice."


def test_roll_range(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 47
    # Check function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "roll 10-108")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "i roll 47" in data[0].text.lower(), "Should say it rolled 47."
    assert (
            mock_roller.last_min == 10
    ), "10 should be the minimum value for the range."
    assert (
            mock_roller.last_max == 108
    ), "108 Should be the maximum value for the range."
    assert mock_roller.last_count == 1, "Should have only picked one number."
