import time

from xml.dom import minidom

class Destination:
    '''
    Destination is an object that both Channel and User inherit from. It just means messages can be sent to these entities.
    '''
    mType = None        #The type of destination, "channel" or "user"
    mServer = None      #The server object this destination belongs to
    mName = None        #Destination name, where to send messages
    mLogging = True     #Whether logging is enabled for this destination
    mLastActive = None  #Timestamp of when they were last active
    mUseCapsLock = False    #Whether to use caps lock when communicating to this destination

    def __init__(self,name,server):
        '''
        Constructor
        '''
        raise NotImplementedError
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
    
    def getLogging(self):
        'Boolean, whether the destination is supposed to have logging.'
        return self.mLogging

    def getServer(self):
        'Returns the server object that this destination belongs to'
        return self.mServer
    
    def updateActivity(self):
        'Updates LastActive timestamp'
        self.mLastActive = time.time()
        if(self.mInChannel==False):
            self.mInChannel = True
        if(self.mOnline==False):
            self.mOnline = True
        
    def getLastActive(self):
        'Returns when the destination was last active'
        return self.mLastActive
    
    def isUpperCase(self):
        'Returns a boolean representing whether to use caps lock'
        return self.mUseCapsLock
    
    def setUpperCase(self,upperCase):
        'Sets whether the destination uses caps lock'
        self.mUseCapsLock = upperCase
        
    def toXml(self):
        'Returns the Destination object XML'
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new Destination object from XML'

class Channel(Destination):
    mType = "channel"           #This is a channel object
    mPassword = None            #Channel password, or none.
    mUserList = set()              #Users in the channel
    mInChannel = False          #Whether or not hallo is in the channel
    mPassiveEnabled = True       #Whether to use passive functions in the channel
    
    def getPassword(self):
        'Channel password getter'
        return self.mPassword
    
    def setPassword(self,password):
        'Channel password setter'
        self.mPassword = password
    
    def getUserList(self):
        'Returns the full user list of the channel'
        return self.mUserList

    def addUser(self,user):
        'Adds a new user to a given channel'
        self.mUserList.add(user)
        user.addChannel(self)
    
    def setUserList(self,userList):
        'Sets the entire user list of a channel'
        self.mUserList = userList
        for user in userList:
            user.addChannel(self)
            
    def isPassiveEnabled(self):
        'Whether or not passive functions are enabled in this channel'
        return self.mPassiveEnabled
    
    def setPassiveEnabled(self,passiveEnabled):
        'Sets whether pasive functions are enabled in this channel'
        self.mPassiveEnabled = passiveEnabled
        
    def toXml(self):
        'Returns the Channel object XML'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("channel")
        doc.appendChild(root)
        #create name element
        nameElement = doc.createElement("channel_name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        #create logging element
        loggingElement = doc.createElement("logging")
        loggingElement.appendChild(doc.createTextNode(self.mLogging))
        root.appendChild(loggingElement)
        #create caps_lock element, to say whether to use caps lock
        capsLockElement = doc.createElement("caps_lock")
        capsLockElement.appendChild(doc.createTextNode(self.mUseCapsLock))
        root.appendChild(capsLockElement)
        #create password element
        if(self.mPassword is not None):
            passwordElement = doc.createElement("password")
            passwordElement.appendChild(doc.createTextNode(self.mPassword))
            root.appendChild(passwordElement)
        #create passive_enabled element, saying whether passive functions are enabled
        passiveEnabledElement = doc.createElement("passive_enabled")
        passiveEnabledElement.appendChild(doc.createTextNode(self.mPassiveEnabled))
        root.appendChild(passiveEnabledElement)
        #output XML string
        return doc.toxml()
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new Destination object from XML'
    
class User(Destination):
    mType = "user"              #This is a user object
    mIdentified = False         #Whether the user is identified (with nickserv)
    mChannelList = set()        #List of channels this user is in
    mOnline = False             #Whether or not the user is online
    
    def isIdentified(self):
        'Checks whether this user is identified'
        #TODO: If false, do an ident check
        return self.mIdentified
    
    def getChannelList(self):
        'Returns the list of channels this user is in'
        return self.mChannelList
    
    def addChannel(self,channel):
        'Adds a new channel to a given user'
        self.mChannelList.add(channel)
        
    def setChannelList(self,channelList):
        'Sets the entire channel list of a user'
        self.mChannelList = channelList