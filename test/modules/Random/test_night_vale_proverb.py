import unittest

from events import EventMessage
from inc.commons import Commons
from modules.random import NightValeProverb
from test.test_base import TestBase
from test.modules.Random.mock_chooser import MockChooser


class NightValeProverbTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_proverb(self):
        # Get proverb list
        n = NightValeProverb()
        proverb_list = n.proverb_list
        response_list = []
        # Check all proverbs are given
        for x in range(len(proverb_list)):
            # Set RNG
            self.chooser.choice = x
            # Check function
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "nightvale proverb"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert data[0].text in proverb_list, "Proverb isn't from list"
            response_list.append(data[0].text)
        assert len(response_list) == len(proverb_list), "Not all proverbs options given?"
        assert set(response_list) == set(proverb_list), "Proverb options didn't match"
