import unittest

from Server import Server
from test.TestBase import TestBase


class ModuleReloadTest(TestBase, unittest.TestCase):

    def test_module_reload(self):
        old_func_disp = self.hallo.function_dispatcher
        try:
            mock_func_disp = FunctionDispatcherMock()
            self.hallo.function_dispatcher = mock_func_disp
            self.function_dispatcher.dispatch("module reload HalloControl", self.test_user, self.test_user)
            data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
            assert "error" not in data[0][0].lower()
            assert "module reloaded" in data[0][0].lower()
            assert mock_func_disp.module_reloaded
        finally:
            self.hallo.function_dispatcher = old_func_disp

    def test_module_no_name(self):
        pass

    def test_module_case_insensitive(self):
        pass


class FunctionDispatcherMock:
    module_reloaded = False

    def reload_module(self, name):
        self.module_reloaded = True
        return True
