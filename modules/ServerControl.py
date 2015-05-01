
from Function import Function
from copyreg import constructor

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

class LeaveChannel(Function):
    '''
    Leaves a channel on a specified server
    '''
    #Name for use in help listing
    mHelpName = "leave"
    #Names which can be used to address the function
    mNames = set(["leave channel","leave","part"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Leave a channel.  Use \"leave <channel>\"."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        serverObject = userObject.getServer()
        channelName = line.split()[0].lower()
        channelObject = serverObject.getChannelByName(channelName)
        if(not channelObject.isInChannel()):
            return "I'm not in that channel."
        serverObject.leaveChannel(channelObject)
        return "Left "+channelName+"."

class Shutdown(Function):
    '''
    Shuts down hallo entirely.
    '''
    #Name for use in help listing
    mHelpName = "shutdown"
    #Names which can be used to address the Function
    mNames = set(["shutdown"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Shuts down hallo entirely."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        serverObject = userObject.getServer()
        halloObject = serverObject.getHallo()
        halloObject.close()
        return "Shutting down."
