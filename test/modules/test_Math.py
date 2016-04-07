import unittest

from Server import Server
from test.TestBase import TestBase


class MathTest(TestBase, unittest.TestCase):

    def test_calc_simple(self):
        self.function_dispatcher.dispatch("calc 2+2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "4"

    def test_calc_multiply(self):
        self.function_dispatcher.dispatch("calc 21*56", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "1176"

    def test_calc_divide(self):
        self.function_dispatcher.dispatch("calc 1/5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "0.2"
