import unittest

from Server import Server
from test.TestBase import TestBase


class CalculateTest(TestBase, unittest.TestCase):

    def test_calc_simple(self):
        self.function_dispatcher.dispatch("calc 2+2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "4", "2+2 != 4"

    def test_calc_multiply(self):
        self.function_dispatcher.dispatch("calc 21*56", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "1176", "21*56 != 1176"

    def test_calc_divide(self):
        self.function_dispatcher.dispatch("calc 1/5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "0.2", "1/5 != 0.2"

    def test_calc_subtract(self):
        self.function_dispatcher.dispatch("calc 13-17", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0] == "-4", "13-17 != -4"

    def test_calc_div_zero(self):
        self.function_dispatcher.dispatch("calc 1/0", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "no division by zero" in data[0][0], "division by zero response did no specify problem"
        assert data[0][0][:5].lower() == "error", "division by zero response did not start with error"

    def test_cos(self):
        self.function_dispatcher.dispatch("calc cos(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "cos(0) != 1"
        self.function_dispatcher.dispatch("calc cos(pi/2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "cos(pi/2) != 0"
        self.function_dispatcher.dispatch("calc cos(pi)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -1 == float(data[0][0]), "cos(pi) != -1"

    def test_sin(self):
        self.function_dispatcher.dispatch("calc sin(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "sin(0) != 0"
        self.function_dispatcher.dispatch("calc sin(pi/2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "sin(pi/2) != 0"
        self.function_dispatcher.dispatch("calc sin(pi)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "sin(pi) != 0"

    def test_order_of_operations(self):
        assert False, "not yet implemented"

    def test_brackets(self):
        assert False, "not yet implemented"

    def test_pi(self):
        assert False, "not yet implemented"

    def test_e(self):
        assert False, "not yet implemented"

    def test_tan(self):
        assert False, "not yet implemented"

    def test_acos(self):
        self.function_dispatcher.dispatch("calc acos(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "acos(1) != 0"
        self.function_dispatcher.dispatch("calc acos(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert  == float(data[0][0]), "acos(0) != pi/2"
        self.function_dispatcher.dispatch("calc acos(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -1 == float(data[0][0]), "acos(-1) != pi"

    def test_asin(self):
        assert False, "not yet implemented"

    def test_atan(self):
        assert False, "not yet implemented"

    def test_sqrt(self):
        assert False, "not yet implemented"

    def test_power(self):
        assert False, "not yet implemented"

    def test_hyperbolics(self):
        assert False, "not yet implemented"

    def test_gamma(self):
        assert False, "not yet implemented"
