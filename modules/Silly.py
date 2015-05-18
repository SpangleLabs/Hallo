from Function import Function

class Is(Function):
    '''
    A fun function which makes hallo respond to any message starting "hallo is..."
    '''
    #Name for use in help listing
    mHelpName = "is"
    #Names which can be used to address the function
    mNames = set(["is"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Placeholder. Format: is"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        return "I am?"