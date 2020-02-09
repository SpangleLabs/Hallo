from events import EventMessage


def test_avg_simple(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "average 2 4")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert float(data[0].text.split()[-1][:-1]) == 3, "average of 2 and 4 should be 3"


def test_avg_same(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "average 2 2 2 2 2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        float(data[0].text.split()[-1][:-1]) == 2
    ), "average of the same number should be the same number"


def test_avg_many(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, None, test_user, "average 2 7 4 6 32 4 1 17 12 12 100"
        )
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        data[0].text.split()[-1][:-1][:6] == "17.909"
    ), "average of many numbers calculated incorrectly"


def test_avg_floats(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "average 2.4 3.2 6.6 1.2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        round(float(data[0].text.split()[-1][:-1]), 2) == 3.35
    ), "average of floats incorrect"


def test_avg_negative(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "average -5 5 -10 10 -14 -16 13 17")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        float(data[0].text.split()[-1][:-1]) == 0
    ), "average including negatives was incorrect"


def test_avg_fail(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"math"})
    # Test that words fail
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, None, test_user, "average -5 5 hello 10 -14 -16 13 17"
        )
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" in data[0].text.lower(), "average of words should throw error"
    # Test that invalid numbers fail
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, None, test_user, "average -5 5 -10 10.0.0 -14 -16 13 17"
        )
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" in data[0].text.lower(), "Invalid numbers did not return error"
