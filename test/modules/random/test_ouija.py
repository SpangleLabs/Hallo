import unittest

from events import EventMessage
from inc.commons import Commons
from test.test_base import TestBase
from test.modules.random.mock_chooser import MockChooser
from test.modules.random.mock_roller import MockRoller


class OuijaTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.roller = MockRoller()
        self.old_int_method = Commons.get_random_int
        Commons.get_random_int = self.roller.roll
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_int = self.old_int_method
        Commons.get_random_choice = self.old_choice_method

    def test_one_word(self):
        # Set RNG
        self.roller.answer = 1
        # Check function
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "ouija"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "message from the other side" in data[0].text
        words = data[0].text.split("...")[1].strip()[:-1]
        assert len(words.split()) == 1, "Only one word should be returned."
        assert words in self.chooser.last_choices, "Word should be one of the choices given to chooser"
        assert self.roller.last_min == 1, "Minimum word count should be one"
        assert self.roller.last_max == 3, "Maximum word count should be three"

    def test_three_words(self):
        # Set RNG
        self.roller.answer = 3
        # Check function
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "ouija"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "message from the other side" in data[0].text
        words = data[0].text.split("...")[1].strip()[:-1]
        assert len(words.split()) == 3, "Three words should be returned."
        assert self.roller.last_min == 1, "Minimum word count should be one"
        assert self.roller.last_max == 3, "Maximum word count should be three"

    def test_word_list(self):
        # Set RNG
        self.roller.answer = 1
        # Check function
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "ouija"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "message from the other side" in data[0].text
        words = data[0].text.split("...")[1].strip()[:-1]
        assert len(words.split()) == 1, "Only one word should be returned."
        assert words in self.chooser.last_choices, "Word should be one of the choices given to chooser"
        assert len(self.chooser.last_choices) > 1, "Should be more than 1 word in word list."
