import unittest

from events import EventMessage
from test.test_base import TestBase


class DeerTest(TestBase, unittest.TestCase):

    def test_deer_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "deer"))
        data = self.server.get_send_data()
        assert "error" not in data[0].text, "Deer output should not produce errors."
        assert "\n" in data[0].text, "Deer output should be multiple lines."
