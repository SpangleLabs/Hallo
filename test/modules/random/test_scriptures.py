import unittest

from events import EventMessage
from inc.commons import Commons
from modules.random import Scriptures
from test.test_base import TestBase
from test.modules.random.mock_chooser import MockChooser


class ScripturesTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_scripture(self):
        # Get proverb list
        n = Scriptures()
        scripture_list = n.scripture_list
        response_list = []
        # Check all scriptures are given
        for x in range(len(scripture_list)):
            # Set RNG
            self.chooser.choice = x
            # Check function
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "amarr scriptures"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert data[0].text in scripture_list, "Scripture isn't from list"
            response_list.append(data[0].text)
        assert len(response_list) == len(scripture_list), "Not all scripture options given?"
        assert set(response_list) == set(scripture_list), "Scripture options didn't match"
