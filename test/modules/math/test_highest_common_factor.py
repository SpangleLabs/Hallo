from events import EventMessage
from modules.math import Hailstone


def test_hcf_simple(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf 5 13")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "1" == data[0].text[:-1][-1:]
    ), "Highest common factor function not returning correctly."


def test_hcf_big(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf 295228 285349")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "1" == data[0].text[-2:-1]
    ), "Highest common factor function not returning correctly."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf 295228 494644")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "4" == data[0].text[-2:-1]
    ), "Highest common factor function not returning correctly."


def test_hcf_one_arg(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf " + str(Hailstone.LIMIT + 1))
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor size limit has not been enforced."


def test_hcf_negative(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf -502 -124")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with negative inputs."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf 502 -124")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with negative input."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf -502 124")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with negative input."


def test_hcf_float(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hcf 2.3 13")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Highest common factor should fail with non-integer input."
