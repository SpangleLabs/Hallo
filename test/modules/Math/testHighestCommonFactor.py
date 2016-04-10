import unittest

from Server import Server
from modules.Math import Hailstone
from test.TestBase import TestBase


class HighestCommonFactorTest(TestBase, unittest.TestCase):

    def test_hcf_simple(self):
        self.function_dispatcher.dispatch("hcf 5 13", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "1" == data[0][0][:-1][-1:], "Highest common factor function not returning correctly."

    def test_hcf_big(self):
        self.function_dispatcher.dispatch("hcf 295228 285349", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "1" == data[0][0][-2:-1], "Highest common factor function not returning correctly."
        self.function_dispatcher.dispatch("hcf 295228 494644", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "4" == data[0][0][-2:-1], "Highest common factor function not returning correctly."

    def test_hcf_one_arg(self):
        self.function_dispatcher.dispatch("hcf "+str(Hailstone.LIMIT+1), self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Highest common factor size limit has not been enforced."

    def test_hcf_negative(self):
        self.function_dispatcher.dispatch("hcf -502 -124", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Highest common factor should fail with negative inputs."
        self.function_dispatcher.dispatch("hcf 502 -124", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Highest common factor should fail with negative input."
        self.function_dispatcher.dispatch("hcf -502 124", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Highest common factor should fail with negative input."

    def test_hcf_float(self):
        self.function_dispatcher.dispatch("hcf 2.3 13", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Highest common factor should fail with non-integer input."
