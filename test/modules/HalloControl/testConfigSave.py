import unittest

from Hallo import Hallo
from Server import Server
from test.TestBase import TestBase


class ConfigSaveTest(TestBase, unittest.TestCase):

    def test_save_config(self):
        old_hallo = self.test_user.server.hallo
        try:
            mock_hallo = HalloMock()
            self.test_user.server.hallo = mock_hallo
            self.function_dispatcher.dispatch("config save", self.test_user, self.test_user)
            data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
            assert "error" not in data[0][0].lower()
            assert "config has been saved" in data[0][0].lower()
            assert mock_hallo.saved_to_xml
        finally:
            self.test_user.server.hallo = old_hallo


class HalloMock(Hallo):
    saved_to_xml = False

    def save_to_xml(self):
        self.saved_to_xml = True
