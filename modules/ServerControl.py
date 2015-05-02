
from Function import Function
from threading import Thread
import re
from inc.commons import Commons
from Server import ServerIRC

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

class Disconnect(Function):
    '''
    Disconnects from a Server
    '''
    #Name for use in help listing
    mHelpName = "disconnect"
    #Names which can be used to address the Function
    mNames = set(["disconnect","quit"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Disconnects from a server."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        serverObject = userObject.getServer()
        halloObject = serverObject.getHallo()
        if(line.strip()!=""):
            serverObject = halloObject.getServerByName(line)
        if(serverObject is None):
            return "Invalid server."
        serverObject.setAutoConnect(False)
        serverObject.disconnect()
        return "Disconnected from server: "+serverObject.getName()+"."

class Connect(Function):
    '''
    Connects to a Server
    '''
    #Name for use in help listing
    mHelpName = "connect"
    #Names which can be used to address the Function
    mNames = set(["connect","new server"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Connects to an existing or a new server."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        'Runs the function'
        currentServer = userObject.getServer()
        halloObject = currentServer.getHallo()
        #Try and see if it's a server we already know
        existingServer = halloObject.getServerByName(line)
        if(existingServer is not None):
            return self.connectToKnownServer(existingServer)
        #Try to find what protocol is specififed, or use whatever protocol the user is using.
        lineSplit = line.split()
        validProtocols = ["irc"]
        if(any([prot in [arg.lower() for arg in lineSplit] for prot in validProtocols])):
            for protocol in validProtocols:
                if(protocol in [arg.lower() for arg in lineSplit]):
                    serverProtocol = protocol
                    protocolRegex = re.compile("\s"+protocol+"\s",re.IGNORECASE)
                    line = protocolRegex.sub(" ",line)
                    break
        else:
            serverProtocol = currentServer.getType()
        #Go through protocols branching to whatever function to handle that protocol
        if(serverProtocol=="irc"):
            return self.connectToNewServerIrc(line,userObject,destinationObject)
        #Add in ELIF statements here, to make user Connect Function support other protocols
        else:
            return "Unrecognised server protocol"
            
    def connectToKnownServer(self,serverObject):
        'Connects to a known server.'
        serverObject.setAutoConnect(True)
        if(serverObject.isConnected()):
            return "Already connected to that server"
        Thread(target=serverObject.run).start()
        return "Connected to server: "+serverObject.getName()+"."
    
    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue
    
    def connectToNewServerIrc(self,line,userObject,destinationObject):
        'Processes arguments in order to connect to a new IRC server'
        #Get some handy objects
        currentServer = userObject.getServer()
        halloObject = currentServer.getHallo()
        #Set all variables to none as default
        serverAddress,serverPort = None,None
        serverName = None
        #Find the URL, if specified
        urlRegex = re.compile("(^|\s)(irc://)?(([a-z.]+\.[a-z]+)(:([0-9]+))?)(\s|$)",re.IGNORECASE)
        urlSearch = urlRegex.search(line)
        if(urlSearch is not None):
            line = line.replace(urlSearch.group(0)," ")
            serverAddress = urlSearch.group(4).lower()
            serverPort = int(urlSearch.group(6))
        #Find the serverAddress, if specified with equals notation
        serverAddress = self.findParameter("server_address",line) or serverAddress
        #Find the serverPort, if specified with equals notation
        serverPortParam = self.findParameter("server_port",line)
        if(serverPortParam is not None):
            try:
                serverPort = int(serverPortParam)
            except ValueError:
                return "Invalid port number."
        #Check serverAddress and serverPort are set
        if(serverAddress is None):
            return "No server address specified."
        if(serverPort is None):
            serverPort = currentServer.getServerPort()
        #Get server name
        serverName = self.findParameter("name",line) or serverName
        serverName = self.findParameter("server_name",line) or serverName
        #if server name is null, get it from serverAddress
        if(serverName is None):
            serverName = Commons.getDomainName(serverAddress)
        #Get other parameters, if set.
        autoConnect = Commons.stringToBool(self.findParameter("auto_connect",line)) or True
        serverNick = self.findParameter("server_nick",line) or self.findParameter("nick",line)
        serverPrefix = self.findParameter("server_prefix",line) or self.findParameter("prefix",line)
        fullName = self.findParameter("full_name",line)
        nickservNick = "nickserv"
        nickservIdentityCommand = "status"
        nickservIdentityResponse = "^status [^ ]+ 3$"
        nickservPassword = None
        if(currentServer.getType()=="irc"):
            nickservNick = currentServer.getNickservNick()
            nickservIdentityCommand = currentServer.getNickservIdentityCommand()
            nickservIdentityResponse = currentServer.getNickservIdentityResponse()
            nickservPassword = currentServer.getNickservPassword()
        nickservNick = self.findParameter("nickserv_nick",line) or nickservNick
        nickservIdentityCommand = self.findParameter("nickserv_identity_command",line) or nickservIdentityCommand
        nickservIdentityResponse = self.findParameter("nickserv_identity_response",line) or nickservIdentityResponse
        nickservPassword = self.findParameter("nickserv_password",line) or nickservPassword
        #Create this serverIRC object
        newServerObject = ServerIRC(halloObject,serverName,serverAddress,serverPort)
        newServerObject.setAutoConnect(autoConnect)
        newServerObject.setNick(serverNick)
        newServerObject.setPrefix(serverPrefix)
        newServerObject.setFullName(fullName)
        newServerObject.setNickservNick(nickservNick)
        newServerObject.setNickservIdentityCommand(nickservIdentityCommand)
        newServerObject.setNickservIdentityResponse(nickservIdentityResponse)
        newServerObject.getNickservPass(nickservPassword)
        #Add the new object to Hallo's list
        halloObject.addServer(newServerObject)
        #Connect to the new server object.
        Thread(target=newServerObject.run).start()
        return "Connected to new IRC server: "+newServerObject.getName()+"."
        
        
class Say(Function):
    '''
    Function to enable speaking through hallo
    '''
    #Name for use in help listing
    mHelpName = "say"
    #Names which can be used to address the Function
    mNames = set(["say","message","msg"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Say a message into a channel or server/channel pair (in the format \"{server,channel}\"). Format: say <channel> <message>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        'Say a message into a channel or server/channel pair (in the format "{server,channel}"). Format: say <channel> <message>'
        halloObject = userObject.getServer().getHallo()
        destinationString = line.split()[0]
        message = line[len(destinationString):].strip()
        #Setting up variable
        destinationServerString,destinationChannelString = None,None
        #Looping possible server-channel separators, seeing if any are in use.
        destinationSeparators = ["->",">",",",".","/",":"]
        for destinationSeparator in destinationSeparators:
            if(destinationString.count(destinationSeparator)!=0):
                destinationServerString = destinationString.split(destinationSeparator)[0]
                destinationChannelString = destinationString.split(destinationSeparator)[1]
                break
        #If no separator, use current server and input as channel
        if(destinationServerString is None):
            destinationServerString = userObject.getServer().getName()
            destinationChannelString = destinationString
        #Try to find server object
        destinationServerObject = halloObject.getServerByName(destinationServerString)
        if(destinationServerObject is None):
            return "Invalid server name."
        #Try to find channel object
        channelObject = destinationServerObject.getChannelByName(destinationChannelString)
        if(channelObject.isInChannel() is False):
            return "I am not in that channel."
        #Send the message
        destinationServerObject.send(message,channelObject)
        return "Message sent."