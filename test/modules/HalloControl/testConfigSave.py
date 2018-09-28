import unittest

from Events import EventMessage
from Hallo import Hallo
from test.TestBase import TestBase


class ConfigSaveTest(TestBase, unittest.TestCase):

    def test_save_config(self):
        old_hallo = self.test_user.server.hallo
        try:
            mock_hallo = HalloMock()
            self.test_user.server.hallo = mock_hallo
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "config save"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "error" not in data[0].text.lower()
            assert "config has been saved" in data[0].text.lower()
            assert mock_hallo.saved_to_json
        finally:
            self.test_user.server.hallo = old_hallo


class HalloMock(Hallo):
    saved_to_json = False

    def save_json(self):
        self.saved_to_json = True
