import unittest

from Events import EventMessage
from Server import Server
from modules.Math import Hailstone
from test.TestBase import TestBase


class HighestCommonFactorTest(TestBase, unittest.TestCase):

    def test_hcf_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf 5 13"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "1" == data[0].text[:-1][-1:], "Highest common factor function not returning correctly."

    def test_hcf_big(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf 295228 285349"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "1" == data[0].text[-2:-1], "Highest common factor function not returning correctly."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf 295228 494644"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "4" == data[0].text[-2:-1], "Highest common factor function not returning correctly."

    def test_hcf_one_arg(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "hcf "+str(Hailstone.LIMIT+1)))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Highest common factor size limit has not been enforced."

    def test_hcf_negative(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf -502 -124"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Highest common factor should fail with negative inputs."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf 502 -124"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Highest common factor should fail with negative input."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf -502 124"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Highest common factor should fail with negative input."

    def test_hcf_float(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "hcf 2.3 13"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Highest common factor should fail with non-integer input."
