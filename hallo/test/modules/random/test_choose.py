import unittest

from hallo.events import EventMessage
from hallo.inc.commons import Commons
from hallo.test.test_base import TestBase
from hallo.test.modules.random.mock_chooser import MockChooser


class ChooseTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_no_options(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "more than 1 thing" in data[0].text.lower()
        ), "Not warning about single option."

    def test_one_option(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "more than 1 thing" in data[0].text.lower()
        ), "Not warning about single option."

    def test_x_or_y(self):
        # Set mock value
        self.chooser.choice = 0
        # Choose x
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or y")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"x"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 1
        # Choose y
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or y")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"y"' in data[0].text.lower()

    def test_x_comma_y(self):
        # Set mock value
        self.chooser.choice = 0
        # Choose x
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x, y")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"x"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 1
        # Choose y
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x, y")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"y"' in data[0].text.lower()

    def test_x_or_comma_y(self):
        # Set mock value
        self.chooser.choice = 0
        # Choose x
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or, y")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"x"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 1
        # Choose y
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or, y")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"y"' in data[0].text.lower()

    def test_x_y_z(self):
        # Set mock value
        self.chooser.choice = 0
        # Choose x
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or y or z")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y", "z"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"x"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 1
        # Choose y
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or y or z")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y", "z"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"y"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 2
        # Choose z
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or y or z")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y", "z"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"z"' in data[0].text.lower()

    def test_multiple_separators(self):
        # Set mock value
        self.chooser.choice = 0
        # Choose x
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x, y or z")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y", "z"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"x"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 1
        # Choose y
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x or y or, z")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y", "z"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"y"' in data[0].text.lower()
        # Set mock value
        self.chooser.choice = 2
        # Choose z
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "choose x, y or, z")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.chooser.last_choices == ["x", "y", "z"]
        assert self.chooser.last_count == 1
        assert "i choose" in data[0].text.lower()
        assert '"z"' in data[0].text.lower()
