from events import EventMessage


def test_factors_simple(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 6")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "2x3" in data[0].text, "Factors failing for small numbers."


def test_factors_big(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 295228")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "2x2x23x3209" in data[0].text, "Factors failing for large numbers."


def test_factors_negative(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors -17")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" in data[0].text.lower(), "Factors should fail with negative input."


def test_factors_float(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 17.5")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Factors should fail with non-integer input."


def test_factors_prime(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 104779")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "104779." == data[0].text[-7:], "Factors failing with largish primes."


def test_factors_fail(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors seventeen")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Factors not outputting error for non-numeric input."


def test_factors_calc(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 17+5")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "2x11." in data[0].text[-5:], "Factors not functioning for calculations."


def test_factors_calc_division(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 232234/83")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "2x1399." in data[0].text[-7:]
    ), "Factors not functioning for divisions resulting in integers."


def test_factors_calc_float(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors 232234/80")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Factors should return error when calculation results in non-integer."
