from hallo.events import EventMessage


def test_long_simple(hallo_getter):
    test_hallo = hallo_getter({"ascii_art"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "longcat")
    )
    data = test_hallo.test_server.get_send_data()
    assert "error" not in data[0].text, "Longcat output should not produce errors."
    assert "\n" in data[0].text, "Longcat output should be multiple lines."


def test_long_long(hallo_getter):
    test_hallo = hallo_getter({"ascii_art"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "longcat")
    )
    data = test_hallo.test_server.get_send_data()
    norm_len = data[0].text.count("\n")
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "longcat 10")
    )
    data = test_hallo.test_server.get_send_data()
    long_len = data[0].text.count("\n")
    assert long_len > norm_len, "Longcat should be able to be longer"
