import importlib
import inspect
import pkgutil

import pytest

from hallo import modules
from hallo.function import Function


def list_modules():
    return [
        "hallo.modules." + modname
        for _, modname, is_pkg in pkgutil.iter_modules(modules.__path__)
        if not is_pkg
    ]


def list_functions_in_module(module_obj, module_name):
    funcs = []
    for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
        # Get class from tuple
        function_class = function_tuple[1]
        # Ensure it is a member of this module
        if function_class.__module__ != module_name:
            continue
        # Make sure it's not the Function class
        if function_class == Function:
            continue
        # Make sure it is a subclass of Function
        if not issubclass(function_class, Function):
            continue
        funcs.append(function_class)
    return funcs


@pytest.mark.parametrize("mod", list_modules())
def test_each_modules_import(mod):
    importlib.import_module(mod)


def test_no_function_name_collisions():
    func_names = []
    for module_name in list_modules():
        module_obj = importlib.import_module(module_name)
        funcs = list_functions_in_module(module_obj, module_name)
        for function_class in funcs:
            func_obj = function_class()
            for name in func_obj.get_names():
                assert name not in func_names
                func_names.append(name)
