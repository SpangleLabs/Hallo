from hallo.events import EventMessage
from hallo.function import Function
from hallo.function_dispatcher import FunctionDispatcher
from hallo.hallo import Hallo
from hallo.modules.hallo_control import Help
from hallo.test.server_mock import ServerMock


def test_help_all(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "help")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "list of available functions:" in data[0].text.lower()
    num_funcs = len(
        data[0].text.lower().replace("list of available functions: ", "").split(",")
    )
    assert num_funcs > 4, "Not enough functions listed."


def test_help_mock_func_disp():
    # Set up mock objects
    mock_hallo = Hallo()
    mock_func_disp = FunctionDispatcher(set(), mock_hallo)
    mock_hallo.function_dispatcher = mock_func_disp
    mock_func_disp.load_function(None, FunctionMock)
    mock_func_disp.load_function(None, FunctionMockNoDoc)
    mock_func_disp.load_function(None, Help)
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
    test_hallo = hallo_getter({"hallo_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "help help")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" not in data[0].text.lower()
    assert 'documentation for "help":' in data[0].text.lower()


def test_help_no_func(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "help not a real function")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower()
    assert "no function by that name exists" in data[0].text.lower()


def test_help_no_doc(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    # Manually add FunctionMock to function dispatcher
    test_hallo.function_dispatcher.load_function(None, FunctionMockNoDoc)
    try:
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "help function no doc")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "error" in data[0].text.lower()
        assert "no documentation exists" in data[0].text.lower()
    finally:
        test_hallo.function_dispatcher.unload_function(None, FunctionMockNoDoc)


def test_help_mock_func(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    # Manually add FunctionMock to function dispatcher
    test_hallo.function_dispatcher.load_function(None, FunctionMock)
    try:
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "help function mock")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "example help, please ignore" in data[0].text.lower()
    finally:
        test_hallo.function_dispatcher.unload_function(None, FunctionMock)


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
