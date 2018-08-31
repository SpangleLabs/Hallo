import unittest

from Events import EventMessage
from test.TestBase import TestBase


class CorbynTest(TestBase, unittest.TestCase):

    def test_corbyn_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" not in data[0].text.lower(), "Corbyn function is returning error."
        assert "CHAIRMAN CORBYN!" in data[0].text, "Corbyn function does not declare imperator trump."

    def test_corbyn_num(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn 7"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text.count("Corbyn") == 7, "Corbyn numerical input not working."

    def test_corbyn_max(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn 10"))
        data10 = self.server.get_send_data(1, self.test_user, EventMessage)
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn 20"))
        data20 = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data10[0].text == data20[0].text, "Corbyn function max limit is not working."

    def test_corbyn_str(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "corbyn woo!"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" not in data[0].text.lower(), "Corbyn function is not working when given invalid number."
