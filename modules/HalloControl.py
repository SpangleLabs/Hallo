from Function import Function
import threading


class ConfigSave(Function):
    """
    Save the current config to xml.
    """
    # Name for use in help listing
    help_name = "config save"
    # Names which can be used to address the function
    names = {"config save", "configsave", "save config"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Save the config and pickle it."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        halloObject = user_obj.get_server().get_hallo()
        halloObject.save_to_xml()


class ModuleReload(Function):
    """
    Reloads a specific function module.
    """
    # Name for use in help listing
    help_name = "module reload"
    # Names which can be used to address the function
    names = {"module reload", "modulereload", "reload module"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Reloads a specified module."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        halloObject = user_obj.get_server().get_hallo()
        functionDispatcher = halloObject.get_function_dispatcher()
        reloadResult = functionDispatcher.reload_module(line)
        if reloadResult:
            return "Module reloaded."
        else:
            return "Failed to reload module."


class ActiveThreads(Function):
    """
    Checks the current number of running hallo threads.
    """
    # Name for use in help listing
    help_name = "active threads"
    # Names which can be used to address the function
    names = {"active threads", "activethreads", "threads"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Returns current number of active threads. Format: active thread"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """
        Returns current number of active threads.. should probably be gods only, but it is not. Format: active_thread
        """
        return "I think I have " + str(threading.active_count()) + " active threads right now."


class Help(Function):
    """
    Allows users to request help on using Hallo
    """
    # Name for use in help listing
    help_name = "help"
    # Names which can be used to address the Function
    names = {"help", "readme", "info", "read me"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Gives information about commands.  Use \"help\" for a list of commands, " \
                "or \"help <command>\" for help on a specific command."

    mHalloObject = None  # Hallo object containing everything.

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        self.mHalloObject = user_obj.get_server().get_hallo()
        if line.strip() == "":
            return self.listAllFunctions(user_obj, destination_obj)
        else:
            functionName = line.strip().lower()
            return self.getHelpOnFunction(functionName)

    def listAllFunctions(self, userObject, destinationObject):
        """Returns a list of all functions."""
        # Get required objects
        serverObject = userObject.get_server()
        functionDispatcher = self.mHalloObject.get_function_dispatcher()
        # Get list of function classes
        functionClassList = functionDispatcher.get_function_class_list()
        # Construct list of available function names
        outputList = []
        for functionClass in functionClassList:
            functionObject = functionDispatcher.get_function_object(functionClass)
            functionHelpName = functionObject.get_help_name()
            # Check permissions allow user to use this function
            if (
                    functionDispatcher.check_function_permissions(functionClass, serverObject, userObject,
                                                                  destinationObject)):
                outputList.append(functionHelpName)
        # Construct the output string
        outputString = "List of available functions: " + ", ".join(outputList)
        return outputString

    def getHelpOnFunction(self, functionName):
        """Returns help documentation on a specified function."""
        # Get required objects
        functionDispatcher = self.mHalloObject.get_function_dispatcher()
        functionClass = functionDispatcher.get_function_by_name(functionName)
        # If function isn't defined, return an error.
        if functionClass is None:
            return "No function by that name exists"
        # Get the current object (new one if non-persistent)
        functionObject = functionDispatcher.get_function_object(functionClass)
        # Try and output help message, throwing an error if the function hasn't defined it
        try:
            helpMessage = "Documentation for \"" + functionObject.get_help_name() + "\": " + functionObject.get_help_docs()
            return helpMessage
        except NotImplementedError:
            return "No documentation exists for that function"
