from hallo.events import EventMessage
from hallo.modules.math import Hailstone


def test_hcf_simple(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf 5 13")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "1" == data[0].text[:-1][-1:]
    ), "Highest common factor function not returning correctly."


def test_hcf_big(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf 295228 285349")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "1" == data[0].text[-2:-1]
    ), "Highest common factor function not returning correctly."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf 295228 494644")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "4" == data[0].text[-2:-1]
    ), "Highest common factor function not returning correctly."


def test_hcf_one_arg(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf " + str(Hailstone.LIMIT + 1))
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor size limit has not been enforced."


def test_hcf_negative(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf -502 -124")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with negative inputs."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf 502 -124")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with negative input."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf -502 124")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with negative input."


def test_hcf_float(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "hcf 2.3 13")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with non-integer input."
