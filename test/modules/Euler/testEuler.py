import unittest

from Server import Server
from test.TestBase import TestBase


class EulerTest(TestBase, unittest.TestCase):

    def test_euler_list(self):
        self.function_dispatcher.dispatch("euler", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Euler function should not throw errors."
        self.function_dispatcher.dispatch("euler list", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Euler function should not throw errors."

    def test_euler_1(self):
        prob_num = "1"
        prob_ans = "233168"
        self.function_dispatcher.dispatch("euler "+prob_num, self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Euler problem "+prob_num+" throws an error."
        assert "Euler project problem "+prob_num+"?" in data[0][0], "Problem name is not in output for " \
                                                                    "problem "+prob_num
        assert prob_ans in data[0][0].lower(), "Euler problem "+prob_num+" has incorrect answer. It should return " + \
                                               prob_ans+" but it returns: "+data[0][0]
