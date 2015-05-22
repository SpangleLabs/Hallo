import importlib
import imp
import sys
import inspect
from xml.dom import minidom

from Function import Function

class FunctionDispatcher(object):
    '''
    FunctionDispatcher is a class to manage functions and to send function requests to the relevant function.
    '''
    mHallo = None                 #Hallo object which owns this
    mModuleList = None            #List of available module names, then function names, then various variables
    mFunctionDict = None          #Dictionary of moduleObjects->functionClasses->nameslist/eventslist
    mFunctionNames = None         #Dictionary of names -> functionClasses
    mPersistentFunctions = None   #Dictionary of persistent function objects. functionClass->functionObject
    mEventFunctions = None        #Dictionary with events as keys and sets of function classes (which may want to act on those events) as arguments

    def __init__(self,moduleList,hallo):
        '''
        Constructor
        '''
        self.mHallo = hallo
        self.mModuleList = set()
        self.mFunctionDict = {}
        self.mFunctionNames = {}
        self.mPersistentFunctions = {}
        self.mEventFunctions = {}
        #Copy moduleList to self.mModuleList
        self.mModuleList = moduleList
        #Load all functions
        for moduleName in self.mModuleList:
            self.reloadModule(moduleName)
    
    def dispatch(self,functionMessage,userObject,destinationObject):
        'Sends the function call out to whichever function, if one is found'
        #Get server object
        serverObject = destinationObject.getServer()
        #Find the function name. Try joining each amount of words in the message until you find a valid function name
        functionMessageSplit = functionMessage.split()
        for functionNameTest in [' '.join(functionMessageSplit[:x+1]) for x in range(len(functionMessageSplit))[::-1]]:
            functionClassTest = self.getFunctionByName(functionNameTest)
            functionArgsTest = ' '.join(functionMessageSplit)[len(functionNameTest):].strip()
            if(functionClassTest is not None):
                break
        #If function isn't found, output a not found message
        if(functionClassTest is None):
            serverObject.send("This is not a recognised function.",destinationObject)
            print("This is not a recognised function.")
            return
        functionClass = functionClassTest
        functionArgs = functionArgsTest
        #Check function rights and permissions
        if(not self.checkFunctionPermissions(functionClass,serverObject,userObject,destinationObject)):
            serverObject.send("You do not have permission to use this function.",destinationObject)
            print("You do not have permission to use this function.")
            return
        #If persistent, get the object, otherwise make one
        functionObject = self.getFunctionObject(functionClass)
        #Try running the function, if it fails, return an error message
        try:
            response = functionObject.run(functionArgs,userObject,destinationObject)
            if(response is not None):
                serverObject.send(response,destinationObject)
                print(response)
            return
        except Exception as e:
            serverObject.send("Function failed with error message: "+str(e),destinationObject)
            print("Function: "+str(functionClass.__module__)+" "+str(functionClass.__name__))
            print("Function error: "+str(e))
            return
    
    def dispatchPassive(self,event,fullLine,serverObject=None,userObject=None,channelObject=None):
        'Dispatches a event call to passive functions, if any apply'
        #If this event is not used, skip this
        if(event not in self.mEventFunctions or len(self.mEventFunctions[event])==0):
            return
        #Get destination object
        destinationObject = channelObject
        if(destinationObject is None):
            destinationObject = userObject
        #Get list of functions that want things
        functionList = self.mEventFunctions[event]
        for functionClass in functionList:
            #Check function rights and permissions
            if(not self.checkFunctionPermissions(functionClass,serverObject,userObject,channelObject)):
                continue
            #If persistent, get the object, otherwise make one
            functionObject = self.getFunctionObject(functionClass)
            #Try running the function, if it fails, return an error message
            try:
                response = functionObject.passiveRun(self,event,fullLine,serverObject,userObject,channelObject)
                if(response is not None):
                    if(destinationObject is not None and serverObject is not None):
                        serverObject.send(response,destinationObject)
                    print(response)
                return
            except Exception as e:
                print("Passive Function: "+str(functionClass.__module__)+" "+str(functionClass.__name__))
                print("Function event: "+str(event))
                print("Function error: "+str(e))
                return
    
    def getFunctionByName(self,functionName):
        'Find a functionClass by a name specified by a user. Not functionClass.__name__'
        #Convert name to lower case
        functionName = functionName.lower()
        if(functionName in self.mFunctionNames):
            return self.mFunctionNames[functionName]
        #Check without underscores. People might still use underscores to separate words in a function name
        functionName = functionName.replace('_',' ')
        if(functionName in self.mFunctionNames):
            return self.mFunctionNames[functionName]
        return None
    
    def getFunctionClassList(self):
        'Returns a simple flat list of all function classes.'
        functionClassList = []
        for moduleObject in self.mFunctionDict:
            functionClassList += list(self.mFunctionDict[moduleObject])
        return functionClassList
    
    def getFunctionObject(self,functionClass):
        'If persistent, gets an object from dictionary. Otherwise creates a new object.'
        if(functionClass.isPersistent()):
            functionObject = self.mPersistentFunctions[functionClass]
        else:
            functionObject = functionClass()
        return functionObject
        
    def checkFunctionPermissions(self,functionClass,serverObject,userObject=None,channelObject=None):
        'Checks if a function can be called. Returns boolean, True if allowed'
        #Get function name
        functionName = functionClass.__name__
        rightName = "function_"+functionName
        #Check rights
        if(userObject is not None):
            if(userObject.rightsCheck(rightName,channelObject) is False):
                return False
        elif(channelObject is not None):
            if(channelObject.rightsCheck(rightName) is False):
                return False
        elif(serverObject is not None):
            if(serverObject.rightsCheck(rightName) is False):
                return False
        if(self.mHallo.getPermissionMask().rightsCheck(rightName) is False):
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
            #Try and load new module, return False if it doesn't exist
            try:
                moduleObject = importlib.import_module(fullModuleName)
            except ImportError:
                return False
        #Unload module, if it was loaded.
        self.unloadModule(moduleObject)
        #Loop through module, searching for Function subclasses.
        for functionTuple in inspect.getmembers(moduleObject,inspect.isclass):
            #Get class from tuple
            functionClass = functionTuple[1]
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
            if(namesList is None):
                return False
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
        
    def close(self):
        'Shut down FunctionDispatcher, save all functions, etc'
        for moduleObject in self.mFunctionDict:
            self.unloadModule(moduleObject)
    
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
    def fromXml(xmlString,hallo):
        'Loads a new FunctionDispatcher from XML'
        doc = minidom.parseString(xmlString)
        #Create module list from XML
        moduleList = set()
        moduleListElement = doc.getElementsByTagName("module_list")[0]
        for moduleXml in moduleListElement.getElementsByTagName("module"):
            moduleNameElement = moduleXml.getElementsByTagName("name")[0]
            moduleName = moduleNameElement.firstChild.data
            moduleList.add(moduleName)
        #Create new FunctionDispatcher
        newFunctionDispatcher = FunctionDispatcher(moduleList,hallo)
        return newFunctionDispatcher
    
    