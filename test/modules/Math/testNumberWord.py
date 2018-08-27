import unittest

from Events import EventMessage
from Server import Server
from test.TestBase import TestBase


class NumberWordTest(TestBase, unittest.TestCase):

    def test_number_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 5"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "five." == data[0][0], "Number word failing for small numbers."

    def test_number_big(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 295228"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "two hundred and ninety-five thousand, two hundred and twenty-eight." == data[0][0].lower(),\
            "Number word failing for large numbers."

    def test_number_teen(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 17"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "seventeen." == data[0][0].lower(), "Number word failing for 'teen' numbers."

    def test_number_negative(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number -502"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "negative five hundred and two." == data[0][0].lower(), "Number word failing for negative numbers."

    def test_number_float(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 2.3"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "two point three" in data[0][0].lower(), "Number word failing for non-integers."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 2.357"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "two point three five seven." == data[0][0].lower(), "Number word failing for non-integers."

    def test_number_american(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 1000000000 american"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "one billion." == data[0][0].lower(), "Number word failing for american formatting."

    def test_number_british(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 1000000000 british"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "one thousand million." == data[0][0].lower(), "Number word failing for british formatting."

    def test_number_european(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 1000000000 european"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "one milliard." == data[0][0].lower(), "Number word failing for european formatting."

    def test_number_calculation(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number 17*5"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "eighty-five." == data[0][0].lower(), "Number word failing for calculations."

    def test_number_fail(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "number seventeen"))
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Number word not outputting error for non-numeric input."
