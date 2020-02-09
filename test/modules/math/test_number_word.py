from events import EventMessage


def test_number_simple(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 5")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "five." == data[0].text, "Number word failing for small numbers."


def test_number_big(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 295228")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "two hundred and ninety-five thousand, two hundred and twenty-eight."
        == data[0].text.lower()
    )


def test_number_teen(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 17")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "seventeen." == data[0].text.lower()
    ), "Number word failing for 'teen' numbers."


def test_number_negative(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number -502")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "negative five hundred and two." == data[0].text.lower()
    ), "Number word failing for negative numbers."


def test_number_float(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 2.3")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "two point three" in data[0].text.lower()
    ), "Number word failing for non-integers."
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 2.357")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "two point three five seven." == data[0].text.lower()
    ), "Number word failing for non-integers."


def test_number_american(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 1000000000 american")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "one billion." == data[0].text.lower()
    ), "Number word failing for american formatting."


def test_number_british(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 1000000000 british")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "one thousand million." == data[0].text.lower()
    ), "Number word failing for british formatting."


def test_number_european(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 1000000000 european")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "one milliard." == data[0].text.lower()
    ), "Number word failing for european formatting."


def test_number_calculation(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number 17*5")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "eighty-five." == data[0].text.lower()
    ), "Number word failing for calculations."


def test_number_fail(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"math"})
    hallo.function_dispatcher.dispatch(
        EventMessage(test_server, None, test_user, "number seventeen")
    )
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Number word not outputting error for non-numeric input."
