import unittest

from Events import EventMessage
from Function import Function
from FunctionDispatcher import FunctionDispatcher
from Hallo import Hallo
from modules.HalloControl import Help
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class HelpTest(TestBase, unittest.TestCase):

    def test_help_all(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "help"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "list of available functions:" in data[0].text.lower()
        num_funcs = len(data[0].text.lower().replace("list of available functions: ", "").split(","))
        assert num_funcs > 4, "Not enough functions listed."

    def test_help_mock_func_disp(self):
        # Set up mock objects
        mock_hallo = Hallo()
        mock_func_disp = FunctionDispatcher(set(), mock_hallo)
        mock_hallo.function_dispatcher = mock_func_disp
        mock_func_disp.load_function(FunctionMock)
        mock_func_disp.load_function(FunctionMockNoDoc)
        mock_func_disp.load_function(Help)
        mock_server = ServerMock(mock_hallo)
        mock_server.name = "test_serv1"
        mock_user = mock_server.get_user_by_address("test_user1".lower(), "test_user1")
        # Test things
        mock_func_disp.dispatch(EventMessage(mock_server, None, mock_user, "help"))
        data = mock_server.get_send_data(1, mock_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "list of available functions:" in data[0].text.lower()
        assert "function mock" in data[0].text.lower()
        assert "function no doc" in data[0].text.lower()

    def test_help_func(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "help help"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "documentation for \"help\":" in data[0].text.lower()

    def test_help_no_func(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "help not a real function"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower()
        assert "no function by that name exists" in data[0].text.lower()

    def test_help_no_doc(self):
        # Manually add FunctionMock to function dispatcher
        self.function_dispatcher.load_function(FunctionMockNoDoc)
        try:
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "help function no doc"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            print(data)
            assert "error" in data[0].text.lower()
            assert "no documentation exists" in data[0].text.lower()
        finally:
            self.function_dispatcher.unload_function(FunctionMockNoDoc)

    def test_help_mock_func(self):
        # Manually add FunctionMock to function dispatcher
        self.function_dispatcher.load_function(FunctionMock)
        try:
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "help function mock"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "error" not in data[0].text.lower()
            assert "example help, please ignore" in data[0].text.lower()
        finally:
            self.function_dispatcher.unload_function(FunctionMock)


class FunctionMock(Function):

    def __init__(self):
        super().__init__()
        self.help_name = "function mock"
        self.names = {"function mock", "mock function"}
        self.help_docs = "Example help, please ignore"

    def run(self, event):
        pass


class FunctionMockNoDoc(Function):

    def __init__(self):
        super().__init__()
        self.help_name = "function no doc"
        self.names = {self.help_name}
        self.help_docs = None

    def run(self, event):
        pass
