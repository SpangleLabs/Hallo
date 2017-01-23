import unittest

from FunctionDispatcher import FunctionDispatcher
from Hallo import Hallo
from test.TestBase import TestBase


class FunctionDispatcherTest(TestBase, unittest.TestCase):

    def test_fd_load_order(self):
        # Create a blank function dispatcher
        fd = FunctionDispatcher(set(), self.hallo)
        try:
            # Add modules to allowed list
            fd.module_list = {"Euler", "Math"}
            # Load up Euler module, ensure no other modules load.
            assert fd.reload_module("Euler")
            assert len(fd.function_dict) == 1
            # Load second module, ensure all methods are there.
            assert fd.reload_module("Math")
            assert len(fd.function_dict) == 2
        finally:
            fd.close()

    def test_fd_disallowed_module(self):
        # Create a blank function dispatcher
        fd = FunctionDispatcher(set(), self.hallo)
        try:
            # Try and load a module
            assert not fd.reload_module("Euler")
        finally:
            fd.close()

    def test_init(self):
        # Create some basic stuff
        test_modules = {"Euler"}
        test_hallo = Hallo()
        # Create function dispatcher
        fd = FunctionDispatcher(test_modules, test_hallo)
        test_hallo.function_dispatcher = fd
        try:
            # Check basic class variable setting
            assert fd.hallo == test_hallo, "Hallo object was not set correctly in FunctionDispatcher."
            assert fd.module_list == test_modules, "Module list was not imported correctly by FunctionDispatcher."
            # Check that module reloading has done things
            assert len(fd.function_dict) == len(test_modules), "Modules were not loaded to function dictionary."
            assert len(fd.function_names) != 0, "Functions were not added to function_names"
        finally:
            fd.close()
            test_hallo.close()

# TODO: write tests for each method:
# dispatch
# dispatch_passive
# get_function_by_name
# get_function_class_list
# get_function_object
# check_function_permissions
# reload_module
# _reload
# unload_module_functions
# check_function_class
# load_function
# unload_function
# close
# to_xml
# from_xml
