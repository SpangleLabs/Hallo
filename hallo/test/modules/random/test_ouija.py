from hallo.events import EventMessage


def test_one_word(mock_roller, mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 1
    # Check function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "ouija")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "message from the other side" in data[0].text
    words = data[0].text.split("...")[1].strip()[:-1]
    assert len(words.split()) == 1, "Only one word should be returned."
    assert (
            words in mock_chooser.last_choices
    ), "Word should be one of the choices given to chooser"
    assert mock_roller.last_min == 1, "Minimum word count should be one"
    assert mock_roller.last_max == 3, "Maximum word count should be three"


def test_three_words(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 3
    # Check function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "ouija")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "message from the other side" in data[0].text
    words = data[0].text.split("...")[1].strip()[:-1]
    assert len(words.split()) == 3, "Three words should be returned."
    assert mock_roller.last_min == 1, "Minimum word count should be one"
    assert mock_roller.last_max == 3, "Maximum word count should be three"


def test_word_list(mock_roller, mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 1
    # Check function
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "ouija")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "message from the other side" in data[0].text
    words = data[0].text.split("...")[1].strip()[:-1]
    assert len(words.split()) == 1, "Only one word should be returned."
    assert (
            words in mock_chooser.last_choices
    ), "Word should be one of the choices given to chooser"
    assert (
            len(mock_chooser.last_choices) > 1
    ), "Should be more than 1 word in word list."
