import importlib
import sys
import inspect
import traceback
from xml.dom import minidom
# noinspection PyDeprecation
import imp

from Events import ServerEvent, UserEvent, ChannelEvent, EventMessage, ChannelUserTextEvent
from Function import Function


class FunctionDispatcher(object):
    """
    FunctionDispatcher is a class to manage functions and to send function requests to the relevant function.
    """

    def __init__(self, module_list, hallo):
        """
        Constructor
        :type module_list: set[str]
        :type hallo: Hallo.Hallo
        """
        self.hallo = hallo  # Hallo object which owns this
        self.module_list = module_list  # List of available module names
        self.function_dict = {}  # Dictionary of moduleObjects->functionClasses->nameslist/eventslist
        self.function_names = {}  # Dictionary of names -> functionClasses
        self.persistent_functions = {}  # Dictionary of persistent function objects. functionClass->functionObject
        self.event_functions = {}  # Dictionary with events classes as keys and sets of function classes
        #  (which may want to act on those events) as values
        # Load all functions
        for module_name in self.module_list:
            self.reload_module(module_name)

    # def dispatch(self, function_message, user_obj, destination_obj, flag_list=None):
    def dispatch(self, event, flag_list=None):
        """
        Sends the function call out to whichever function, if one is found
        :param event: The message event which has triggered the function dispatch
        :type event: Events.EventMessage
        :param flag_list: List of flags to apply to function call
        :type flag_list: list[str]
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
        for function_name_test in [' '.join(function_message_split[:x + 1]) for x in
                                   range(len(function_message_split))[::-1]]:
            function_class_test = self.get_function_by_name(function_name_test)
            function_args_test = ' '.join(function_message_split)[len(function_name_test):].strip()
            if function_class_test is not None:
                break
        # If function isn't found, output a not found message
        if function_class_test is None:
            if EventMessage.FLAG_HIDE_ERRORS not in flag_list:
                event.reply(event.create_response("Error, this is not a recognised function."))
                print("Error, this is not a recognised function.")
            return
        function_class = function_class_test
        event.split_command_text(function_name_test, function_args_test)
        # Check function rights and permissions
        if not self.check_function_permissions(function_class, event.server, event.user, event.channel):
            event.reply(event.create_response("You do not have permission to use this function."))
            print("You do not have permission to use this function.")
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
            e_str = (str(e)[:75] + '..') if len(str(e)) > 75 else str(e)
            event.reply(event.create_response("Function failed with error message: {}".format(e_str)))
            print("Function: {} {}".format(function_class.__module__, function_class.__name__))
            print("Function error: {}".format(e))
            print("Function error location: {}".format(traceback.format_exc()))
            return

    def dispatch_passive(self, event):
        """
        Dispatches a event call to passive functions, if any apply
        :param event: Event object which is triggering passive functions
        :type event: Events.Event
        """
        # If this event is not used, skip this
        if event.__class__ not in self.event_functions or len(self.event_functions[event.__class__]) == 0:
            return
        # Get list of functions that want things
        function_list = self.event_functions[event.__class__]
        for function_class in function_list:
            # Check function rights and permissions
            if not self.check_function_permissions(function_class,
                                                   event.server if isinstance(event, ServerEvent) else None,
                                                   event.user if isinstance(event, UserEvent) else None,
                                                   event.channel if isinstance(event, ChannelEvent) else None):
                continue
            # If persistent, get the object, otherwise make one
            function_obj = self.get_function_object(function_class)
            # Try running the function, if it fails, return an error message
            try:
                response = function_obj.passive_run(event, self.hallo)
                if response is not None:
                    if isinstance(response, ChannelUserTextEvent) and isinstance(event, ChannelUserTextEvent):
                        event.reply(response)
                    else:
                        event.server.send(response)
                continue
            except Exception as e:
                print("ERROR Passive Function: {} {}".format(function_class.__module__, function_class.__name__))
                print("ERROR Function event: {}".format(event))
                print("ERROR Function error: {}".format(e))
                print("Function error location: {}".format(traceback.format_exc()))
                continue

    def get_function_by_name(self, function_name):
        """
        Find a functionClass by a name specified by a user. Not functionClass.__name__
        :param function_name: Name of the function to search for
        """
        # Convert name to lower case
        function_name = function_name.lower()
        if function_name in self.function_names:
            return self.function_names[function_name]
        # Check without underscores. People might still use underscores to separate words in a function name
        function_name = function_name.replace('_', ' ')
        if function_name in self.function_names:
            return self.function_names[function_name]
        return None

    def get_function_class_list(self):
        """Returns a simple flat list of all function classes."""
        function_class_list = []
        for module_object in self.function_dict:
            function_class_list += list(self.function_dict[module_object])
        return function_class_list

    def get_function_object(self, function_class):
        """
        If persistent, gets an object from dictionary. Otherwise creates a new object.
        :param function_class: Class of function to retrieve or create function object for
        """
        if function_class.is_persistent():
            function_obj = self.persistent_functions[function_class]
        else:
            function_obj = function_class()
        return function_obj

    def check_function_permissions(self, function_class, server_obj, user_obj, channel_obj):
        """Checks if a function can be called. Returns boolean, True if allowed
        :param function_class: Class of function to check permissions for
        :type function_class: type
        :param server_obj: Server on which to check function permissions
        :type server_obj: Server.Server
        :param user_obj: User which has requested the function
        :type user_obj: Destination.User
        :param channel_obj: Channel on which the function was requested
        :type channel_obj: Destination.Channel | None
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

    def reload_module(self, module_name):
        """
        Reloads a function module, or loads it if it is not already loaded. Returns True on success, False on failure
        :param module_name: Name of the module to reload
        """
        # Check it's an allowed module
        if module_name not in self.module_list:
            self.hallo.printer.output_raw("Module name, {}, is not in allowed list: {}."
                                          .format(module_name, ", ".join(self.module_list)))
            return False
        # Create full name
        # TODO: allow bypass for reloading of core classes: Hallo, Server, Destination, etc
        full_module_name = "modules.{}".format(module_name)
        # Check if module has already been imported
        if full_module_name in sys.modules:
            module_obj = sys.modules[full_module_name]
            self._reload(module_obj)
        else:
            # Try and load new module, return False if it doesn't exist
            try:
                module_obj = importlib.import_module(full_module_name)
            except ImportError:
                self.hallo.printer.output_raw("Could not import module")
                return False
        # Unload module, if it was loaded.
        self.unload_module_functions(module_obj)
        # Loop through module, searching for Function subclasses.
        for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
            # Get class from tuple
            function_class = function_tuple[1]
            # Ensure it is a member of this module
            if function_class.__module__ != full_module_name:
                continue
            # Check it's a valid function object
            if not self.check_function_class(function_class):
                continue
            # Try and load function, if it fails, try and unload it.
            try:
                self.load_function(function_class)
            except NotImplementedError:
                self.unload_function(function_class)
        return True

    def _reload(self, module_obj):
        """
        Actually reloads the module
        :param module_obj: Module to reload
        :type module_obj: module
        :return: None
        """
        try:
            # noinspection PyUnresolvedReferences
            importlib.reload(module_obj)
        except AttributeError:
            # noinspection PyDeprecation
            imp.reload(module_obj)

    def unload_module_functions(self, module_obj):
        """
        Unloads a module, unloading all the functions it contains
        :param module_obj: Module to unload
        """
        # If module isn't in mFunctionDict, cancel
        if module_obj not in self.function_dict:
            return
        function_list = list(self.function_dict[module_obj])
        for function_class in function_list:
            self.unload_function(function_class)
        del self.function_dict[module_obj]

    @staticmethod
    def check_function_class(function_class):
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

    def load_function(self, function_class):
        """
        Loads a function class into all the relevant dictionaries
        :param function_class: Class of the function to load into dispatcher
        """
        # Get module of function
        module_name = function_class.__module__
        module_obj = sys.modules[module_name]
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
        self.function_dict[module_obj][function_class]['names'] = names_list
        self.function_dict[module_obj][function_class]['events'] = events_list
        # Add function to mFunctionNames
        for function_name in names_list:
            if function_name in self.function_names:
                raise NotImplementedError("This function name \"{}\", in \"{}\" function class is "
                                          "already taken by the \"{}\" function class."
                                          .format(function_name,
                                                  function_class.__name__,
                                                  self.function_names[function_name].__name__))
            self.function_names[function_name] = function_class
        # Add function to mEventFunctions
        for function_event in events_list:
            if function_event not in self.event_functions:
                self.event_functions[function_event] = set()
            self.event_functions[function_event].add(function_class)

    def unload_function(self, function_class):
        """
        Unloads a function class from all the relevant dictionaries
        :param function_class: Class of the function which is being unloaded
        """
        # Get module of function
        module_name = function_class.__module__
        module_obj = sys.modules[module_name]
        # Check that function is loaded
        if module_obj not in self.function_dict:
            return
        if function_class not in self.function_dict[module_obj]:
            return
        # Get list of function names and list of events functions respond to
        names_list = self.function_dict[module_obj][function_class]['names']
        events_list = self.function_dict[module_obj][function_class]['events']
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
                print("Failed to save {}".format(function_class.__name__))
                print(str(e))
            del self.persistent_functions[function_class]
        # Remove from mFunctionDict
        del self.function_dict[module_obj][function_class]

    def close(self):
        """Shut down FunctionDispatcher, save all functions, etc"""
        for module_object in list(self.function_dict):
            self.unload_module_functions(module_object)

    def to_xml(self):
        """Output the FunctionDispatcher in XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("function_dispatcher")
        doc.appendChild(root)
        # create name element
        module_list_elem = doc.createElement("module_list")
        for module_name in self.module_list:
            module_elem = doc.createElement("module")
            module_name_elem = doc.createElement("name")
            module_name_elem.appendChild(doc.createTextNode(module_name))
            module_elem.appendChild(module_name_elem)
            module_list_elem.appendChild(module_elem)
        root.appendChild(module_list_elem)
        # output XML string
        return doc.toxml()

    @staticmethod
    def from_xml(xml_string, hallo):
        """Loads a new FunctionDispatcher from XML
        :param xml_string: XML string which can be parsed to build function dispatcher
        :param hallo: Hallo object which owns this FunctionDispatcher
        """
        doc = minidom.parseString(xml_string)
        # Create module list from XML
        module_list = set()
        module_list_elem = doc.getElementsByTagName("module_list")[0]
        for module_elem in module_list_elem.getElementsByTagName("module"):
            module_name_elem = module_elem.getElementsByTagName("name")[0]
            module_name = module_name_elem.firstChild.data
            module_list.add(module_name)
        # Create new FunctionDispatcher
        new_function_dispatcher = FunctionDispatcher(module_list, hallo)
        return new_function_dispatcher

    def to_json(self):
        """
        Output the function dispatcher configuration in a dict format for saving as json
        :return: dict
        """
        json_obj = dict()
        json_obj["modules"] = []
        for module_name in self.module_list:
            json_obj["modules"].append({"name": module_name})
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        """
        Creates a function dispatcher from json object dict
        :param json_obj: dict
        :param hallo: Hallo
        :return: FunctionDispatcher
        """
        module_list = set()
        for module in json_obj["modules"]:
            module_list.add(module["name"])
        new_dispatcher = FunctionDispatcher(module_list, hallo)
        return new_dispatcher
