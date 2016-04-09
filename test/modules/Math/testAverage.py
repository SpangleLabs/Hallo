import unittest

from Server import Server
from test.TestBase import TestBase


class CalculateTest(TestBase, unittest.TestCase):

    def test_avg_simple(self):
        self.function_dispatcher.dispatch("average 2 4", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert float(data[0][0].split()[-1][:-1]) == 3, "average of 2 and 4 should be 3"

    def test_avg_same(self):
        self.function_dispatcher.dispatch("average 2 2 2 2 2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert float(data[0][0].split()[-1][:-1]) == 2, "average of the same number should be the same number"

    def test_avg_many(self):
        self.function_dispatcher.dispatch("average 2 7 4 6 32 4 1 17 12 12 100", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0].split()[-1][:-1][:6] == "17.909", "average of many numbers calculated incorrectly"

    def test_avg_floats(self):
        self.function_dispatcher.dispatch("average 2.4 3.2 6.6 1.2", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert round(float(data[0][0].split()[-1][:-1]), 2) == 3.35, "average of floats incorrect"

    def test_avg_negative(self):
        self.function_dispatcher.dispatch("average -5 5 -10 10 -14 -16 13 17", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert float(data[0][0].split()[-1][:-1]) == 0, "average including negatives was incorrect"

    def test_avg_fail(self):
        # Test that words fail
        self.function_dispatcher.dispatch("average -5 5 hello 10 -14 -16 13 17", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "average of words should throw error"
        # Test that invalid numbers fail
        self.function_dispatcher.dispatch("average -5 5 -10 10.0.0 -14 -16 13 17", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Invalid numbers did not return error"
