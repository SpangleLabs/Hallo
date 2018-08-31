import unittest

from Events import EventMessage
from test.TestBase import TestBase


class SimplifyFractionTest(TestBase, unittest.TestCase):

    def test_fraction_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 6/4"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "3/2." in data[0].text[-4:], "Simplify fraction fails for small fractions."

    def test_fraction_complex(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 360679/22"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "32789/2." in data[0].text[-8:], "Simplify fraction fails for large fractions."

    def test_fraction_multi_slash(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 360679/22/2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Simplify fraction should return error when given more than 1 slash."

    def test_fraction_integer(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 22/2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert " 11." == data[0].text[-4:], "Simplify fraction should return integer when result is integer."

    def test_fraction_one_arg(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 104779"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Simplify fraction should return error when not given a fraction."

    def test_fraction_unsimplify(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 17/3"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "17/3." == data[0].text[-5:], "Simplify fraction should return original " \
                                             "fraction if it cannot be simplified."

    def test_factors_float(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 17.5/2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Simplify fraction should return error when given a float."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 17/2.2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Simplify fraction should return error when given a float."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 6.6/2.2"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Simplify fraction should return error when given a float."

    def test_factors_negative(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 24/-10"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert " -12/5." in data[0].text[-7:], "Simplify fraction not working for negative denominators."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction -24/10"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert " -12/5." in data[0].text[-7:], "Simplify fraction not working for negative numerators."
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "fraction 24/10"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert " 12/5." in data[0].text[-6:], "Simplify fraction not working for negative numerators & denominators."

    def test_factors_word(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "factors hello/7"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Simplify fraction should return error when invalid number used."
