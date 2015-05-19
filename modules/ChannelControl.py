from Function import Function

class Operator(Function):
    '''
    Gives a user on an irc server "operator" status.
    '''
    #Name for use in help listing
    mHelpName = "op"
    #Names which can be used to address the function
    mNames = set(["op","operator","give op","gib op","get op","give operator","gib operator","get operator"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Op member in given channel, or current channel if no channel given. Or command user if no member given. Format: op <name> <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!="irc"):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        #If 0 arguments, op user who called command.
        lineSplit = line.split()
        if(len(lineSplit)==0):
            serverObject.send("MODE +o "+userObject.getName(),None,"raw")
            return "Op status given."
        #If 1 argument, see if it's a channel or a user.
        #If 2 arguments, determine which is channel and which is user.