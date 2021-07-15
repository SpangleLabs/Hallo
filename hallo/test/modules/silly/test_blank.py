from hallo.events import EventMessage


def test_blank_empty(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch(EventMessage(test_hallo.test_server, None, test_hallo.test_user, ""))
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "yes?" == data[0].text.lower(), "Blank function not working."


def test_blank_channel(hallo_getter):
    test_hallo = hallo_getter({"silly"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "yes?" == data[0].text.lower(), "Blank function not working in channel."
