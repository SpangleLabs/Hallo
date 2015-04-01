from xml.dom import minidom
from inc.commons import Commons
import socket

#TODO: investigate this
endl = Commons.mEndLine

class Server(object):
    '''
    Generic server object. An interface for ServerIRC or ServerSkype or whatever objects.
    '''
    mHallo = None               #The hallo object that created this server
    #Persistent/saved class variables
    mName = None                #server name
    mAutoConnect = True         #Whether to automatically connect to this server when hallo starts
    mChannelList = []           #list of channels on this server (which may or may not be currently active)
    mNick = None                #Nickname to use on this server
    mPrefix = None              #Prefix to use with functions on this server
    mFullName = None            #Full name to use on this server
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server
    mUserList = []              #Users on this server

    def __init__(self,hallo,params):
        '''
        Constructor for server object
        '''
        self.mHallo = hallo
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
    
    def send(self,data,channel=None,msgType="message"):
        'Sends a message to the server, or a specific channel in the server'
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString,hallo):
        '''
        Constructor to build a new server object from xml
        '''
        
    def toXml(self):
        '''
        Returns an XML representation of the server object
        '''
    
    def getHallo(self):
        'Returns the Hallo instance that created this Server'
        return self.mHallo
    
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
        
    def getAutoConnect(self):
        'AutoConnect getter'
        return self.mAutoConnect
    
    def setAutoConnect(self,autoConnect):
        'AutoConnect setter'
        self.mAutoConnect = autoConnect
        
        
class ServerIRC(Server):
    mHallo = None               #The hallo object that created this server
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
    #IRC specific dynamic variables
    mSocket = None              #Socket to communicate to the server
    mWelcomeMessage = ""        #Server's welcome message when connecting. MOTD and all.
    
    def __init__(self,hallo):
        '''
        Constructor for server object
        '''
        self.mHallo = hallo
    
    def connect(self):
        #TODO: remove all this core and conf
        # begin pulling data from a given server
        self.mHallo.core['server'][self.mName] = {}
        self.mHallo.core['server'][self.mName]['check'] = {}
        self.mHallo.core['server'][self.mName]['check']['names'] = ""
        self.mHallo.core['server'][self.mName]['check']['recipientonline'] = ""
        self.mHallo.core['server'][self.mName]['check']['nickregistered'] = False
        self.mHallo.core['server'][self.mName]['check']['userregistered'] = False
        self.mHallo.core['server'][self.mName]['channel'] = {}
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            self.mHallo.core['server'][self.mName]['channel'][channel] = {}
            self.mHallo.core['server'][self.mName]['channel'][channel]['last_message'] = 0
            self.mHallo.core['server'][self.mName]['channel'][channel]['user_list'] = []
            if(self.mHallo.conf['server'][self.mName]['channel'][channel]['megahal_record']):
                self.mHallo.core['server'][self.mName]['channel'][channel]['megahalcount'] = 0
        self.mHallo.core['server'][self.mName]['lastping'] = 0
        self.mHallo.core['server'][self.mName]['connected'] = False
        self.mHallo.core['server'][self.mName]['motdend'] = False
        self.mHallo.core['server'][self.mName]['open'] = True
        #End of the mess.
        self.mOpen = True
        #Create new socket
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #Connect to socket
            self.mSocket.connect((self.mServerAddress,self.mServerPort))
        except Exception as e:
            print("CONNECTION ERROR: " + str(e))
            self.mOpen = False
            #TODO: remove line
            self.mHallo.core['server'][self.mName]['open'] = False
        #Wait for the first message back from the server.
        print(Commons.currentTimestamp() + " waiting for first message from server: " + self.mName)
        firstLine = self.readLineFromSocket()  #TODO: make this timeout somehow.
        self.mWelcomeMessage += firstLine+"\n"
        #Send nick and full name to server
        print(Commons.currentTimestamp() + " sending nick and user info to server: " + self.mName)
        self.mSocket.send(('NICK ' + self.getNick() + endl).encode('utf-8'))
        self.mSocket.send(('USER ' + self.getFullName() + endl).encode('utf-8'))
        #Wait for MOTD to end
        while(True):
            nextWelcomeLine = self.readLineFromSocket()
            self.mWelcomeMessage += nextWelcomeLine+"\n"
            if("376" in nextWelcomeLine or "endofmessage" in nextWelcomeLine.replace(' ','').lower()):
                break
        #Identify with nickserv
        if self.mNickservPass:
            #TODO: update this
            self.mHallo.base_say('IDENTIFY ' + self.mNickservPass, [self.mName,'nickserv'])
        #Join channels
        print(Commons.currentTimestamp() + " joining channels on " + self.mName + ", identifying.")
        #TODO: update this with Channel objects
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if(self.mHallo.conf['server'][self.mName]['channel'][channel]['in_channel']):
                if(self.mHallo.conf['server'][self.mName]['channel'][channel]['pass'] == ''):
                    self.mHallo.core['server'][self.mName]['socket'].send(('JOIN ' + channel + endl).encode('utf-8'))
                else:
                    self.mHallo.core['server'][self.mName]['socket'].send(('JOIN ' + channel + ' ' + self.mHallo.conf['server'][self.mName]['channel'][channel]['pass'] + endl).encode('utf-8'))
    
    def disconnect(self):
        'Disconnect from the server'
        #TODO: upgrade this when logging is upgraded
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
        #    self.mHallo.base_say('Daisy daisy give me your answer do...',[server,channel])
            if(self.mHallo.conf['server'][self.mName]['channel'][channel]['in_channel'] and self.mHallo.conf['server'][self.mName]['channel'][channel]['logging']):
                self.mHallo.base_addlog(Commons.currentTimestamp() + ' '+self.getNick()+' has quit.',[self.mName,channel])
        #    time.sleep(1)
        if(self.mOpen):
            #self.mHallo.core['server'][self.mName]['socket'].send(('QUIT :Daisy daisy give me your answer do...' + endl).encode('utf-8'))
            self.mSocket.send(('QUIT :Will I dream?' + endl).encode('utf-8'))
            self.mSocket.close()
            self.mOpen = False
            #Remove self from Hallo's server list
            self.mHallo.removeServer()
            
    
    def run(self):
        '''
        Method to read from stream and process. Will call an internal parsing method or whatnot
        '''
        raise NotImplementedError
    
    def send(self,data,channel=None,msgType="message"):
        'Sends a message to the server, or a specific channel in the server'
        maxMsgLength = 450  #Maximum length of a message sent to the server
        if(msgType not in ["message","notice","raw"]):
            msgType = "message"
        #TODO: get channel address
        destinationName = channel.getName()
        #If it's raw data, just send it.
        if(msgType=="raw"):
            for dataLine in data.split("\n"):
                self.sendRaw(dataLine)
            return
        if(msgType=="notice"):
            msgTypeName = "NOTICE"
        else:
            msgTypeName = "PRIVMSG"
        msgMaxLength = maxMsgLength-len(msgTypeName+' '+destinationName+' ')

    def sendRaw(self,data):
        'Sends raw data to the server'
        self.mSocket.send((data+endl).encode("utf-8"))

    def readLineFromSocket(self):
        'Private method to read a line from the IRC socket.'
        nextLine = b""
        while(self.mOpen):
            try:
                nextByte = self.mSocket.recv(1)
            except:
                #TODO: reconnect
                nextByte = b""
            if(nextByte!=b"\n"):
                nextLine = nextLine + nextByte
            else:
                return self.decodeLine(nextLine)

    def decodeLine(self,rawBytes):
        'Decodes a line of bytes, trying a couple character sets'
        try:
            outputLine = rawBytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                outputLine = rawBytes.decode('iso-8859-1')
            except UnicodeDecodeError:
                outputLine = rawBytes.decode('cp1252')
        return outputLine

    @staticmethod
    def fromXml(xmlString,hallo):
        '''
        Constructor to build a new server object from xml
        '''
        doc = minidom.parse(xmlString)
        newServer = ServerIRC(hallo)
        newServer.mName = doc.getElementsByTagName("server_name")[0].firstChild.data
        newServer.mAutoConnect = doc.getElementsByTagName("auto_connect")[0].firstChild.data
        if(len(doc.getElementsByTagName("server_nick"))!=0):
            newServer.mNick = doc.getElementsByTagName("server_nick")[0].firstChild.data
        if(len(doc.getElementsByTagName("server_prefix"))!=0):
            newServer.mPrefix = doc.getElementsByTagName("server_prefix")[0].firstChild.data
        if(len(doc.getElementsByTagName("full_name"))!=0):
            newServer.mFullName = doc.getElementsByTagName("full_name")[0].firstChild.data
        newServer.mServerAddress = doc.getElementsByTagName("server_address")[0].firstChild.data
        newServer.mServerPort = doc.getElementsByTagName("server_port")[0].firstChild.data
        newServer.mNickservPass = doc.getElementsByTagName("nickserv_pass")[0].firstChild.data
        return newServer
        
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
        typeElement.appendChild(doc.createTextNode("irc"))
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        