from datetime import datetime

from hallo.events import EventMessage


def test_short_doof(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    for x in range(21):
        # Set RNG
        mock_roller.answer = x
        # Check
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "fooooooof")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "doof" == data[0].text.lower(), "Should be short doof."


def test_medium_doof(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    for x in range(21, 41):
        # Set RNG
        mock_roller.answer = x
        # Check
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "foof")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "doooooof" == data[0].text.lower(), "Should be medium doof."


def test_long_doof(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    for x in range(41, 60):
        if x == 40 + 15:
            continue
        # Set RNG
        mock_roller.answer = x
        # Check
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "foooof")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert (
                "ddddoooooooooooooooooooooffffffffff." == data[0].text.lower()
        ), "Should be long doof."


def test_mega_doof(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 55
    # Check
    start_time = datetime.now()
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "foof")
    )
    end_time = datetime.now()
    data = test_hallo.test_server.get_send_data(2, test_hallo.test_user, EventMessage)
    assert "powering up..." == data[0].text.lower(), "Should have powered up."
    assert (
                   end_time - start_time
           ).seconds > 3, "Should have had a delay between powering up and mega doof."
    assert len(data[1].text.lower()) > 1000, "doof should be extra long."
    assert "!" in data[1].text, "doof should have exclamation mark."


def test_passive_foof(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    mock_roller.answer = 0
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "foof")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "doof" == data[0].text.lower(), "Should be short doof."


def test_passive_foof_exclamation(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    mock_roller.answer = 0
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "foof!")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "doof" == data[0].text.lower(), "Should be short doof."


def test_passive_long_foof(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    mock_roller.answer = 0
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "foooooooooooooooof"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "doof" == data[0].text.lower(), "Should be short doof."
