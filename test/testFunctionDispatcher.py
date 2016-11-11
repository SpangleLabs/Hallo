import unittest

from FunctionDispatcher import FunctionDispatcher
from test.TestBase import TestBase


class FunctionDispatcherTest(TestBase, unittest.TestCase):

    def test_fd_load_order(self):
        # Create a blank function dispatcher
        fd = FunctionDispatcher([], None)
        # Add modules to allowed list
        fd.module_list = ["Euler", "Math"]
        # Load up Euler module, ensure no other modules load.
        fd.reload_module("Euler")
        assert len(fd.function_dict) == 1
        # Load second module, ensure all methods are there.
        fd.reload_module("Math")
        assert len(fd.function_dict) == 2

    def test_fd_disallowed_module(self):
        # Create a blank function dispatcher
        fd = FunctionDispatcher([], None)
        # Try and load a module
        assert not fd.reload_module("Euler")
