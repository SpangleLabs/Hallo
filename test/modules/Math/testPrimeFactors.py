import unittest

from Server import Server
from test.TestBase import TestBase


class PrimeFactorsTest(TestBase, unittest.TestCase):

    def test_factors_simple(self):
        self.function_dispatcher.dispatch("factors 6", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "2x3" in data[0][0], "Factors failing for small numbers."

    def test_factors_big(self):
        self.function_dispatcher.dispatch("factors 295228", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "2x2x23x3209" in data[0][0], "Factors failing for large numbers."

    def test_factors_negative(self):
        self.function_dispatcher.dispatch("factors -17", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Factors should fail with negative input."

    def test_factors_float(self):
        self.function_dispatcher.dispatch("factors 17.5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Factors should fail with non-integer input."

    def test_factors_prime(self):
        self.function_dispatcher.dispatch("factors 104779", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "104779." == data[0][0][-7:], "Factors failing with largish primes."

    def test_factors_fail(self):
        self.function_dispatcher.dispatch("factors seventeen", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Factors not outputting error for non-numeric input."

    def test_factors_calc(self):
        self.function_dispatcher.dispatch("factors 17+5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "2x11." in data[0][0][-5:], "Factors not functioning for calculations."

    def test_factors_calc_division(self):
        self.function_dispatcher.dispatch("factors 232234/83", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "2x1399." in data[0][0][-7:], "Factors not functioning for divisions resulting in integers."

    def test_factors_calc_float(self):
        self.function_dispatcher.dispatch("factors 232234/80", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Factors should return error when calculation results in non-integer."