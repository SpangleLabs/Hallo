import importlib
import imp
import sys
import inspect

from Function import Function

class FunctionDispatcher(object):
    '''
    classdocs
    '''
    mHallo = None       #Hallo object which owns this
    mModuleList = []    #List of available module names
    mFunctionDict = {}  #Dictionary of moduleObjects->functionClasses->nameslist/eventslist
    mFunctionNames = {}         #Dictionary of names -> functionClasses
    mPersistentFunctions = {}   #Dictionary of persistent function objects. functionClass->functionObject
    mEventFunctions = {}        #Dictionary with events as keys and sets of function classes (which may want to act on those events) as arguments

    def __init__(self, params):
        '''
        Constructor
        '''
        #Load all functions
        for moduleName in self.mModuleList:
            self.reloadModule(moduleName)
    
    def dispatch(self,functionName,functionArgs,userObject,channelObject=None):
        'Sends the function call out to whichever function, if one is found'
        pass
    
    def dispatchPassive(self,event,fullLine,userObject,channelObject=None):
        'Dispatches a event call to passive functions, if any apply'
        pass
    
    def reloadModule(self,moduleName):
        'Reloads a function module, or loads it if it is not already loaded. Returns True on success, False on failure'
        #Check it's an allowed module
        if(moduleName not in self.mModuleList):
            return False
        #Create full name TODO: allow bypass for User, Channel, Destination, Server, Hallo, Function, FunctionDispatcher, UserGroup, PermissionMask reloading
        fullModuleName = "modules."+moduleName
        #Check if module has already been imported
        if(fullModuleName in sys.modules):
            #TODO: Remove old instances from dictionaries?
            moduleObject = sys.modules[fullModuleName]
            imp.reload(moduleObject)
        else:
            moduleObject = importlib.import_module(fullModuleName)
        #Loop through module, searching for Function subclasses.
        for functionClass in inspect.getmembers(moduleObject,inspect.isclass):
            #Check it's a valid function object
            if(not self.checkFunction(functionClass)):
                continue
            #Get list of names and add function to the dictionary
            #If persistent, load object and store it
            #Get list of passive events, add all to that dictionary
            
    def checkFunction(self,functionClass):
        'Checks a potential class to see if it is a valid Function subclass class'
        #Make sure it's not the Function class
        if(functionClass == Function):
            return False
        #Make sure it is a subclass of Function
        if(not issubclass(functionClass,Function)):
            return False
        #Create function object
        functionObject = functionClass()
        #Check that help name is defined
        try:
            helpName = functionObject.getHelpName()
        except NotImplementedError:
            return False
        #Check that help docs are defined
        try:
            functionObject.getHelpDocs()
        except NotImplementedError:
            return False
        #Check that names list is not empty
        try:
            namesList = functionObject.getNames()
            if(len(namesList)==0):
                return False
            #Check that names list contains help name
            if(helpName not in namesList):
                return False
        except NotImplementedError:
            return False
        #If it passed all those tests, it's valid, probably
        return True
    
    def loadFunction(self,functionClass):
        'Loads a function class into all the relevant dictionaries'
        #Get module of function
        moduleName = functionClass.__module__
        moduleObject = sys.modules[moduleName]
        #If function is persistent, load it up and add to mPersistentFunctions
        if(functionClass.isPersistent()):
            functionObject = functionClass.loadFunction()
            self.mPersistentFunctions[functionClass] = functionObject
        else:
            functionObject = functionClass()
        #Get names list and events list
        namesList = functionObject.getNames()
        eventsList = functionObject.getPassiveEvents()
        #Add names list and events list to mFunctionDict
        if(moduleObject not in self.mFunctionDict):
            self.mFunctionDict[moduleObject] = {}
        self.mFunctionDict[moduleObject][functionClass] = {}
        self.mFunctionDict[moduleObject][functionClass]['names'] = namesList
        self.mFunctionDict[moduleObject][functionClass]['events'] = eventsList
        #Add function to mFunctionNames
        for functionName in namesList:
            self.mFunctionNames[functionName] = functionClass
        #Add function to mEventFunctions
        for functionEvent in eventsList:
            if(functionEvent not in self.mEventFunctions):
                self.mEventFunctions[functionEvent] = set()
            self.mEventFunctions[functionEvent].add(functionClass)
    
    def unloadFunction(self,functionClass):
        'Unloads a function class from all the relevant dictionaries'
    
    def toXml(self):
        'Output the FunctionDispatcher in XML'
        pass
    
    @staticmethod
    def fromXml():
        'Loads a new FunctionDispatcher from XML'
        pass