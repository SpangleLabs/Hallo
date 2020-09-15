from hallo.events import EventMessage


def test_alarm_simple(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"silly"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "alarm")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "wooo" in data[0].text.lower(), "Alarm function not going woo."


def test_alarm_word(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"silly"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "alarm nerd")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "wooo" in data[0].text.lower(), "Alarm function not going woo."
    assert (
        "nerd" in data[0].text.lower()
    ), "Alarm function not going responding with word input."
