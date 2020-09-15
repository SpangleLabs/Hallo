from hallo.events import EventMessage


def test_blank_empty(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"silly"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "is"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "i am?" == data[0].text.lower(), "Is function not working."
