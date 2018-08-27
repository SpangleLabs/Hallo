import unittest

from Events import EventMessage
from Server import Server
from modules.Math import Hailstone
from test.TestBase import TestBase


class HailstoneTest(TestBase, unittest.TestCase):

    def test_hailstone_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hailstone 5"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "5->16->8->4->2->1" in data[0][0], "Hailstone function not returning correctly."

    def test_hailstone_over_limit(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "hailstone "+str(Hailstone.LIMIT+1)))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Hailstone size limit has not been enforced."

    def test_hailstone_negative(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hailstone -5"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Hailstone should fail with negative input."

    def test_hailstone_float(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hailstone 2.3"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Hailstone should fail with non-integer input."
