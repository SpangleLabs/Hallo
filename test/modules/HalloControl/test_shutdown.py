import unittest

from events import EventMessage
from hallo import Hallo
from test.test_base import TestBase


class ShutdownTest(TestBase, unittest.TestCase):

    def test_shutdown(self):
        old_hallo = self.test_user.server.hallo
        try:
            mock_hallo = HalloMock()
            self.test_user.server.hallo = mock_hallo
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "shutdown"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "error" not in data[0].text.lower()
            assert "shutting down" in data[0].text.lower()
            assert mock_hallo.shutdown
        finally:
            self.test_user.server.hallo = old_hallo


class HalloMock(Hallo):
    shutdown = False

    def close(self):
        self.shutdown = True
