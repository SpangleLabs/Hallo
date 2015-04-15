

class Destination:
    '''
    Destination is an object that both Channel and User inherit from. It just means messages can be sent to these entities.
    '''
    mName = None        #Destination name, where to send messages
    mType = None        #The type of destination, "channel" or "user"
    mLogging = True     #Whether logging is enabled for this destination

    def __init__(self,name):
        '''
        Constructor
        '''
        self.mName = name.lower()
        
    def getName(self):
        'Name getter'
        return self.mName.lower()
    
    def setName(self,name):
        'Name setter'
        self.mName = name.lower()
        
    def getType(self):
        'Returns whether the destination is a user or channel.'
        return self.mType
        
    def isChannel(self):
        'Boolean, whether the destination is a channel.'
        if(self.mType=="channel"):
            return True
        else:
            return False
        
    def isUser(self):
        'Boolean, whether the destination is a user.'
        if(self.mType=="channel"):
            return False
        else:
            return True
    
    def hasLogging(self):
        'Boolean, whether the destination is supposed to have logging.'
        return self.mLogging

class Channel(Destination):
    mType = "channel"
    def __init__(self, params):
        '''
        Constructor
        '''
    
    
class User(Destination):
    mType = "user"
    def __init__(self, params):
        '''
        Constructor
        '''