import unittest

from Server import Server
from test.TestBase import TestBase


class CorbynTest(TestBase, unittest.TestCase):

    def test_trump_simple(self):
        self.function_dispatcher.dispatch("corbyn", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Corbyn function is returning error."
        assert "CHAIRMAN CORBYN!" in data[0][0], "Corbyn function does not declare imperator trump."

    def test_trump_num(self):
        self.function_dispatcher.dispatch("corbyn 7", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data[0][0].count("Corbyn") == 7, "Corbyn numerical input not working."

    def test_trump_max(self):
        self.function_dispatcher.dispatch("corbyn 10", self.test_user, self.test_user)
        data10 = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        self.function_dispatcher.dispatch("corbyn 20", self.test_user, self.test_user)
        data20 = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert data10[0][0] == data20[0][0], "Corbyn function max limit is not working."

    def test_trump_str(self):
        self.function_dispatcher.dispatch("corbyn woo!", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower(), "Corbyn function is not working when given invalid number."
