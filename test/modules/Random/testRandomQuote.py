import os
import re
import unittest

from Events import EventMessage
from test.TestBase import TestBase


class QuoteTest(TestBase, unittest.TestCase):

    def test_quote(self):
        # Check API key is set
        if self.hallo.get_api_key("mashape") is None:
            # Read from env variable
            self.hallo.add_api_key("mashape", os.getenv("test_api_key_mashape"))
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "random quote"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        quote_regex = re.compile(r"\".+\" - .+")
        assert quote_regex.match(data[0].text) is not None, "Quote and author not in response."

    def test_quote_no_key(self):
        # Check there's no API key
        if self.hallo.get_api_key("mashape") is not None:
            del self.hallo.api_key_list["mashape"]
        # Test function
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "random quote"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no api key" in data[0].text.lower(), "Not warning about lack of API key."
        assert "mashape" in data[0].text.lower(), "Not specifying mashape API."
