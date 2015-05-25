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

class Help(Function):
    '''
    Allows users to request help on using Hallo
    '''
    #Name for use in help listing
    mHelpName = "help"
    #Names which can be used to address the Function
    mNames = set(["help","readme","info","read me"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Gives information about commands.  Use \"help\" for a list of commands, or \"help <command>\" for help on a specific command."
    
    mHalloObject = None     #Hallo object containing everything.
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        self.mHalloObject = userObject.getServer().getHallo()
        if(line.strip()==""):
            return self.listAllFunctions(userObject,destinationObject)
        else:
            functionName = line.strip().lower()
            return self.getHelpOnFunction(functionName)
        
    def listAllFunctions(self,userObject,destinationObject):
        'Returns a list of all functions.'
        #Get required objects
        serverObject = userObject.getServer()
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        #Get list of function classes
        functionClassList = functionDispatcher.getFunctionClassList()
        #Construct list of available function names
        outputList = []
        for functionClass in functionClassList:
            functionObject = functionDispatcher.getFunctionObject(functionClass)
            functionHelpName = functionObject.getHelpName()
            #Check permissions allow user to use this function
            if(functionDispatcher.checkFunctionPermissions(functionClass,serverObject,userObject,destinationObject)):
                outputList.append(functionHelpName)
        #Construct the output string
        outputString = "List of available functions: " + ", ".join(outputList)
        return outputString
        
    def getHelpOnFunction(self,functionName):
        'Returns help documentation on a specified function.'
        #Get required objects
        functionDispatcher = self.mHalloObject.getFunctionDispatcher()
        functionClass = functionDispatcher.getFunctionByName(functionName)
        #If function isn't defined, return an error.
        if(functionClass is None):
            return "No function by that name exists"
        #Get the current object (new one if non-persistent)
        functionObject = functionDispatcher.getFunctionObject(functionClass)
        #Try and output help message, throwing an error if the function hasn't defined it
        try:
            helpMessage = "Documentation for \""+functionObject.getHelpName()+"\": "+functionObject.getHelpDocs()
            return helpMessage
        except NotImplementedError:
            return "No documentation exists for that function"
