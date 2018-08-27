import unittest

from Events import EventMessage
from test.TestBase import TestBase


class LongCatTest(TestBase, unittest.TestCase):

    def test_long_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "longcat"))
        data = self.server.get_send_data()
        assert "error" not in data[0][0], "Longcat output should not produce errors."
        assert "\n" in data[0][0], "Longcat output should be multiple lines."

    def test_long_long(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "longcat"))
        data = self.server.get_send_data()
        norm_len = data[0][0].count("\n")
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "longcat 10"))
        data = self.server.get_send_data()
        long_len = data[0][0].count("\n")
        assert long_len > norm_len, "Longcat should be able to be longer"
