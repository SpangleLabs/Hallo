import importlib
import imp
import sys
import inspect
from xml.dom import minidom

from Function import Function

class FunctionDispatcher(object):
    '''
    classdocs
    '''
    mHallo = None               #Hallo object which owns this
    mModuleList = set()         #List of available module names, then function names, then various variables
    mFunctionDict = {}          #Dictionary of moduleObjects->functionClasses->nameslist/eventslist
    mFunctionNames = {}         #Dictionary of names -> functionClasses
    mPersistentFunctions = {}   #Dictionary of persistent function objects. functionClass->functionObject
    mEventFunctions = {}        #Dictionary with events as keys and sets of function classes (which may want to act on those events) as arguments

    def __init__(self,moduleList):
        '''
        Constructor
        '''
        #Copy moduleList to self.mModuleList
        self.mModuleList = moduleList
        #Load all functions
        for moduleName in self.mModuleList:
            self.reloadModule(moduleName)
    
    def dispatch(self,functionName,functionArgs,userObject,channelObject=None):
        'Sends the function call out to whichever function, if one is found'
        pass
    
    def dispatchPassive(self,event,fullLine,userObject,channelObject=None):
        'Dispatches a event call to passive functions, if any apply'
        pass
    
    def checkFunctionCall(self,functionClass,userObject,channelObject):
        'Checks if a function can be called. Returns boolean, True if allowed'
        #Get function name
        functionName = functionClass.__name__
        rightName = "function_"+functionName
        #Check rights
        if(userObject.rightsCheck(rightName) is False):
            return False
        return True
    
    def reloadModule(self,moduleName):
        'Reloads a function module, or loads it if it is not already loaded. Returns True on success, False on failure'
        #Check it's an allowed module
        if(moduleName not in self.mModuleList):
            return False
        #Create full name TODO: allow bypass for User, Channel, Destination, Server, Hallo, Function, FunctionDispatcher, UserGroup, PermissionMask reloading
        fullModuleName = "modules."+moduleName
        #Check if module has already been imported
        if(fullModuleName in sys.modules):
            moduleObject = sys.modules[fullModuleName]
            imp.reload(moduleObject)
        else:
            moduleObject = importlib.import_module(fullModuleName)
        #Unload module, if it was loaded.
        self.unloadModule(moduleObject)
        #Loop through module, searching for Function subclasses.
        for functionClass in inspect.getmembers(moduleObject,inspect.isclass):
            #Check it's a valid function object
            if(not self.checkFunctionClass(functionClass)):
                continue
            #Try and load function, if it fails, try and unload it.
            try:
                self.loadFunction(functionClass)
            except NotImplementedError:
                self.unloadFunction(functionClass)
            
    def unloadModule(self,moduleObject):
        'Unloads a module, unloading all the functions it contains'
        #If module isn't in mFunctionDict, cancel
        if(moduleObject not in self.mFunctionDict):
            return
        for functionClass in self.mFunctionDict[moduleObject]:
            self.unloadFunction(functionClass)
        del self.mFunctionDict[moduleObject]
            
    def checkFunctionClass(self,functionClass):
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
        #Get module of function
        moduleName = functionClass.__module__
        moduleObject = sys.modules[moduleName]
        #Check that function is loaded
        if(moduleObject not in self.mFunctionDict):
            return
        if(functionClass not in self.mFunctionDict[moduleObject]):
            return
        #Get nameslist and events list
        namesList = self.mFunctionDict[moduleObject][functionClass]['names']
        eventsList = self.mFunctionDict[moduleObject][functionClass]['events']
        #Remove names from mFunctionNames
        for functionName in namesList:
            del self.mFunctionNames[functionName]
        #Remove events from mEventFunctions
        for functionEvent in eventsList:
            if(functionEvent not in self.mEventFunctions):
                continue
            if(functionClass not in self.mEventFunctions[functionEvent]):
                continue
            self.mEventFunctions[functionEvent].remove(functionClass)
        #If persistent, save object and remove from mPersistentFunctions
        if(functionClass.isPersistent()):
            functionObject = self.mPersistentFunctions[functionClass]
            try:
                functionObject.saveFunction()
            except:
                pass
            del self.mPersistentFunctions[functionClass]
        #Remove from mFunctionDict
        del self.mFunctionDict[moduleObject][functionClass]
    
    def toXml(self):
        'Output the FunctionDispatcher in XML'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("function_dispatcher")
        doc.appendChild(root)
        #create name element
        moduleListElement = doc.createElement("module_list")
        for moduleName in self.mModuleList:
            moduleElement = doc.createElement("module")
            moduleNameElement = doc.createElement("name")
            moduleNameElement.appendChild(doc.createTextNode(moduleName))
            moduleElement.appendChild(moduleNameElement)
            moduleListElement.appendChild(moduleElement)
        root.appendChild(moduleListElement)
        #output XML string
        return doc.toxml()
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new FunctionDispatcher from XML'
        doc = minidom.parse(xmlString)
        #Create module list from XML
        moduleList = set()
        moduleListElement = doc.getElementsByTagName("module_list")[0]
        for moduleXml in moduleListElement.getElementsByTagName("module"):
            moduleNameElement = moduleXml.getElementsByTagName("name")
            moduleName = moduleNameElement.firstChild.data
            moduleList.add(moduleName)
        #Create new FunctionDispatcher
        newFunctionDispatcher = FunctionDispatcher(moduleList)
        return newFunctionDispatcher
    
    