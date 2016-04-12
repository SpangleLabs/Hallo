import unittest

from Server import Server
from test.TestBase import TestBase


class ChangeOptionsTest(TestBase, unittest.TestCase):

    def test_change_options_simple(self):
        self.function_dispatcher.dispatch("change options 5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "[5]" in data[0][0], "Option missing from results."
        assert "[2,2,1]" in data[0][0], "Option missing from results."
        assert "[2,1,1,1]" in data[0][0], "Option missing from results."
        assert "[1,1,1,1,1]" in data[0][0], "Option missing from results."

    def test_change_options_over_limit(self):
        self.function_dispatcher.dispatch("change options 21", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Change options size limit has not been enforced."

    def test_change_options_negative(self):
        self.function_dispatcher.dispatch("change options -5", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Change options should fail with negative input."

    def test_change_options_float(self):
        self.function_dispatcher.dispatch("change option 2.3", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Change options should fail with non-integer input."
