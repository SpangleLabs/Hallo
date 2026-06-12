from hallo.events import EventMessage


async def test_change_options_simple(hallo_getter):
    test_hallo = await hallo_getter({"math"})
    await test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "change options 5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "[5]" in data[0].text, "Option missing from results."
    assert "[2,2,1]" in data[0].text, "Option missing from results."
    assert "[2,1,1,1]" in data[0].text, "Option missing from results."
    assert "[1,1,1,1,1]" in data[0].text, "Option missing from results."


async def test_change_options_over_limit(hallo_getter):
    test_hallo = await hallo_getter({"math"})
    await test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "change options 21")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Change options size limit has not been enforced."


async def test_change_options_negative(hallo_getter):
    test_hallo = await hallo_getter({"math"})
    await test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "change options -5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Change options should fail with negative input."


async def test_change_options_float(hallo_getter):
    test_hallo = await hallo_getter({"math"})
    await test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "change option 2.3")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Change options should fail with non-integer input."
