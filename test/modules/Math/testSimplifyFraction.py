import unittest

from Server import Server
from test.TestBase import TestBase


class SimplifyFractionTest(TestBase, unittest.TestCase):

    def test_fraction_simple(self):
        self.function_dispatcher.dispatch("fraction 6/4", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "3/2." in data[0][0][-4:], "Simplify fraction fails for small fractions."

    def test_fraction_complex(self):
        self.function_dispatcher.dispatch("fraction 360679/22", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "32789/2." in data[0][0][-8:], "Simplify fraction fails for large fractions."

    def test_fraction_multi_slash(self):
        self.function_dispatcher.dispatch("fraction 360679/22/2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Simplify fraction should return error when given more than 1 slash."

    def test_fraction_integer(self):
        self.function_dispatcher.dispatch("fraction 22/2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert " 11." == data[0][0][-4:], "Simplify fraction should return integer when result is integer."

    def test_fraction_one_arg(self):
        self.function_dispatcher.dispatch("fraction 104779", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Simplify fraction should return error when not given a fraction."

    def test_fraction_unsimplify(self):
        self.function_dispatcher.dispatch("fraction 17/3", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "17/3." == data[0][0][-5:], "Simplify fraction should return original " \
                                           "fraction if it cannot be simplified."

    def test_factors_float(self):
        self.function_dispatcher.dispatch("fraction 17.5/2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Simplify fraction should return error when given a float."
        self.function_dispatcher.dispatch("fraction 17/2.2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Simplify fraction should return error when given a float."
        self.function_dispatcher.dispatch("fraction 6.6/2.2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Simplify fraction should return error when given a float."

    def test_factors_negative(self):
        self.function_dispatcher.dispatch("fraction 24/-10", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        print(data)
        assert " -12/5." in data[0][0][-7:], "Simplify fraction not working for negative denominators."
        self.function_dispatcher.dispatch("fraction -24/10", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        print(data)
        assert " -12/5." in data[0][0][-7:], "Simplify fraction not working for negative numerators."
        self.function_dispatcher.dispatch("fraction 24/10", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        print(data)
        assert " 12/5." in data[0][0][-6:], "Simplify fraction not working for negative numerators & denominators."

    def test_factors_word(self):
        self.function_dispatcher.dispatch("factors hello/7", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Simplify fraction should return error when invalid number used."
