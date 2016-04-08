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
        assert "error" in data[0][0].lower(), "division by zero should fail"
        assert "no division by zero" in data[0][0], "division by zero response did no specify problem"

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
        self.function_dispatcher.dispatch("calc 6+7*8", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 62 == float(data[0][0]), "6+7*8 != 62"
        self.function_dispatcher.dispatch("calc 16/8-2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "16/8-2 != 0"
        self.function_dispatcher.dispatch("calc 9-5/(8-3)*2+6", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 13 == float(data[0][0]), "9-5/(8-3)*2+6 != 13"
        self.function_dispatcher.dispatch("calc 150/(6+3*8)-5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), " 150/(6+3*8)-5 != 0"

    def test_brackets(self):
        self.function_dispatcher.dispatch("calc (25-11)*3", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 42 == float(data[0][0]), "(25-11)*3 != 42"
        self.function_dispatcher.dispatch("calc 4+(-1(-2-1))^2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 13 == float(data[0][0]), "4+(-1(-2-1))^2 != 13"
        self.function_dispatcher.dispatch("calc 2(3+4)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 14 == float(data[0][0]), "2(3+4) != 14"
        self.function_dispatcher.dispatch("calc (3+4)3", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 21 == float(data[0][0]), "(3+4)3 != 21"
        self.function_dispatcher.dispatch("calc (((17*3)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "(((17*3) should fail"
        self.function_dispatcher.dispatch("calc (21/3))+2))*5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "(21/3))+2))*5 should fail"
        self.function_dispatcher.dispatch("calc ((15*(3))())", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "((15*(3))()) should fail"
        self.function_dispatcher.dispatch("calc (3)-(7)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -4 == float(data[0][0]), "(3)-(7) != -4"
        self.function_dispatcher.dispatch("calc e(3+4)pi", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 59.778 == float(data[0][0][:6]), "e(3+4)pi != 59.778"
        self.function_dispatcher.dispatch("calc cos(acos(0.7))", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0.7 == round(float(data[0][0]), 5), "cos(acos(0.7)) != 0.7"

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
        self.function_dispatcher.dispatch("calc acos(2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0], "acos(2) should fail"

    def test_asin(self):
        self.function_dispatcher.dispatch("calc asin(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "asin(0) != 0"
        self.function_dispatcher.dispatch("calc asin(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.5707 == float(data[0][0][:6]), "asin(1) != pi/2"
        self.function_dispatcher.dispatch("calc asin(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -1.5707 == float(data[0][0][:7]), "asin(-1) != -pi/2"
        self.function_dispatcher.dispatch("calc asin(2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0], "asin(2) should fail"

    def test_atan(self):
        self.function_dispatcher.dispatch("calc atan(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "atan(0) != 0"
        self.function_dispatcher.dispatch("calc atan(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0.785 == float(data[0][0][:5]), "atan(1) != pi/4"
        self.function_dispatcher.dispatch("calc atan(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -0.785 == float(data[0][0][:6]), "atan(-1) != -pi/4"
        self.function_dispatcher.dispatch("calc atan(1000000)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.5707 == float(data[0][0][:6]), "atan(1000000) != pi/2"

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
        assert "error" in data[0][0].lower(), "negative root should fail"

    def test_power(self):
        self.function_dispatcher.dispatch("calc 2^2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 4 == float(data[0][0]), "2^2 != 4"
        self.function_dispatcher.dispatch("calc 2**2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 4 == float(data[0][0]), "** should work alongside ^"
        self.function_dispatcher.dispatch("calc 2^-1", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0.5 == float(data[0][0]), "2^-1 != 1/2"
        self.function_dispatcher.dispatch("calc 2^0.5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.414 == float(data[0][0][:5]), "2^0.5 != 1.414"
        self.function_dispatcher.dispatch("calc 2^0", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "2^0 != 1"

    def test_hyperbolics(self):
        # Cosh
        self.function_dispatcher.dispatch("calc cosh(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "cosh(0) != 1"
        self.function_dispatcher.dispatch("calc cosh(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.543 == float(data[0][0][:5]), "cosh(1) != 1.543"
        self.function_dispatcher.dispatch("calc cosh(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.543 == float(data[0][0][:5]), "cosh(-1) != 1.543"
        # Sinh
        self.function_dispatcher.dispatch("calc sinh(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "sinh(0) != 0"
        self.function_dispatcher.dispatch("calc sinh(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1.175 == float(data[0][0][:5]), "sinh(1) != 1.175"
        self.function_dispatcher.dispatch("calc sinh(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -1.175 == float(data[0][0][:6]), "sinh(-1) != -1.175"
        # Tanh
        self.function_dispatcher.dispatch("calc tanh(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "tanh(0) != 0"
        self.function_dispatcher.dispatch("calc tanh(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0.761 == float(data[0][0][:5]), "tanh(1) != 0.761"
        self.function_dispatcher.dispatch("calc tanh(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -0.761 == float(data[0][0][:6]), "tanh(-1) != -0.761"
        self.function_dispatcher.dispatch("calc tanh(1000000)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "tanh(1000000) != 1"
        # Acosh
        self.function_dispatcher.dispatch("calc acosh(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "acosh(0) should fail"
        self.function_dispatcher.dispatch("calc acosh(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "acosh(1) != 0"
        self.function_dispatcher.dispatch("calc acosh(4)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 2.063 == float(data[0][0][:5]), "acosh(4) != 2.063"
        # Asinh
        self.function_dispatcher.dispatch("calc asinh(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "asinh(0) != 0"
        self.function_dispatcher.dispatch("calc asinh(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0.881 == float(data[0][0][:5]), "asinh(1) != 0.881"
        self.function_dispatcher.dispatch("calc asinh(-1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -0.881 == float(data[0][0][:6]), "asinh(-1) != -0.881"
        # Atanh
        self.function_dispatcher.dispatch("calc atanh(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0 == float(data[0][0]), "atanh(0) != 0"
        self.function_dispatcher.dispatch("calc atanh(0.5)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 0.549 == float(data[0][0][:5]), "atanh(0.5) != 0.549"
        self.function_dispatcher.dispatch("calc atanh(-0.5)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert -0.549 == float(data[0][0][:6]), "atanh(-0.5) != -0.549"
        self.function_dispatcher.dispatch("calc atanh(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "atanh(1) should fail"
        self.function_dispatcher.dispatch("calc atanh(2)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "atanh(2) should fail"

    def test_gamma(self):
        self.function_dispatcher.dispatch("calc gamma(1)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 1 == float(data[0][0]), "gamma(1) != 1"
        self.function_dispatcher.dispatch("calc gamma(5)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert 24 == float(data[0][0]), "gamma(5) != 24"
        self.function_dispatcher.dispatch("calc gamma(0)", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0], "gamma(0) should fail"

    def test_passive(self):
        assert False, "Not yet implemented"