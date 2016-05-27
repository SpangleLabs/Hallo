import unittest

from Hallo import Hallo
from Server import Server
from test.TestBase import TestBase


class ShutdownTest(TestBase, unittest.TestCase):

    def test_shutdown(self):
        old_hallo = self.test_user.server.hallo
        try:
            mock_hallo = HalloMock()
            self.test_user.server.hallo = mock_hallo
            self.function_dispatcher.dispatch("shutdown", self.test_user, self.test_user)
            data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
            assert "error" not in data[0][0].lower()
            assert "shutting down" in data[0][0].lower()
            assert mock_hallo.shutdown
        finally:
            self.test_user.server.hallo = old_hallo


class HalloMock(Hallo):
    shutdown = False

    def close(self):
        self.shutdown = True
