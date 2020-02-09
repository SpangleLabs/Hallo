from events import EventMessage


def test_fraction_simple(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 6/4")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "3/2." in data[0].text[-4:], "Simplify fraction fails for small fractions."


def test_fraction_complex(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 360679/22")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "32789/2." in data[0].text[-8:]
    ), "Simplify fraction fails for large fractions."


def test_fraction_multi_slash(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 360679/22/2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Simplify fraction should return error when given more than 1 slash."


def test_fraction_integer(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 22/2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        " 11." == data[0].text[-4:]
    ), "Simplify fraction should return integer when result is integer."


def test_fraction_one_arg(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 104779")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Simplify fraction should return error when not given a fraction."


def test_fraction_unsimplify(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 17/3")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "17/3." == data[0].text[-5:]


def test_factors_float(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 17.5/2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Simplify fraction should return error when given a float."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 17/2.2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Simplify fraction should return error when given a float."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 6.6/2.2")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Simplify fraction should return error when given a float."


def test_factors_negative(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 24/-10")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        " -12/5." in data[0].text[-7:]
    ), "Simplify fraction not working for negative denominators."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction -24/10")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        " -12/5." in data[0].text[-7:]
    ), "Simplify fraction not working for negative numerators."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "fraction 24/10")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        " 12/5." in data[0].text[-6:]
    ), "Simplify fraction not working for negative numerators & denominators."


def test_factors_word(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "factors hello/7")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Simplify fraction should return error when invalid number used."
