import unittest

import pytest

from events import EventMessage
from inc.commons import Commons
from test.test_base import TestBase
from test.modules.random.mock_roller import MockRoller


@pytest.mark.external_integration
class RandomColourTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.roller = MockRoller()
        self.old_int_method = Commons.get_random_int
        Commons.get_random_int = self.roller.roll

    def tearDown(self):
        super().tearDown()
        Commons.get_random_int = self.old_int_method

    def test_black(self):
        # Set RNG
        self.roller.answer = 0
        # Check
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "random colour")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
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
        assert self.roller.last_min == 0, "0 should be minimum colour value."
        assert self.roller.last_max == 255, "255 should be max colour value."
        assert self.roller.last_count == 3, "Should ask for 3 numbers."

    def test_white(self):
        # Set RNG
        self.roller.answer = 255
        # Check
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "random colour")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
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
        assert self.roller.last_min == 0, "0 should be minimum colour value."
        assert self.roller.last_max == 255, "255 should be max colour value."
        assert self.roller.last_count == 3, "Should ask for 3 numbers."

    def test_grey(self):
        # Set RNG
        self.roller.answer = 127
        # Check
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "random colour")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
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
        assert self.roller.last_min == 0, "0 should be minimum colour value."
        assert self.roller.last_max == 255, "255 should be max colour value."
        assert self.roller.last_count == 3, "Should ask for 3 numbers."

    def test_red(self):
        # Set RNG
        self.roller.answer = [255, 0, 0]
        # Check
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "random colour")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
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
        assert self.roller.last_min == 0, "0 should be minimum colour value."
        assert self.roller.last_max == 255, "255 should be max colour value."
        assert self.roller.last_count == 3, "Should ask for 3 numbers."

    def test_green(self):
        # Set RNG
        self.roller.answer = [0, 255, 0]
        # Check
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "random colour")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
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
        assert self.roller.last_min == 0, "0 should be minimum colour value."
        assert self.roller.last_max == 255, "255 should be max colour value."
        assert self.roller.last_count == 3, "Should ask for 3 numbers."

    def test_blue(self):
        # Set RNG
        self.roller.answer = [0, 0, 255]
        # Check
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "random colour")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
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
        assert self.roller.last_min == 0, "0 should be minimum colour value."
        assert self.roller.last_max == 255, "255 should be max colour value."
        assert self.roller.last_count == 3, "Should ask for 3 numbers."
