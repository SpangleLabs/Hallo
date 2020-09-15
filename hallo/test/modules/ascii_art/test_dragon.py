from hallo.events import EventMessage


def test_dragon_simple(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"ascii_art"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "dragon")
    )
    data = test_server.get_send_data()
    assert "error" not in data[0].text, "Dragon output should not produce errors."
    assert "\n" in data[0].text, "Dragon output should be multiple lines."


def test_dragon_deer(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"ascii_art"})
    found_deer = False
    for _ in range(1000):
        hallo.function_dispatcher.dispatch(
            EventMessage(test_server, None, test_user, "dragon")
        )
        data = test_server.get_send_data()
        assert "error" not in data[0].text, "Dragon output should not contain errors."
        assert "\n" in data[0].text, "Dragon output should be multiple lines."
        if "deer" in data[0].text:
            found_deer = True
    assert found_deer, "In 1000 runs, at least 1 call to dragon should return deer."
