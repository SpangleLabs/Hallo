from hallo.events import EventMessage


def test_alarm_simple(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "alarm")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "wooo" in data[0].text.lower(), "Alarm function not going woo."


def test_alarm_word(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "alarm nerd")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "wooo" in data[0].text.lower(), "Alarm function not going woo."
    assert (
        "nerd" in data[0].text.lower()
    ), "Alarm function not going responding with word input."
