import pytest

from hallo.events import EventMessage


@pytest.mark.external_integration
def test_black(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 0
    # Check
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random colour")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "randomly chosen colour is" in data[0].text.lower()
    ), "Should state that a colour is chosen."
    assert (
            "https://www.thecolorapi.com" in data[0].text
    ), "URL should be in response."
    assert "format=html" in data[0].text, "URL should specify HTML format."
    assert "black" in data[0].text.lower(), "Colour should be named black."
    assert "#000000" in data[0].text, "Hex code should be #000000"
    assert "rgb(0,0,0)" in data[0].text, "RGB code should be stated as 0,0,0"
    assert mock_roller.last_min == 0, "0 should be minimum colour value."
    assert mock_roller.last_max == 255, "255 should be max colour value."
    assert mock_roller.last_count == 3, "Should ask for 3 numbers."


@pytest.mark.external_integration
def test_white(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 255
    # Check
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random colour")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "randomly chosen colour is" in data[0].text.lower()
    ), "Should state that a colour is chosen."
    assert (
            "https://www.thecolorapi.com" in data[0].text
    ), "URL should be in response."
    assert "format=html" in data[0].text, "URL should specify HTML format."
    assert "white" in data[0].text.lower(), "Colour should be named white."
    assert "#ffffff" in data[0].text.lower(), "Hex code should be #FFFFFF"
    assert (
            "rgb(255,255,255)" in data[0].text
    ), "RGB code should be stated as 255,255,255"
    assert mock_roller.last_min == 0, "0 should be minimum colour value."
    assert mock_roller.last_max == 255, "255 should be max colour value."
    assert mock_roller.last_count == 3, "Should ask for 3 numbers."


@pytest.mark.external_integration
def test_grey(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = 127
    # Check
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random colour")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "randomly chosen colour is" in data[0].text.lower()
    ), "Should state that a colour is chosen."
    assert (
            "https://www.thecolorapi.com" in data[0].text
    ), "URL should be in response."
    assert "format=html" in data[0].text, "URL should specify HTML format."
    assert "gray" in data[0].text.lower(), "Colour should be named gray."
    assert "#7f7f7f" in data[0].text.lower(), "Hex code should be #7f7f7f"
    assert (
            "rgb(127,127,127)" in data[0].text
    ), "RGB code should be stated as 127,127,127"
    assert mock_roller.last_min == 0, "0 should be minimum colour value."
    assert mock_roller.last_max == 255, "255 should be max colour value."
    assert mock_roller.last_count == 3, "Should ask for 3 numbers."


@pytest.mark.external_integration
def test_red(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = [255, 0, 0]
    # Check
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random colour")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "randomly chosen colour is" in data[0].text.lower()
    ), "Should state that a colour is chosen."
    assert (
            "https://www.thecolorapi.com" in data[0].text
    ), "URL should be in response."
    assert "format=html" in data[0].text, "URL should specify HTML format."
    assert "red" in data[0].text.lower(), "Colour should be named red."
    assert "#ff0000" in data[0].text.lower(), "Hex code should be #ff0000"
    assert "rgb(255,0,0)" in data[0].text, "RGB code should be stated as 255,0,0"
    assert mock_roller.last_min == 0, "0 should be minimum colour value."
    assert mock_roller.last_max == 255, "255 should be max colour value."
    assert mock_roller.last_count == 3, "Should ask for 3 numbers."


@pytest.mark.external_integration
def test_green(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = [0, 255, 0]
    # Check
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random colour")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "randomly chosen colour is" in data[0].text.lower()
    ), "Should state that a colour is chosen."
    assert (
            "https://www.thecolorapi.com" in data[0].text
    ), "URL should be in response."
    assert "format=html" in data[0].text, "URL should specify HTML format."
    assert "green" in data[0].text.lower(), "Colour should be named green."
    assert "#00ff00" in data[0].text.lower(), "Hex code should be #00ff00"
    assert "rgb(0,255,0)" in data[0].text, "RGB code should be stated as 0,255,0"
    assert mock_roller.last_min == 0, "0 should be minimum colour value."
    assert mock_roller.last_max == 255, "255 should be max colour value."
    assert mock_roller.last_count == 3, "Should ask for 3 numbers."


@pytest.mark.external_integration
def test_blue(mock_roller, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Set RNG
    mock_roller.answer = [0, 0, 255]
    # Check
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "random colour")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "randomly chosen colour is" in data[0].text.lower()
    ), "Should state that a colour is chosen."
    assert (
            "https://www.thecolorapi.com" in data[0].text
    ), "URL should be in response."
    assert "format=html" in data[0].text, "URL should specify HTML format."
    assert "blue" in data[0].text.lower(), "Colour should be named blue."
    assert "#0000ff" in data[0].text.lower(), "Hex code should be #0000ff"
    assert "rgb(0,0,255)" in data[0].text, "RGB code should be stated as 0,0,255"
    assert mock_roller.last_min == 0, "0 should be minimum colour value."
    assert mock_roller.last_max == 255, "255 should be max colour value."
    assert mock_roller.last_count == 3, "Should ask for 3 numbers."
