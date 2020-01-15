import os
import unittest

from events import EventMessage
from test.test_base import TestBase


class CatGifTest(TestBase, unittest.TestCase):

    def test_cat_gif_with_key(self):
        # Check API key is set
        if self.hallo.get_api_key("thecatapi") is None:
            # Read from env variable
            self.hallo.add_api_key("thecatapi", os.getenv("test_api_key_thecatapi"))
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "cat gif"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text.lower().startswith("http"), "Link not being returned."
        assert data[0].text.lower().endswith(".gif"), "Gif not being returned."

    def test_cat_gif_no_key(self):
        # Check there's no API key
        if self.hallo.get_api_key("thecatapi") is not None:
            del self.hallo.api_key_list["thecatapi"]
        # Test function
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "cat gif"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "no api key" in data[0].text.lower(), "Not warning about lack of API key."
        assert "cat api" in data[0].text.lower(), "Not specifying cat API."
