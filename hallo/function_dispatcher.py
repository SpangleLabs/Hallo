import importlib
import logging
import os
import re
import sys
import inspect
from types import ModuleType
from typing import Set, Type, Dict, Optional, List, TypeVar

from hallo.destination import User, Channel
from hallo.errors import (
    FunctionError,
    PassiveFunctionError,
    FunctionNotFoundError,
    FunctionNotAllowedError,
    FunctionSaveError,
)
from hallo.events import (
    ServerEvent,
    UserEvent,
    ChannelEvent,
    EventMessage,
    ChannelUserTextEvent, Event,
)
from hallo.function import Function
from hallo.server import Server

logger = logging.getLogger(__name__)
FuncT = TypeVar("FuncT", bound=Function)


def module_name_to_file_name(full_module_name: str) -> str:
    return full_module_name.replace(".", "/") + ".py"


class FunctionDispatcher(object):
    """
    FunctionDispatcher is a class to manage functions and to send function requests to the relevant function.
    """
    MODULE_DIR = "hallo/modules"

    def __init__(self, module_list: Set[str], hallo):
        """
        Constructor
        :type module_list: set[str]
        :type hallo: hallo.Hallo
        """
        self.hallo = hallo  # Hallo object which owns this
        self.module_list: Set[str] = module_list  # List of available module names
        self.function_dict = (
            {}
        )  # Dictionary of moduleObjects->functionClasses->namesList/eventsList
        self.function_names: Dict[str, Type[Function]] = {}  # Dictionary of names -> functionClasses
        self.persistent_functions: Dict[Type[Function], Function] = (
            {}
        )  # Dictionary of persistent function objects. functionClass->functionObject
        self.event_functions: Dict[Type[Event], Set[Type[Function]]] = (
            {}
        )  # Dictionary with events classes as keys and sets of function classes
        #  (which may want to act on those events) as values
        # Load all functions
        for module_name in self.module_list:
            self.reload_module(module_name)

    def dispatch(self, event: EventMessage, flag_list: List[str] = None) -> None:
        """
        Sends the function call out to whichever function, if one is found
        :param event: The message event which has triggered the function dispatch
        :param flag_list: List of flags to apply to function call
        """
        if flag_list is None:
            flag_list = []
        # Find the function name. Try joining each amount of words in the message until you find a valid function name
        function_message_split = event.command_text.split()
        if not function_message_split:
            function_message_split = [""]
        function_class_test = None
        function_name_test = ""
        function_args_test = ""
        for function_name_test in [
            " ".join(function_message_split[: x + 1])
            for x in range(len(function_message_split))[::-1]
        ]:
            function_class_test = self.get_function_by_name(function_name_test)
            function_args_test = " ".join(function_message_split)[
                len(function_name_test):
            ].strip()
            if function_class_test is not None:
                break
        # If function isn't found, output a not found message
        if function_class_test is None:
            if EventMessage.FLAG_HIDE_ERRORS not in flag_list:
                event.reply(
                    event.create_response("Error, this is not a recognised function.")
                )
                error = FunctionNotFoundError(self, event)
                logger.error(error.get_log_line())
            return
        function_class = function_class_test
        event.split_command_text(function_name_test, function_args_test)
        # Check function rights and permissions
        if not self.check_function_permissions(
            function_class, event.server, event.user, event.channel
        ):
            event.reply(
                event.create_response(
                    "You do not have permission to use this function."
                )
            )
            error = FunctionNotAllowedError(self, function_class, event)
            logger.error(error.get_log_line())
            return
        # If persistent, get the object, otherwise make one
        function_obj = self.get_function_object(function_class)
        # Try running the function, if it fails, return an error message
        try:
            response = function_obj.run(event)
            if response is not None:
                event.reply(response)
            else:
                event.reply(event.create_response("The function returned no value."))
            return
        except Exception as e:
            error = FunctionError(e, self, function_obj, event)
            e_str = (str(e)[:250] + "..") if len(str(e)) > 250 else str(e)
            event.reply(
                event.create_response(
                    "Function failed with error message: {}".format(e_str)
                )
            )
            logger.error(error.get_log_line())
            return

    def dispatch_passive(self, event: Event) -> None:
        """
        Dispatches a event call to passive functions, if any apply
        :param event: Event object which is triggering passive functions
        """
        # If this event is not used, skip this
        if (
            event.__class__ not in self.event_functions
            or len(self.event_functions[event.__class__]) == 0
        ):
            return
        # Get list of functions that want things
        function_list = self.event_functions[event.__class__].copy()
        for function_class in function_list:
            # Check function rights and permissions
            if not self.check_function_permissions(
                function_class,
                event.server if isinstance(event, ServerEvent) else None,
                event.user if isinstance(event, UserEvent) else None,
                event.channel if isinstance(event, ChannelEvent) else None,
            ):
                continue
            # If persistent, get the object, otherwise make one
            function_obj = self.get_function_object(function_class)
            # Try running the function, if it fails, return an error message
            try:
                logger.debug("Calling passive function: %s with event %s", function_obj.__class__.__name__, event)
                response = function_obj.passive_run(event, self.hallo)
                logger.debug("Got passive function response: %s", response)
                if response is not None:
                    if isinstance(response, ChannelUserTextEvent) and isinstance(
                        event, ChannelUserTextEvent
                    ):
                        event.reply(response)
                    else:
                        event.server.send(response)
                continue
            except Exception as e:
                error = PassiveFunctionError(e, self, function_obj, event)
                logger.error(error.get_log_line())
                continue

    def get_function_by_name(self, function_name: str) -> Optional[Type[Function]]:
        """
        Find a functionClass by a name specified by a user. Not functionClass.__name__
        :param function_name: Name of the function to search for
        """
        # Convert name to lower case
        function_name = function_name.lower()
        if function_name in self.function_names:
            return self.function_names[function_name]
        # Check without underscores. People might still use underscores to separate words in a function name
        function_name = function_name.replace("_", " ")
        if function_name in self.function_names:
            return self.function_names[function_name]
        return None

    def get_function_class_list(self) -> List[Type[Function]]:
        """Returns a simple flat list of all function classes."""
        function_class_list = []
        for module_object in self.function_dict:
            function_class_list += list(self.function_dict[module_object])
        return function_class_list

    def get_function_object(self, function_class: Type[FuncT]) -> FuncT:
        """
        If persistent, gets an object from dictionary. Otherwise creates a new object.
        :param function_class: Class of function to retrieve or create function object for
        """
        if function_class.is_persistent():
            function_obj = self.persistent_functions[function_class]
        else:
            function_obj = function_class()
        return function_obj

    def check_function_permissions(
        self, function_class: Type[Function], server_obj: Server, user_obj: User, channel_obj: Optional[Channel]
    ) -> bool:
        """Checks if a function can be called. Returns boolean, True if allowed
        :param function_class: Class of function to check permissions for
        :param server_obj: Server on which to check function permissions
        :param user_obj: User which has requested the function
        :param channel_obj: Channel on which the function was requested
        """
        # Get function name
        function_name = function_class.__name__
        right_name = "function_{}".format(function_name)
        # Check rights
        if user_obj is not None:
            return user_obj.rights_check(right_name, channel_obj)
        if channel_obj is not None:
            return channel_obj.rights_check(right_name)
        if server_obj is not None:
            return server_obj.rights_check(right_name)
        return self.hallo.rights_check(right_name)

    def reload_module(self, module_name: str) -> bool:
        """
        Reloads a function module, or loads it if it is not already loaded. Returns True on success, False on failure
        :param module_name: Name of the module to reload
        """
        # Check it's an allowed module
        if module_name not in self.module_list:
            logger.warning(
                "Module name, {}, is not in allowed list: {}.".format(
                    module_name, ", ".join(self.module_list)
                )
            )
            return False
        # Get the full module names
        full_module_names = self.full_module_names_for_module(module_name)
        if not full_module_names:
            logger.error("Specified module to reload does not exist: %s", module_name)
            return False
        success = True
        for full_module_name in full_module_names:
            success = success and self.reload_python_module(full_module_name)
        return success

    def list_modules_in_package(self, package_name: str) -> List[str]:
        return [
            x[:-3] for x in os.listdir(f"{self.MODULE_DIR}/{package_name}")
            if x.endswith(".py") and not x.startswith("__")
        ]

    def reload_python_module(self, full_module_name: str) -> bool:
        # Check if module has already been imported
        if full_module_name in sys.modules:
            module_obj = sys.modules[full_module_name]
            module_obj = importlib.reload(module_obj)
        else:
            # Try and load new module, return False if it doesn't exist
            try:
                module_obj = importlib.import_module(full_module_name)
            except ImportError:
                logger.warning(
                    "Could not import module: {}".format(full_module_name)
                )
                return False
        # Unload module, if it was loaded.
        self.unload_module_functions(module_obj)
        # Loop through module, searching for Function subclasses.
        for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
            # Get class from tuple
            function_class = function_tuple[1]
            # Ensure it is a member of this module
            if not function_class.__module__.startswith(full_module_name):
                continue
            # Check it's a valid function object
            if not self.check_function_class(function_class):
                continue
            # Try and load function, if it fails, try and unload it.
            try:
                self.load_function(module_obj, function_class)
            except NotImplementedError as e:
                logger.warning("Failed to load function %s. ", function_class, exc_info=e)
                self.unload_function(module_obj, function_class)
        return True

    def unload_module_functions(self, module_obj) -> None:
        """
        Unloads a module, unloading all the functions it contains
        :param module_obj: Module to unload
        """
        # If module isn't in mFunctionDict, cancel
        if module_obj not in self.function_dict:
            return
        function_list = list(self.function_dict[module_obj])
        for function_class in function_list:
            self.unload_function(module_obj, function_class)
        del self.function_dict[module_obj]

    @staticmethod
    def check_function_class(function_class: Type[Function]) -> bool:
        """
        Checks a potential class to see if it is a valid Function subclass class
        :param function_class: Class of the function to check for ability to load
        """
        # Make sure it's not the Function class
        if function_class == Function:
            return False
        # Make sure it is a subclass of Function
        if not issubclass(function_class, Function):
            return False
        # Create function object
        function_obj = function_class()
        # Check that help name is defined
        try:
            help_name = function_obj.get_help_name()
        except NotImplementedError:
            return False
        # Check that help docs are defined
        try:
            function_obj.get_help_docs()
        except NotImplementedError:
            return False
        # Check that names list is not empty
        try:
            names_list = function_obj.get_names()
            if names_list is None:
                return False
            if len(names_list) == 0:
                return False
            # Check that names list contains help name
            if help_name not in names_list:
                return False
        except NotImplementedError:
            return False
        # If it passed all those tests, it's valid, probably
        return True

    def load_function(self, module_obj: ModuleType, function_class: Type[Function]) -> None:
        """
        Loads a function class into all the relevant dictionaries
        :param module_obj: The module of the function
        :param function_class: Class of the function to load into dispatcher
        """
        # If function is persistent, load it up and add to mPersistentFunctions
        if function_class.is_persistent():
            function_obj = function_class.load_function()
            self.persistent_functions[function_class] = function_obj
        else:
            function_obj = function_class()
        # Get names list and events list
        names_list = function_obj.get_names()
        events_list = function_obj.get_passive_events()
        # Add names list and events list to mFunctionDict
        if module_obj not in self.function_dict:
            self.function_dict[module_obj] = {}
        self.function_dict[module_obj][function_class] = {}
        self.function_dict[module_obj][function_class]["names"] = names_list
        self.function_dict[module_obj][function_class]["events"] = events_list
        # Add function to mFunctionNames
        for function_name in names_list:
            if function_name in self.function_names:
                raise NotImplementedError(
                    'This function name "{}", in "{}" function class is already taken by '
                    'the "{}" function class.'.format(
                        function_name,
                        function_class.__name__,
                        self.function_names[function_name].__name__,
                    )
                )
            self.function_names[function_name] = function_class
        # Add function to mEventFunctions
        for function_event in events_list:
            if function_event not in self.event_functions:
                self.event_functions[function_event] = set()
            self.event_functions[function_event].add(function_class)

    def unload_function(self, module_obj: ModuleType, function_class: Type[Function]) -> None:
        """
        Unloads a function class from all the relevant dictionaries
        :param module_obj: The module that the function belongs to
        :param function_class: Class of the function which is being unloaded
        """
        # Check that function is loaded
        if module_obj not in self.function_dict:
            return
        if function_class not in self.function_dict[module_obj]:
            return
        # Get list of function names and list of events functions respond to
        names_list = self.function_dict[module_obj][function_class]["names"]
        events_list = self.function_dict[module_obj][function_class]["events"]
        # Remove names from mFunctionNames
        for function_name in names_list:
            del self.function_names[function_name]
        # Remove events from mEventFunctions
        for function_event in events_list:
            if function_event not in self.event_functions:
                continue
            if function_class not in self.event_functions[function_event]:
                continue
            self.event_functions[function_event].remove(function_class)
        # If persistent, save object and remove from mPersistentFunctions
        if function_class.is_persistent():
            function_obj = self.persistent_functions[function_class]
            try:
                function_obj.save_function()
            except Exception as e:
                error = FunctionSaveError(e, function_obj)
                logger.error(error.get_log_line())
            del self.persistent_functions[function_class]
        # Remove from mFunctionDict
        del self.function_dict[module_obj][function_class]

    def list_cross_module_imports(self, module_name: str) -> List[str]:
        full_module_names = self.full_module_names_for_module(module_name)
        cross_module_import = re.compile(f"import hallo\.modules\.([^.\s]+)")
        other_modules = set()
        for full_module_name in full_module_names:
            file_name = module_name_to_file_name(full_module_name)
            with open(file_name, "r") as f:
                file_contents = f.read()
            for match in cross_module_import.findall(file_contents, re.MULTILINE):
                other_modules.add(match)
        return list(other_modules)

    def full_module_names_for_module(self, module_name: str) -> List[str]:
        if os.path.isfile(f"{self.MODULE_DIR}/{module_name}.py"):
            # It's a python module
            logger.debug("Reloading module")
            return [f"hallo.modules.{module_name}"]
        if os.path.isdir(f"{self.MODULE_DIR}/{module_name}/"):
            # It's a python package
            logger.debug("Reloading package")
            modules = self.list_modules_in_package(module_name)
            if not modules:
                logger.error("Specified package to reload, %s, is empty", module_name)
            return [f"hallo.modules.{module_name}.{module}" for module in modules]
        return []

    def close(self) -> None:
        """Shut down FunctionDispatcher, save all functions, etc"""
        for module_object in list(self.function_dict):
            self.unload_module_functions(module_object)

    def to_json(self) -> Dict:
        """
        Output the function dispatcher configuration in a dict format for saving as json
        """
        json_obj = dict()
        json_obj["modules"] = []
        for module_name in self.module_list:
            json_obj["modules"].append({"name": module_name})
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo) -> 'FunctionDispatcher':
        """
        Creates a function dispatcher from json object dict
        """
        module_list = set()
        for module in json_obj["modules"]:
            module_list.add(module["name"])
        new_dispatcher = FunctionDispatcher(module_list, hallo)
        return new_dispatcher
