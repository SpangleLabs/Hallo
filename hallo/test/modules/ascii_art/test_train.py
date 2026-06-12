from hallo.events import EventMessage


async def test_train_simple(hallo_getter):
    test_hallo = await hallo_getter({"ascii_art"})
    await test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "train")
    )
    data = test_hallo.test_server.get_send_data()
    assert "error" not in data[0].text, "Train output should not produce errors."
    assert "\n" in data[0].text, "Train output should be multiple lines."
    assert "chugga chugga" in data[0].text, "Train needs to say chugga chugga."
