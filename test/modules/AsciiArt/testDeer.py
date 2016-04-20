import unittest

from test.TestBase import TestBase


class DeerTest(TestBase, unittest.TestCase):

    def test_deer_simple(self):
        self.function_dispatcher.dispatch("deer", self.test_user, self.test_user)
        data = self.server.get_send_data()
        assert "error" not in data[0][0], "Deer output should not produce errors."
        assert "\n" in data[0][0], "Deer output should be multiple lines."
