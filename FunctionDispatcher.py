

class FunctionDispatcher(object):
    '''
    classdocs
    '''
    mHallo = None       #Hallo object which owns this
    mModuleList = []    #List of available modules
    mFunctionDict = {}  #Dictionary of function names to function classes
    mPersistentFunctions = {}   #Dictionary of persistent function objects
    mEventFunctions = {}        #Dictionary with events as keys and sets of functions (which may want to act on those events) as arguments


    def __init__(self, params):
        '''
        Constructor
        '''
    
    def dispatch(self,functionName,functionArgs,userObject,channelObject=None):
        'Sends the function call out to whichever function, if one is found'
        pass
    
    def dispatchPassive(self,event,fullLine,userObject,channelObject=None):
        'Dispatches a event call to passive functions, if any apply'
        pass
    
    def reloadModule(self,moduleName):
        'Reloads a function module. Returns True on success, False on failure'
        #Check it's an allowed module
        if(moduleName not in self.mModuleList):
            return False
    
    def toXml(self):
        'Output the FunctionDispatcher in XML'
        pass
    
    @staticmethod
    def fromXml():
        'Loads a new FunctionDispatcher from XML'
        pass