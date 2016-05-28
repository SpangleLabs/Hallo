import unittest

from Server import Server
from test.TestBase import TestBase


class HelpTest(TestBase, unittest.TestCase):

    def test_help_all(self):
        self.function_dispatcher.dispatch("help", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "list of available functions:" in data[0][0].lower()
        num_funcs = len(data[0][0].lower().replace("list of available functions: ", "").split(","))
        assert num_funcs > 4, "Not enough functions listed."

    def test_help_mock_func_disp(self):
        pass

    def test_help_func(self):
        pass

    def test_help_mock_func(self):
        pass
