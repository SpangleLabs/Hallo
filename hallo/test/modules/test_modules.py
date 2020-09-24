import glob
import importlib
import inspect
import pkgutil
import re

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


def test_no_import_from_modules():
    bad_import_from_pattern = re.compile(r"from hallo\.modules\.")
    module_files = glob.glob("hallo/modules/**/*.py", recursive=True)
    bad_files = []
    for module_file in module_files:
        with open(module_file, "r") as f:
            file_content = f.read()
            if bad_import_from_pattern.search(file_content) is not None:
                bad_files.append(module_file)
    assert not bad_files, \
        f"Module to module imports cannot use \"from\" imports. It breaks module reloading. " \
        f"These modules need fixing: {bad_files}"
