
from Function import Function

class JoinChannel(Function):
    '''
    Joins a channel on a specified server
    '''
    #Name for use in help listing
    mHelpName = "join"
    #Names which can be used to address the function
    mNames = set(["join channel","join","channel"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Join a channel.  Use \"join <channel>\"."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        serverObject = userObject.getServer()
        channelName = line.split()[0].lower()
        channelPassword = None
        if(channelName!=line):
            channelPassword = line[len(channelName):]
        channelObject = serverObject.getChannelByName(channelName)
        channelObject.setPassword(channelPassword)
        if(channelObject.isInChannel()):
            return "I'm already in that channel."
        serverObject.joinChannel(channelObject)
        return "Joined "+channelName+"."
