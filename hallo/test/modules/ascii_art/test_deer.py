from hallo.events import EventMessage


def test_deer_simple(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"ascii_art"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "deer")
    )
    data = test_server.get_send_data()
    assert "error" not in data[0].text, "Deer output should not produce errors."
    assert "\n" in data[0].text, "Deer output should be multiple lines."
