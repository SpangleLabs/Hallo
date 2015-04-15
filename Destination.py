

class Destination:
    '''
    Destination is an object that both Channel and User inherit from. It just means messages can be sent to these entities.
    '''
    mType = None        #The type of destination, "channel" or "user"
    mServer = None      #The server object this destination belongs to
    mName = None        #Destination name, where to send messages
    mLogging = True     #Whether logging is enabled for this destination

    def __init__(self,name,server):
        '''
        Constructor
        '''
        self.mName = name.lower()
        self.mServer = server
        
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

    def getServer(self):
        'Returns the server object that this destination belongs to'

class Channel(Destination):
    mType = "channel"           #This is a channel object
    
    
class User(Destination):
    mType = "user"              #This is a user object
    mIdentified = False         #Whether the user is identified with nickserv
    
    def isIdentified(self):
        'Checks whether this user is identified'
        #TODO: If false, do an ident check
        return self.mIdentified
    