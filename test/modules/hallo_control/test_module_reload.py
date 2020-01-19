from events import EventMessage


def test_module_reload(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    old_func_disp = hallo.function_dispatcher
    mock_func_disp = FunctionDispatcherMock()
    mock_func_disp.module_reload_resp = True
    try:
        hallo.function_dispatcher = mock_func_disp
        old_func_disp.dispatch(EventMessage(
            test_server, None, test_user, "module reload hallo_control"
        ))
        data = test_server.get_send_data(1, test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "module reloaded" in data[0].text.lower()
        assert mock_func_disp.module_reloaded
    finally:
        hallo.function_dispatcher = old_func_disp


def test_module_fail(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"hallo_control"})
    old_func_disp = hallo.function_dispatcher
    mock_func_disp = FunctionDispatcherMock()
    mock_func_disp.module_reload_resp = False
    try:
        hallo.function_dispatcher = mock_func_disp
        old_func_disp.dispatch(EventMessage(
            test_server, None, test_user, "module reload hallo_control"
        ))
        data = test_server.get_send_data(1, test_user, EventMessage)
        assert "error" in data[0].text.lower()
        assert "module reloaded" not in data[0].text.lower()
        assert not mock_func_disp.module_reloaded
    finally:
        hallo.function_dispatcher = old_func_disp


class FunctionDispatcherMock:
    module_reloaded = False
    module_reload_resp = True

    def reload_module(self, name):
        self.module_reloaded = self.module_reload_resp
        return self.module_reload_resp
