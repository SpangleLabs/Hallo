from function_dispatcher import FunctionDispatcher
from hallo import Hallo


def test_fd_load_order(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({})
    # Create a blank function dispatcher
    fd = FunctionDispatcher(set(), hallo)
    try:
        # Add modules to allowed list
        fd.module_list = {"euler", "math"}
        # Load up Euler module, ensure no other modules load.
        assert fd.reload_module("euler")
        assert len(fd.function_dict) == 1
        # Load second module, ensure all methods are there.
        assert fd.reload_module("math")
        assert len(fd.function_dict) == 2
    finally:
        fd.close()


def test_fd_disallowed_module(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({})
    # Create a blank function dispatcher
    fd = FunctionDispatcher(set(), hallo)
    try:
        # Try and load a module
        assert not fd.reload_module("euler")
    finally:
        fd.close()


def test_init():
    # Create some basic stuff
    test_modules = {"euler"}
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


def test_xml(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({})
    # Set up
    test_modules = {"euler", "bio"}
    fd = FunctionDispatcher(test_modules, hallo)
    # Get xml output
    xml_fd = fd.to_xml()
    # Create new function dispatcher from the xml
    fd2 = FunctionDispatcher.from_xml(xml_fd, hallo)
    # Check it's the same
    assert len(fd.module_list) == len(fd2.module_list)
    for module in fd2.module_list:
        assert module in fd.module_list
    assert fd2.hallo == hallo


def test_open_close(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({})
    # Set up
    test_module = "euler"
    test_modules = {test_module}
    # Create function dispatcher
    fd = FunctionDispatcher(test_modules, hallo)
    try:
        # Check test module is loaded
        assert len(fd.function_dict) == len(test_modules)
        assert len(fd.function_names) > 0
    finally:
        # Close function dispatcher
        fd.close()
    # Check test module unloaded
    assert len(fd.function_dict) == 0
    assert len(fd.function_names) == 0

# TODO: write tests for each method:
# Test init loads function from xml, test close saves it
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
