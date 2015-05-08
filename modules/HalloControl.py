from Function import Function

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
