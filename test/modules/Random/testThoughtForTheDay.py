import unittest

from Events import EventMessage
from inc.Commons import Commons
from modules.Random import NightValeProverb, Scriptures, ThoughtForTheDay
from test.TestBase import TestBase
from test.modules.Random.testChoose import MockChooser


class ThoughtForTheDayTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_tftd(self):
        # Get proverb list
        n = ThoughtForTheDay()
        thought_list = n.thought_list
        response_list = []
        # Check all thoughts are given
        for x in range(len(thought_list)):
            # Set RNG
            self.chooser.choice = x
            # Check function
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "thought for the day"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert data[0].text[0] == data[0].text[-1] == "\"", "Thought isn't quoted."
            assert any(x in data[0].text[1:-1] for x in thought_list), \
                "Thought isn't from list: {}".format(data[0].text)
            assert data[0].text[-2] in [".", "!", "?"], "Thought doesn't end with correct punctuation."
            response_list.append(data[0].text)
        assert len(set(response_list)) == len(set(thought_list)), "Not all thought options given?"
