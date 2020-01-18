from events import EventMessage
from function import Function
from function_dispatcher import FunctionDispatcher
from hallo import Hallo
from modules.hallo_control import Help
from test.server_mock import ServerMock


def test_help_all(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "help"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "list of available functions:" in data[0].text.lower()
    num_funcs = len(data[0].text.lower().replace("list of available functions: ", "").split(","))
    assert num_funcs > 4, "Not enough functions listed."


def test_help_mock_func_disp():
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


def test_help_func(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "help help"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" not in data[0].text.lower()
    assert "documentation for \"help\":" in data[0].text.lower()


def test_help_no_func(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "help not a real function"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" in data[0].text.lower()
    assert "no function by that name exists" in data[0].text.lower()


def test_help_no_doc(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    # Manually add FunctionMock to function dispatcher
    hallo.function_dispatcher.load_function(FunctionMockNoDoc)
    try:
        hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "help function no doc"))
        data = test_server.get_send_data(1, test_user, EventMessage)
        assert "error" in data[0].text.lower()
        assert "no documentation exists" in data[0].text.lower()
    finally:
        hallo.function_dispatcher.unload_function(FunctionMockNoDoc)


def test_help_mock_func(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    # Manually add FunctionMock to function dispatcher
    hallo.function_dispatcher.load_function(FunctionMock)
    try:
        hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "help function mock"))
        data = test_server.get_send_data(1, test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "example help, please ignore" in data[0].text.lower()
    finally:
        hallo.function_dispatcher.unload_function(FunctionMock)


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
