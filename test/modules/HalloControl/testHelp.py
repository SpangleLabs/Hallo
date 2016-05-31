import unittest

from Function import Function
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
        self.function_dispatcher.dispatch("help help", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "documentation for \"help\":" in data[0][0].lower()

    def test_help_no_func(self):
        self.function_dispatcher.dispatch("help not a real function", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert "no function by that name exists" in data[0][0].lower()

    def test_help_no_doc(self):
        pass

    def test_help_mock_func(self):
        raise NotImplementedError
        # Manually add FunctionMock to function dispatcher
        self.function_dispatcher.reload_module(".test.modules.HalloControl.testHelp")
        self.function_dispatcher.dispatch("help function mock", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        print(data)
        assert "error" not in data[0][0].lower()
        assert "example help, please ignore" in data[0][0].lower()


class FunctionMock(Function):

    def __init__(self):
        super().__init__()
        self.help_name = "function mock"
        self.names = {"function mock", "mock function"}
        self.help_docs = "Example help, please ignore"

    def run(self, line, user_obj, destination_obj):
        pass
