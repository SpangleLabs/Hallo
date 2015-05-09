from Function import Function
import threading

class ConfigSave(Function):
    '''
    Save the current config to xml.
    '''
    #Name for use in help listing
    mHelpName = "config save"
    #Names which can be used to address the function
    mNames = set(["config save","configsave","save config"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Save the config and pickle it."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        halloObject = userObject.getServer().getHallo()
        halloObject.saveToXml()

class ModuleReload(Function):
    '''
    Reloads a specific function module.
    '''
    #Name for use in help listing
    mHelpName = "module reload"
    #Names which can be used to address the function
    mNames = set(["module reload","modulereload","reload module"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Reloads a specified module."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        halloObject = userObject.getServer().getHallo()
        functionDispatcher = halloObject.getFunctionDispatcher()
        reloadResult = functionDispatcher.reloadModule(line)
        if(reloadResult == True):
            return "Module reloaded."
        else:
            return "Failed to reload module."

class ActiveThreads(Function):
    '''
    Checks the current number of running hallo threads.
    '''
    #Name for use in help listing
    mHelpName = "active threads"
    #Names which can be used to address the function
    mNames = set(["active threads","activethreads","threads"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns current number of active threads. Format: active thread"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        'Returns current number of active threads.. should probably be gods only, but it is not. Format: active_thread'
        return "I think I have " + str(threading.active_count()) + " active threads right now."
    
