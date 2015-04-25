
FUNC_EVENT_PING = "ping"            #Event constant signifying a server ping has been received
FUNC_EVENT_MESSAGE = "message"      #Event constant signifying a standard message
FUNC_EVENT_JOIN = "join_channel"    #Event constant signifying someone joined a channel
FUNC_EVENT_LEAVE = "leave_channel"  #Event constant signifying someone left a channel
FUNC_EVENT_QUIT = "quit"            #Event constant signifying someone disconnected
FUNC_EVENT_CHNAME = "name_change"   #Event constant signifying someone changed their name
FUNC_EVENT_KICK = "kick"            #Event constant signifying someone was forcibly removed from the channel
FUNC_EVENT_NOTICE = "notice"        #Event constant signifying a notice was received. (IRC only?)
FUNC_EVENT_MODE = "mode_change"     #Event constant signifying a channel mode change. (IRC only?)
FUNC_EVENT_CTCP = "message_ctcp"    #Event constant signifying a CTCP message received (IRC only)


class Function:
    '''
    Generic function object. All functions inherit from this.
    '''
    mHelpName = None    #Name for use in help listing
    mNames = set()      #Names which can be used to address the function
    mHelpDocs = None    #Help documentation, if it's just a single line, can be set here
    #Static constants
    EVENT_PING = "ping"            #Event constant signifying a server ping has been received
    EVENT_MESSAGE = "message"      #Event constant signifying a standard message
    EVENT_JOIN = "join_channel"    #Event constant signifying someone joined a channel
    EVENT_LEAVE = "leave_channel"  #Event constant signifying someone left a channel
    EVENT_QUIT = "quit"            #Event constant signifying someone disconnected
    EVENT_CHNAME = "name_change"   #Event constant signifying someone changed their name
    EVENT_KICK = "kick"            #Event constant signifying someone was forcibly removed from the channel
    EVENT_NOTICE = "notice"        #Event constant signifying a notice was received. (IRC only?)
    EVENT_MODE = "mode_change"     #Event constant signifying a channel mode change. (IRC only?)
    EVENT_CTCP = "message_ctcp"    #Event constant signifying a CTCP message received (IRC only)
    

    def __init__(self, params):
        '''
        Constructor for the function
        '''
        raise NotImplementedError
    
    def run(self,line,userObject,channelObject=None):
        'Runs the function when it is called directly'
        raise NotImplementedError

    @staticmethod
    def isPersistent(self):
        'Returns boolean representing whether this function is supposed to be persistent or not'
        return False
    
    @staticmethod
    def loadFunction():
        'Loads the function, persistent functions only.'
        raise NotImplementedError
    
    def saveFunction(self):
        'Saves the function, persistent functions only.'
        raise NotImplementedError
    
    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set()

    def passiveRun(self,event,fullLine,userObject,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        pass
        
    def getHelpName(self):
        'Returns the name to be printed for help documentation'
        if(self.mHelpName is None):
            raise NotImplementedError
        return self.mHelpName
    
    def getHelpDocs(self,arguments=None):
        'Returns the help documentation, specific to given arguments, if supplied'
        if(self.mHelpDocs is None):
            raise NotImplementedError
        return self.mHelpDocs
    
    def getNames(self):
        'Returns the list of names for directly addressing the function'
        return self.mNames.add(self.mHelpName)
    
    
