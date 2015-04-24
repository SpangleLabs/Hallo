from Function import Function

class Roll(Function):
    '''
    Function to roll dice
    '''
    mHelpName = "roll"                          #Name for use in help listing
    mNames = set("roll","dice","random")        #Names which can be used to address the function
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Roll X-Y returns a random number between X and Y. Format: \"roll <min>-<max>\" or \"roll <num>d<sides>\""

    def __init__(self, params):
        '''
        Constructor
        '''
        
    def run(self,line,userObject,channelObject=None):
        pass