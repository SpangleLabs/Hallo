import os
import re
import unittest

import pytest

from events import EventMessage
from inc.commons import Commons
from test.test_base import TestBase
from test.modules.Random.mock_chooser import MockChooser


@pytest.mark.external_integration
class NightValeWeatherTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_weather(self):
        # Check API key is set
        if self.hallo.get_api_key("youtube") is None:
            # Read from env variable
            self.hallo.add_api_key("youtube", os.getenv("test_api_key_youtube"))
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "nightvale weather"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "and now, the weather" in data[0].text.lower(), "Didn't announce the weather"
        youtube_regex = re.compile(r"https?://youtu\.be/[A-Za-z0-9_\-]{11} .+")
        assert youtube_regex.search(data[0].text) is not None, "Youtube URL and title didn't appear in message"
        assert len(self.chooser.last_choices) > 1, "One or fewer videos was on the playlist."

    def test_passive(self):
        # Check API key is set
        if self.hallo.get_api_key("youtube") is None:
            # Read from env variable
            self.hallo.add_api_key("youtube", os.getenv("test_api_key_youtube"))
        self.function_dispatcher.dispatch_passive(
            EventMessage(self.server, self.test_chan, self.test_user,
                         "and now to {} with the weather".format(self.server.get_nick())))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "and now, the weather" in data[0].text.lower(), "Didn't announce the weather"
        youtube_regex = re.compile(r"https?://youtu\.be/[A-Za-z0-9_\-]{11} .+")
        assert youtube_regex.search(data[0].text) is not None, "Youtube URL and title didn't appear in message"
        assert len(self.chooser.last_choices) > 1, "One or fewer videos was on the playlist."

    def test_no_api_key(self):
        # Check there's no API key
        if self.hallo.get_api_key("youtube") is not None:
            del self.hallo.api_key_list["youtube"]
        # Test function
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "nightvale weather"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no api key" in data[0].text.lower(), "Not warning about lack of API key."
        assert "youtube" in data[0].text.lower(), "Not specifying youtube API."
