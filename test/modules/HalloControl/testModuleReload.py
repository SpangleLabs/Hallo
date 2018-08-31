import unittest

from Events import EventMessage
from test.TestBase import TestBase


class ModuleReloadTest(TestBase, unittest.TestCase):

    def test_module_reload(self):
        old_func_disp = self.hallo.function_dispatcher
        try:
            mock_func_disp = FunctionDispatcherMock()
            mock_func_disp.module_reload_resp = True
            self.hallo.function_dispatcher = mock_func_disp
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                           "module reload HalloControl"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "error" not in data[0].text.lower()
            assert "module reloaded" in data[0].text.lower()
            assert mock_func_disp.module_reloaded
        finally:
            self.hallo.function_dispatcher = old_func_disp

    def test_module_fail(self):
        old_func_disp = self.hallo.function_dispatcher
        try:
            mock_func_disp = FunctionDispatcherMock()
            mock_func_disp.module_reload_resp = False
            self.hallo.function_dispatcher = mock_func_disp
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                          "module reload HalloControl"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "error" in data[0].text.lower()
            assert "module reloaded" not in data[0].text.lower()
            assert not mock_func_disp.module_reloaded
        finally:
            self.hallo.function_dispatcher = old_func_disp


class FunctionDispatcherMock:
    module_reloaded = False
    module_reload_resp = True

    def reload_module(self, name):
        self.module_reloaded = self.module_reload_resp
        return self.module_reload_resp
