import unittest

from hallo.events import EventMessage
from hallo.inc.commons import Commons
from hallo.test.test_base import TestBase
from hallo.test.modules.random.mock_roller import MockRoller


class RollTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.roller = MockRoller()
        self.old_int_method = Commons.get_random_int
        Commons.get_random_int = self.roller.roll

    def tearDown(self):
        super().tearDown()
        Commons.get_random_int = self.old_int_method

    def test_invalid_dice(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll fd6")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "please give input in the form" in data[0].text.lower()
        ), "Should ask for correct format."
        assert "x-y" in data[0].text.lower(), "Should offer range format."
        assert "xdy" in data[0].text.lower(), "Should offer dice format."
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 6df")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "please give input in the form" in data[0].text.lower()
        ), "Should ask for correct format."
        assert "x-y" in data[0].text.lower(), "Should offer range format."
        assert "xdy" in data[0].text.lower(), "Should offer dice format."

    def test_invalid_range(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 1-f")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "please give input in the form" in data[0].text.lower()
        ), "Should ask for correct format."
        assert "x-y" in data[0].text.lower(), "Should offer range format."
        assert "xdy" in data[0].text.lower(), "Should offer dice format."
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll b-16")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "please give input in the form" in data[0].text.lower()
        ), "Should ask for correct format."
        assert "x-y" in data[0].text.lower(), "Should offer range format."
        assert "xdy" in data[0].text.lower(), "Should offer dice format."

    def test_zero_dice(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 0d6")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "invalid number of dice" in data[0].text.lower()
        ), "Should say dice number is wrong."

    def test_too_many_dice(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 100000d6")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "invalid number of dice" in data[0].text.lower()
        ), "Should say dice number is wrong."

    def test_zero_sides(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 4d0")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "invalid number of sides" in data[0].text.lower()
        ), "Should say side number is wrong."

    def test_too_many_sides(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 4d99999999")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "invalid number of sides" in data[0].text.lower()
        ), "Should say side number is wrong."

    def test_one_die(self):
        # Set RNG
        self.roller.answer = 4
        # Check function
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 1d6")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i roll 4" in data[0].text.lower(), "Should say it rolled 4."
        assert (
            self.roller.last_min == 1
        ), "1 should be the minimum value for a die roll."
        assert (
            self.roller.last_max == 6
        ), "6 Should be the maximum value for the d6 roll."
        assert self.roller.last_count == 1, "Should have only rolled 1 die."

    def test_many_dice(self):
        # Set RNG
        self.roller.answer = [1, 2, 6]
        # Check function
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 3d10")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "i roll 1, 2, 6" in data[0].text.lower()
        ), "Should say it rolled 1, 2 and 6."
        assert (
            "total is 9" in data[0].text.lower()
        ), "Should have totalled the dice rolls to 9."
        assert (
            self.roller.last_min == 1
        ), "1 should be the minimum value for any dice roll."
        assert (
            self.roller.last_max == 10
        ), "6 Should be the maximum value for the d6 roll."
        assert self.roller.last_count == 3, "Should have rolled 3 dice."

    def test_roll_range(self):
        # Set RNG
        self.roller.answer = 47
        # Check function
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "roll 10-108")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i roll 47" in data[0].text.lower(), "Should say it rolled 47."
        assert (
            self.roller.last_min == 10
        ), "10 should be the minimum value for the range."
        assert (
            self.roller.last_max == 108
        ), "108 Should be the maximum value for the range."
        assert self.roller.last_count == 1, "Should have only picked one number."
