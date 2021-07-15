from hallo.events import EventMessage


def test_module_reload(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    old_func_disp = test_hallo.function_dispatcher
    mock_func_disp = FunctionDispatcherMock()
    mock_func_disp.module_reload_resp = True
    try:
        test_hallo.function_dispatcher = mock_func_disp
        old_func_disp.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "module reload hallo_control")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "module reloaded" in data[0].text.lower()
        assert mock_func_disp.module_reloaded
    finally:
        test_hallo.function_dispatcher = old_func_disp


def test_module_fail(hallo_getter):
    test_hallo = hallo_getter({"hallo_control"})
    old_func_disp = test_hallo.function_dispatcher
    mock_func_disp = FunctionDispatcherMock()
    mock_func_disp.module_reload_resp = False
    try:
        test_hallo.function_dispatcher = mock_func_disp
        old_func_disp.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "module reload hallo_control")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert "error" in data[0].text.lower()
        assert "module reloaded" not in data[0].text.lower()
        assert not mock_func_disp.module_reloaded
    finally:
        test_hallo.function_dispatcher = old_func_disp


class FunctionDispatcherMock:
    module_reloaded = False
    module_reload_resp = True

    def reload_module(self, *_):
        self.module_reloaded = self.module_reload_resp
        return self.module_reload_resp

    def list_cross_module_imports(self, *_):
        return []
