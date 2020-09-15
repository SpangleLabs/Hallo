from hallo.events import EventMessage
from hallo.modules.math import Hailstone


def test_hailstone_simple(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hailstone 5")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "5->16->8->4->2->1" in data[0].text
    ), "Hailstone function not returning correctly."


def test_hailstone_over_limit(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(
            test_server, None, test_user, "hailstone " + str(Hailstone.LIMIT + 1)
        )
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Hailstone size limit has not been enforced."


def test_hailstone_negative(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hailstone -5")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" in data[0].text.lower(), "Hailstone should fail with negative input."


def test_hailstone_float(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "hailstone 2.3")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Hailstone should fail with non-integer input."
