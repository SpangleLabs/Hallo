from hallo.events import EventMessage


def test_deer_simple(hallo_getter):
    test_hallo = hallo_getter({"ascii_art"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "deer")
    )
    data = test_hallo.test_server.get_send_data()
    assert "error" not in data[0].text, "Deer output should not produce errors."
    assert "\n" in data[0].text, "Deer output should be multiple lines."
