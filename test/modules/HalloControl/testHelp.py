import unittest

from Function import Function
from FunctionDispatcher import FunctionDispatcher
from Hallo import Hallo
from Server import Server
from modules.HalloControl import Help
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class HelpTest(TestBase, unittest.TestCase):

    def test_help_all(self):
        self.function_dispatcher.dispatch("help", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "list of available functions:" in data[0][0].lower()
        num_funcs = len(data[0][0].lower().replace("list of available functions: ", "").split(","))
        assert num_funcs > 4, "Not enough functions listed."

    def test_help_mock_func_disp(self):
        mock_hallo = Hallo()
        mock_func_disp = FunctionDispatcher({}, mock_hallo)
        mock_hallo.function_dispatcher = mock_func_disp
        mock_func_disp.load_function(FunctionMock)
        mock_func_disp.load_function(FunctionMockNoDoc)
        mock_func_disp.load_function(Help)
        mock_server = ServerMock(mock_hallo)
        mock_server.name = "test_serv1"
        mock_user = mock_server.get_user_by_name("test_user1")
        mock_func_disp.dispatch("help", mock_user, mock_user)
        data = mock_server.get_send_data(1, mock_user, Server.MSG_MSG)
        assert "error" not in data[0][0].lower()
        assert "list of available functions:" in data[0][0].lower()
        assert "function mock" in data[0][0].lower()
        assert "function no doc" in data[0][0].lower()

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
        # Manually add FunctionMock to function dispatcher
        self.function_dispatcher.load_function(FunctionMockNoDoc)
        try:
            self.function_dispatcher.dispatch("help function no doc", self.test_user, self.test_user)
            data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
            print(data)
            assert "error" in data[0][0].lower()
            assert "no documentation exists" in data[0][0].lower()
        finally:
            self.function_dispatcher.unload_function(FunctionMockNoDoc)

    def test_help_mock_func(self):
        # Manually add FunctionMock to function dispatcher
        self.function_dispatcher.load_function(FunctionMock)
        try:
            self.function_dispatcher.dispatch("help function mock", self.test_user, self.test_user)
            data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
            assert "error" not in data[0][0].lower()
            assert "example help, please ignore" in data[0][0].lower()
        finally:
            self.function_dispatcher.unload_function(FunctionMock)


class FunctionMock(Function):

    def __init__(self):
        super().__init__()
        self.help_name = "function mock"
        self.names = {"function mock", "mock function"}
        self.help_docs = "Example help, please ignore"

    def run(self, line, user_obj, destination_obj):
        pass


class FunctionMockNoDoc(Function):

    def __init__(self):
        super().__init__()
        self.help_name = "function no doc"
        self.names = {self.help_name}
        self.help_docs = None

    def run(self, line, user_obj, destination_obj):
        pass
