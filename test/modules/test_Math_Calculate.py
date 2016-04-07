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
        self.function_dispatcher.dispatch("calc pi", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "3.141" == data[0][0][:5], "pi != 3.141"

    def test_e(self):
        self.function_dispatcher.dispatch("calc e", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "2.718" == data[0][0][:5], "e != 2.718"

    def test_tan(self):
        self.function_dispatcher.dispatch("calc tan(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "tan(0) != 0"
        self.function_dispatcher.dispatch("calc tan(pi)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "tan(pi) != 0"
        self.function_dispatcher.dispatch("calc tan(pi/2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 10**6 < abs(float(data[0][0])), "abs(tan(pi/2)) < 1,000,000"

    def test_acos(self):
        self.function_dispatcher.dispatch("calc acos(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "acos(1) != 0"
        self.function_dispatcher.dispatch("calc acos(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "1.570" == data[0][0][:5], "acos(0) != pi/2"
        self.function_dispatcher.dispatch("calc acos(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "3.141" == data[0][0][:5], "acos(-1) != pi"

    def test_asin(self):
        self.function_dispatcher.dispatch("calc asin(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "sin(0) != 0"
        self.function_dispatcher.dispatch("calc asin(pi/2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "sin(pi/2) != 0"
        self.function_dispatcher.dispatch("calc asin(pi)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "sin(pi) != 0"

    def test_atan(self):
        assert False, "not yet implemented"

    def test_sqrt(self):
        self.function_dispatcher.dispatch("calc sqrt(4)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 2 == float(data[0][0]), "sqrt(4) != 2"
        self.function_dispatcher.dispatch("calc sqrt(2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "1.414" == data[0][0][:5], "sqrt(2) != 1.414"
        self.function_dispatcher.dispatch("calc sqrt(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "sqrt(1) != 1"
        self.function_dispatcher.dispatch("calc sqrt(2.25)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.5 == float(data[0][0]), "sqrt(2.25) != 1.5"
        self.function_dispatcher.dispatch("calc sqrt(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "cannot sqrt negative values" in data[0][0], "negative root response did not say it cannot sqrt " \
                                                            "negative numbers"
        assert "no complex numbers" in data[0][0], "negative root response did not say it does not support complex " \
                                                   "numbers"
        assert data[0][0][:5].lower() == "error", "negative root response did not start with error"

    def test_power(self):
        assert False, "not yet implemented"

    def test_hyperbolics(self):
        assert False, "not yet implemented"

    def test_gamma(self):
        self.function_dispatcher.dispatch("calc gamma(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "gamma(1) != 1"
        self.function_dispatcher.dispatch("calc gamma(5)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 24 == float(data[0][0]), "gamma(5) != 24"
