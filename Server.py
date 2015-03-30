from xml.dom import minidom


class Server(object):
    '''
    Generic server object. An interface for ServerIRC or ServerSkype or whatever objects.
    '''
    #Persistent/saved class variables
    mHallo = None               #The hallo object that created this server
    mName = None                #server name
    mAutoConnect = True         #Whether to automatically connect to this server when hallo starts
    mChannelList = []           #list of channels on this server (which may or may not be currently active)
    mConnection = None          #Connection for the server, socket or whatnot
    mNick = None                #Nickname to use on this server
    mPrefix = None              #Prefix to use with functions on this server
    mFullName = None            #Full name to use on this server
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server
    mUserList = []              #Users on this server

    def __init__(self, params):
        '''
        Constructor for server object
        '''
        raise NotImplementedError
    
    def connect(self):
        raise NotImplementedError
    
    def disconnect(self):
        raise NotImplementedError
    
    def run(self):
        '''
        Method to read from stream and process. Will call an internal parsing method or whatnot
        '''
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString):
        '''
        Constructor to build a new server object from xml
        '''
        
    def toXml(self):
        '''
        Returns an XML representation of the server object
        '''
    
    def getName(self):
        'Name getter'
        return self.mName
    
    def getNick(self):
        'Nick getter'
        if(self.mNick==None):
            return self.mHallo.getNick()
        return self.mNick
    
    def setNick(self,nick):
        'Nick setter'
        self.mNick = nick
        
    def getPrefix(self):
        'Prefix getter'
        if(self.mPrefix==None):
            return self.mHallo.getDefaultPrefix()
        return self.mPrefix
    
    def setPrefix(self,prefix):
        'Prefix setter'
        self.mPrefix = prefix
    
    def getFullName(self):
        'Full name getter'
        if(self.mFullName==None):
            return self.mHallo.getDefaultFullName()
        return self.mFullName
    
    def setFullName(self,fullName):
        'Full name setter'
        self.mFullName = fullName
        
        
class ServerIRC(Server):
    #Persistent/saved class variables
    mName = None                #server name
    mAutoConnect = True         #Whether to automatically connect to this server when hallo starts
    mChannelList = []           #list of channels on this server (which may or may not be currently active)
    mConnection = None          #Connection for the server, socket or whatnot
    mNick = None                #Nickname to use on this server
    mPrefix = None              #Prefix to use with functions on this server
    mFullName = None            #Full name to use on this server
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server
    mUserList = []              #Users on this server
    #IRC specific variables
    mServerAddress = None       #Address to connect to server
    mServerPort = None          #Port to connect to server
    mNickservPass = None        #Password to identify with nickserv
    
    def __init__(self, params):
        '''
        Constructor for server object
        '''
        raise NotImplementedError
    
    def connect(self):
        raise NotImplementedError
    
    def disconnect(self):
        raise NotImplementedError
    
    def run(self):
        '''
        Method to read from stream and process. Will call an internal parsing method or whatnot
        '''
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString):
        '''
        Constructor to build a new server object from xml
        '''
        
    def toXml(self):
        '''
        Returns an XML representation of the server object
        '''
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("server")
        doc.appendChild(root)
        #create type element
        typeElement = doc.createElement("server_type")
        typeElement.appendChild(doc.createTextNode("IRC"))
        root.appendChild(typeElement)
        #create name element
        nameElement = doc.createElement("server_name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        #create auto connect element
        autoConnectElement = doc.createElement("auto_connect")
        autoConnectElement.appendChild(doc.createTextNode(self.mAutoConnect))
        root.appendChild(autoConnectElement)
        #TODO:create channel list element
        #create nick element
        if(self.mNick is not None):
            nickElement = doc.createElement("server_nick")
            nickElement.appendChild(doc.createTextNode(self.mNick))
            root.appendChild(nickElement)
        #create prefix element
        if(self.mPrefix is not None):
            prefixElement = doc.createElement("server_prefix")
            prefixElement.appendChild(doc.createTextNode(self.mPrefix))
            root.appendChild(prefixElement)
        #create full name element
        if(self.mFullName is not None):
            fullNameElement = doc.createElement("full_name")
            fullNameElement.appendChild(doc.createTextNode(self.mFullName))
            root.appendChild(fullNameElement)
        #create server address element
        serverAddressElement = doc.createElement("server_address")
        serverAddressElement.appendChild(doc.createTextNode(self.mServerAddress))
        root.appendChild(serverAddressElement)
        #create server port element
        serverPortElement = doc.createElement("server_port")
        serverPortElement.appendChild(doc.createTextNode(self.mServerPort))
        root.appendChild(serverPortElement)
        #create nickserv pass element
        nickservPassElement = doc.createElement("nickserv_pass")
        nickservPassElement.appendChild(doc.createTextNode(self.mNickservPass))
        root.appendChild(nickservPassElement)
        #output XML string
        return doc.toxml()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        