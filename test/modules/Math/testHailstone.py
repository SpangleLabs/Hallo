import unittest

from Server import Server
from modules.Math import Hailstone
from test.TestBase import TestBase


class HailstoneTest(TestBase, unittest.TestCase):

    def test_hailstone_simple(self):
        self.function_dispatcher.dispatch("hailstone 5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "5->16->8->4->2->1" in data[0][0], "Hailstone function not returning correctly."

    def test_hailstone_over_limit(self):
        self.function_dispatcher.dispatch("hailstone "+str(Hailstone.LIMIT+1), self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Hailstone size limit has not been enforced."

    def test_hailstone_negative(self):
        self.function_dispatcher.dispatch("hailstone -5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        print(data[0][0])
        assert "error" in data[0][0].lower(), "Hailstone should fail with negative input."

    def test_hailstone_float(self):
        self.function_dispatcher.dispatch("hailstone 2.3", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Hailstone should fail with non-integer input."
