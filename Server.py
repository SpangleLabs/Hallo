from xml.dom import minidom
from inc.commons import Commons
from threading import Thread,Lock
import socket
import time

#TODO: I would rather deprecate these
import ircbot_chk

from Destination import Channel,User
from PermissionMask import PermissionMask

endl = Commons.mEndLine

class ServerException(Exception):
    pass

class ServerFactory:
    '''
    Server factory, makes servers. Basically looks at xml, finds server type, and passes to appropriate Server object constructor
    '''
    mHallo = None           #Parent Hallo object
    
    def __init__(self,hallo):
        '''
        Constructs the Server Factory, stores Hallo object.
        '''
        self.mHallo = hallo
    
    def newServerFromXml(self,xmlString):
        doc = minidom.parse(xmlString)
        serverType = doc.getElementsByTagName("server_type")[0].firstChild.data
        if(serverType=="irc"):
            return ServerIRC.fromXml(xmlString,self.mHallo)
        else:
            return None

class Server(object):
    '''
    Generic server object. An interface for ServerIRC or ServerSkype or whatever objects.
    '''
    mHallo = None               #The hallo object that created this server
    #Persistent/saved class variables
    mName = None                #server name
    mAutoConnect = True         #Whether to automatically connect to this server when hallo starts
    mChannelList = []           #list of channels on this server (which may or may not be currently active)
    mUserList = []              #Users on this server (not all of which are online)
    mNick = None                #Nickname to use on this server
    mPrefix = None              #Prefix to use with functions on this server
    mFullName = None            #Full name to use on this server
    mPermissionMask = None      #PermissionMask for the server
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server

    def __init__(self,hallo,params):
        '''
        Constructor for server object
        '''
        self.mHallo = hallo
        self.mPermissionMask = PermissionMask()
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
        raise NotImplementedError
        
    def toXml(self):
        '''
        Returns an XML representation of the server object
        '''
        raise NotImplementedError
    
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
        
    def getChannelByName(self,channelName):
        'Returns a Channel object with the specified channel name.'
        for channel in self.mChannelList:
            if(channel.getName()==channelName):
                return channel
        return None
    
    def addChannel(self,channelObject):
        'Adds a channel to the channel list'
        if(self.getChannelByName(channelObject.getName()) is None):
            self.mChannelList.append(channelObject)
            
    def joinchannel(self,channelObject):
        'Joins a specified channel'
        raise NotImplementedError
        
    def getUserByName(self,userName):
        'Returns a User object with the specified user name.'
        for user in self.mUserList:
            if(user.getName()==userName):
                return user
        return None
        
    def rightsCheck(self,rightName):
        'Checks the value of the right with the specified name. Returns boolean'
        rightValue = self.mPermissionMask.getRight(rightName)
        #If PermissionMask contains that right, return it.
        if(rightValue in [True,False]):
            return rightValue
        #Fallback to the parent Hallo's decision.
        return self.mHallo.rightsCheck(rightName)
        
        
class ServerIRC(Server):
    mHallo = None               #The hallo object that created this server
    #Persistent/saved class variables
    mName = None                #server name
    mAutoConnect = True         #Whether to automatically connect to this server when hallo starts
    mChannelList = []           #list of channels on this server (which may or may not be currently active)
    mUserList = []              #Users on this server (not all of which are online)
    mConnection = None          #Connection for the server, socket or whatnot
    mNick = None                #Nickname to use on this server
    mPrefix = None              #Prefix to use with functions on this server
    mFullName = None            #Full name to use on this server
    mPermissionMask = None      #PermissionMask for the server
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server
    #IRC specific variables
    mServerAddress = None       #Address to connect to server
    mServerPort = None          #Port to connect to server
    mNickservPass = None        #Password to identify with nickserv
    mNickservNick = "nickserv"  #Nickserv's nick, None if nickserv does not exist
    mNickservIdentCommand = "STATUS"    #Command to send to nickserv to check if a user is identified
    mNickservIdentResponse = "\b3\b"    #Regex to search for to validate identity in response to IdentCommand
    #IRC specific dynamic variables
    mSocket = None              #Socket to communicate to the server
    mWelcomeMessage = ""        #Server's welcome message when connecting. MOTD and all.
    mCheckChannelUserListLock = None        #Thread lock for checking a channel's user list
    mCheckChannelUserListChannel = None     #Channel to check user list of
    mCheckChannelUserListUserList = None    #User name list of checked channel
    mCheckUsersOnlineLock = None            #Thread lock for checking which users are online
    mCheckUsersOnlineCheckList = None       #List of users' names to check
    mCheckUsersOnlineOnlineList = None      #List of users' names who are online
    
    def __init__(self,hallo,serverName=None,serverUrl=None,serverPort=6667):
        '''
        Constructor for server object
        '''
        self.mHallo = hallo
        self.mPermissionMask = PermissionMask()
        self.mCheckChannelUserListLock = Lock()
        self.mCheckUsersOnlineLock = Lock()
        if(serverName is not None):
            self.mName = serverName
        if(serverUrl is not None):
            self.mServerAddress = serverUrl
            self.mServerPort = serverPort
    
    def connect(self):
        while(True):
            try:
                self.rawConnect()
                break
            except ServerException:
                print("Failed to connect. Waiting 3 seconds before reconnect.")
                time.sleep(3)
                continue
    
    def rawConnect(self):
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
        #Wait for the first message back from the server.
        print(Commons.currentTimestamp() + " waiting for first message from server: " + self.mName)
        firstLine = self.readLineFromSocket()
        self.mWelcomeMessage += firstLine+"\n"
        #Send nick and full name to server
        print(Commons.currentTimestamp() + " sending nick and user info to server: " + self.mName)
        self.send('NICK ' + self.getNick(),None,"raw")
        self.send('USER ' + self.getFullName(),None,"raw")
        #Wait for MOTD to end
        while(True):
            nextWelcomeLine = self.readLineFromSocket()
            self.mWelcomeMessage += nextWelcomeLine+"\n"
            if("376" in nextWelcomeLine or "endofmessage" in nextWelcomeLine.replace(' ','').lower()):
                break
        #Identify with nickserv
        if self.mNickservPass:
            self.send('IDENTIFY ' + self.mNickservPass,self.getUserByName("nickserv"))
        #Join channels
        print(Commons.currentTimestamp() + " joining channels on " + self.mName + ", identifying.")
        #Join relevant channels
        for channel in self.mChannelList:
            if(channel.isAutoJoin()):
                self.joinchannel(channel)
    
    def disconnect(self):
        'Disconnect from the server'
        #TODO: upgrade this when logging is upgraded
        for channel in self.mChannelList:
        #    self.mHallo.base_say('Daisy daisy give me your answer do...',[server,channel])
            if(channel.isInChannel() and channel.getLogging()):
                self.mHallo.base_addlog(Commons.currentTimestamp() + ' '+self.getNick()+' has quit.',[self.mName,channel.getName()])
        #    time.sleep(1)
        if(self.mOpen):
            #self.mHallo.core['server'][self.mName]['socket'].send(('QUIT :Daisy daisy give me your answer do...' + endl).encode('utf-8'))
            self.send('QUIT :Will I dream?',None,"raw")
            self.mSocket.close()
            self.mOpen = False
    
    def run(self):
        '''
        Method to read from stream and process. Will call an internal parsing method or whatnot
        '''
        if(not self.mOpen):
            self.connect()
        while(self.mOpen):
            try:
                nextLine = self.readLineFromSocket()
            except ServerException:
                print("Server disconnected. Reconnecting.")
                self.mOpen = False
                self.connect()
            #Parse line
            Thread(target=self.parseLine, args=(nextLine)).start()
    
    def send(self,data,channel=None,msgType="message"):
        'Sends a message to the server, or a specific channel in the server'
        maxMsgLength = 512  #Maximum length of a message sent to the server
        if(msgType not in ["message","notice","raw"]):
            msgType = "message"
        #If it's raw data, just send it.
        if(msgType=="raw"):
            for dataLine in data.split("\n"):
                self.sendRaw(dataLine)
            return
        #Get message type
        if(msgType=="notice"):
            msgTypeName = "NOTICE"
        else:
            msgTypeName = "PRIVMSG"
        #Get channel or user name
        destinationName = channel.getName()
        #Get max line length
        maxLineLength = maxMsgLength-len(msgTypeName+' '+destinationName+' '+endl)
        #Split and send
        for dataLine in data.split("\n"):
            dataLineSplit = Commons.chunkStringDot(dataLine,maxLineLength)
            for dataLineLine in dataLineSplit:
                self.sendRaw(msgTypeName+' '+destinationName+' '+dataLineLine)
    
    def joinchannel(self,channelObject):
        'Joins a specified channel'
        if(channelObject not in self.mChannelList):
            self.addChannel(channelObject)
        if(channelObject.getPassword() is None):
            self.send('JOIN ' + channelObject.getName(),None,"raw")
        else:
            self.send('JOIN ' + channelObject.getName() + ' ' + channelObject.getPassword(),None,"raw")

    def sendRaw(self,data):
        'Sends raw data to the server'
        self.mSocket.send((data+endl).encode("utf-8"))
                
    def parseLine(self,newLine):
        'Parses a line from the IRC server'
        #Cleaning up carriage returns
        newLine = newLine.replace("\r","")
        #TODO: add stuff about time last ping was seen, for reconnection checking
        if(len(newLine)<5 or (newLine[0] != ":" and newLine[0:4] != "PING")):
            self.parseLineUnhandled(newLine)
            self.parseLineRaw(newLine,"unhandled")
        elif(newLine.split()[0] == "PING"):
            self.parseLinePing(newLine)
            self.parseLineRaw(newLine,"ping")
        elif(newLine.split()[0] == "PRIVMSG"):
            self.parseLineMessage(newLine)
            self.parseLineRaw(newLine,"message")
        elif(newLine.split()[1] == "JOIN"):
            self.parseLineJoin(newLine)
            self.parseLineRaw(newLine,"join")
        elif(newLine.split()[1] == "PART"):
            self.parseLinePart(newLine)
            self.parseLineRaw(newLine,"part")
        elif(newLine.split()[1] == "QUIT"):
            self.parseLineQuit(newLine)
            self.parseLineRaw(newLine,"quit")
        elif(newLine.split()[1] == "MODE"):
            self.parseLineMode(newLine)
            self.parseLineRaw(newLine,"mode")
        elif(newLine.split()[1] == "NOTICE"):
            self.parseLineNotice(newLine)
            self.parseLineRaw(newLine,"notice")
        elif(newLine.split()[1] == "NICK"):
            self.parseLineNick(newLine)
            self.parseLineRaw(newLine,"nick")
        elif(newLine.split()[1] == "INVITE"):
            self.parseLineInvite(newLine)
            self.parseLineRaw(newLine,"invite")
        elif(newLine.split()[1] == "KICK"):
            self.parseLineKick(newLine)
            self.parseLineRaw(newLine,"kick")
        elif(len(newLine.split()[1])==3 and newLine.split()[1].isdigit()):
            self.parseLineNumeric(newLine)
            self.parseLineRaw(newLine,"numeric")
        else:
            self.parseLineUnhandled(newLine)
            self.parseLineRaw(newLine,"unhandled")
        return
    
    def parseLinePing(self,pingLine):
        'Parses a PING message from the server'
        print(Commons.currentTimestamp() + "["+self.mName+"] PING")
        pingNumber = pingLine.split()[1]
        self.send("PONG "+pingNumber,None,"raw")
        
    def parseLineMessage(self,messageLine):
        'Parses a PRIVMSG message from the server'
        #Parse out the message text
        messageText = ':'.join(messageLine.split(':')[2:])
        #Parse out the message sender
        messageSenderName = messageLine.split('!')[0].replace(':', '')
        #Parse out where the message went to (e.g. channel or private message to Hallo)
        messageDestinationName = messageLine.split()[2].lower()
        #Test for CTCP message, hand to CTCP parser if so.
        messageCtcpBool = messageText.split(':')[2][0] == '\x01'
        if(messageCtcpBool):
            self.parseLineCtcp(messageLine)
            return
        #Test for private message or public message.
        messagePrivateBool = messageDestinationName.lower() == self.getNick().lower()
        messagePublicBool = not messagePrivateBool
        #Get relevant objects.
        messageSender = self.getUserByName(messageSenderName)
        messageDestination = messageSender
        if(messagePublicBool):
            messageChannel = self.getChannelByName(messageDestinationName)
            messageDestination = messageChannel
        #Print message to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + messageDestinationName + ' <' + messageSenderName + '> ' + messageText)
        #Log the message
        if(messagePrivateBool):
            if(messageSender is None or messageSender.getLogging()):
                self.base_addlog(Commons.currentTimestamp() + ' <' + messageSenderName + '> ' + messageText, [self.mName,messageDestinationName])
        elif(messageChannel is None or messageChannel.getLogging()):
            self.base_addlog(Commons.currentTimestamp() + ' <' + messageSenderName + '> ' + messageText, [self.mName,messageDestinationName])
        #TODO: Figure out if the message is a command.
        ##If it's a privmsg it's a command
        ##If it is public and starts with channel's prefix, it's a command
        ##If channel prefix is name, check that there's a comma or colon?
        #If public message, return stuff to channel, else to sender
        #TODO: pass to passive function checker
        
    def parseLineCtcp(self,ctcpLine):
        'Parses a CTCP message from the server'
        #Parse out the ctcp message text
        messageText = ':'.join(ctcpLine.split(':')[2:])[1:-1]
        #Parse out the message sender
        messageSenderName = ctcpLine.split('!')[0].replace(':', '')
        #Parse out where the message went to (e.g. channel or private message to Hallo)
        messageDestinationName = ctcpLine.split()[2].lower()
        #Parse out the CTCP command and arguments
        messageCtcpCommand = messageText.split()[0]
        messageCtcpArguments = ' '.join(messageText.split()[1:])
        #Test for private message or public message
        messagePrivateBool = messageDestinationName.lower() == self.getNick().lower()
        messagePublicBool = not messagePrivateBool
        #Get relevant objects.
        if(messagePublicBool):
            messageChannel = self.getChannelByName(messageDestinationName)
        messageSender = self.getUserByName(messageSenderName)
        #Print message to console
        if(messageCtcpCommand.lower()=="action"):
            consoleLine = Commons.currentTimestamp() + ' [' + self.mName + '] ' + messageDestinationName
            consoleLine += '**' + messageSenderName + ' ' + messageCtcpArguments + '**'
        else:
            consoleLine = Commons.currentTimestamp() + ' [' + self.mName + '] ' + messageDestinationName
            consoleLine += ' <' + messageSenderName + ' (CTCP)> ' + messageText
        print(consoleLine)
        #Log the message
        if(messageCtcpCommand.lower()=="action"):
            logLine = Commons.currentTimestamp()
            logLine += '**' + messageSenderName + ' ' + messageCtcpArguments + '**'
        else:
            logLine = Commons.currentTimestamp()
            logLine += ' <' + messageSenderName + ' (CTCP)> ' + messageText
        if(messagePrivateBool):
            if(messageSender is None or messageSender.getLogging()):
                self.base_addlog(logLine, [self.mName,messageDestinationName])
        elif(messageChannel is None or messageChannel.getLogging()):
            self.base_addlog(logLine, [self.mName,messageDestinationName])
        #Reply to certain types of CTCP command
        if(messageCtcpCommand.lower()=='version'):
            self.send("\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01",messageSender,"notice")
        elif(messageCtcpCommand.lower()=='time'):
            self.send("\x01TIME Fribsday 15 Nov 2024 " + str(time.gmtime()[3]+100).rjust(2,'0') + ":" + str(time.gmtime()[4]+20).rjust(2,'0') + ":" + str(time.gmtime()[5]).rjust(2,'0') + "GMT\x01",messageSender,"notice")
        elif(messageCtcpCommand.lower()=='ping'):
            self.send('\x01PING ' + messageCtcpArguments + '\x01',messageSender,"notice")
        elif(messageCtcpCommand.lower()=='userinfo'):
            self.send("\x01Hello, I'm hallo, I'm a robot who does a few different things, mostly roll numbers and choose things, occassionally giving my input on who is the best pony. dr-spangle built me, if you have any questions he tends to be better at replying than I.\x01",messageSender,"notice")
        elif(messageCtcpCommand.lower()=='clientinfo'):
            self.send('\x01VERSION, NOTICE, TIME, USERINFO and obviously CLIENTINFO are supported.\x01',messageSender,"notice")

        
    def parseLineJoin(self,joinLine):
        'Parses a JOIN message from the server'
        #Parse out the channel and client from the JOIN data
        joinChannelName = ':'.join(joinLine.split(':')[2:]).lower()
        joinClientName = joinLine.split('!')[0][1:]
        #Get relevant objects
        joinChannel = self.getChannelByName(joinChannelName)
        joinClient = self.getUserByName(joinClientName) #TODO: create if they don't exist
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + joinClient.getName() + ' joined ' + joinChannel.getName())
        #If channel does logging, log
        #TODO: replace with newer logging
        if(joinChannel.getLogging()):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + joinClient.getName() + ' joined ' + joinChannel.getName(),[self.mName,joinChannel.getName()])
        #Apply automatic flags as required
        if('auto_list' in self.mHallo.conf['server'][self.mName]['channel'][joinChannel.getName()]):
            for entry in self.mHallo.conf['server'][self.mName]['channel'][joinChannel.getName()]['auto_list']:
                if(joinClient.getName().lower()==entry['user']):
                    for _ in range(7):
                        #TODO: Need a new way to check if users are registered
                        #TODO: http://stackoverflow.com/questions/1682920/determine-if-a-user-is-idented-on-irc
                        if(ircbot_chk.ircbot_chk.chk_userregistered(self.mHallo,self.mName,joinClient.getName())):
                            self.send('MODE ' + joinChannel.getName() + ' ' + entry['flag'] + ' ' + joinClient.getName(),None,"raw")
                            break
                        time.sleep(5)
        #If hallo has joined a channel, get the user list and apply automatic flags as required
        if(joinClient.getName().lower() == self.getNick().lower()):
            joinChannel.setInChannel(True)
            self.checkChannelUserList(joinChannel)
            if('auto_list' in self.mHallo.conf['server'][self.mName]['channel'][joinChannel.getName()]):
                for entry in self.mHallo.conf['server'][self.mName]['channel'][joinChannel.getName()]['auto_list']:
                    if(entry['user'] in joinChannel.getUserList()):
                        for _ in range(7):
                            #TODO: Replace this with a new way to check users are registered
                            if(ircbot_chk.ircbot_chk.chk_userregistered(self,self.mName,entry['user'])):
                                self.send('MODE ' + joinChannel.getName() + ' ' + entry['flag'] + ' ' + entry['user'],None,"raw")
                                break
                            time.sleep(5)
        else:
            #If it was not hallo joining a channel, add nick to user list
            joinChannel.addUser(joinClient)
        
    def parseLinePart(self,partLine):
        'Parses a PART message from the server'
        #Parse out channel, client and message from PART data
        partChannelName = partLine.split()[2]
        partClientName = partLine.split('!')[0][1:]
        partMessage = ':'.join(partLine.split(':')[2:])
        #Get channel and user object
        partChannel = self.getChannelByName(partChannelName)
        partClient = self.getUserByName(partClientName)
        #Print message to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + partClient.getName() + ' left ' + partChannel.getName() + ' (' + partMessage + ')')
        #If channel does logging, log the PART data
        #TODO: replace with newer logging
        if(partChannel.getLogging()):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + partClient.getName() + ' left ' + partChannel.getName() + ' (' + partMessage + ')',[self.mName,partChannel.getName()])
        #Remove user from channel's user list
        partChannel.removeUser(partClient)
        #Try to work out if the user is still on the server
        #TODO: this needs to be nicer
        userStillOnServer = False
        for channel_server in self.mChannelList:
            if(partClient in channel_server.getUserList()):
                userStillOnServer = True
        if(not userStillOnServer):
            if(partClient.getName().lower() in self.mHallo.core['server'][self.mName]['auth_op']):
                self.mHallo.core['server'][self.mHallo.mName]['auth_op'].remove(partClient.getName().lower())
            if(partClient.getName().lower() in self.mHallo.core['server'][self.mName]['auth_god']):
                self.mHallo.core['server'][self.mName]['auth_god'].remove(partClient.getName().lower())
    
    def parseLineQuit(self,quitLine):
        'Parses a QUIT message from the server'
        #Parse client and message
        quitClientName = quitLine.split('!')[0][1:]
        quitMessage = ':'.join(quitLine.split(':')[2:])
        #Get client object
        quitClient = self.getUserByName(quitClientName)
        #Print message to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + quitClient.getName() + ' quit: ' + quitMessage)
        #Log to all channels on server
        for channel in self.mChannelList:
            if(quitClient.isInChannel() and quitClient.getLogging() and quitClient in self.mHallo.core['server'][self.mName]['channel'][channel.getName()]['user_list']):
                self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + quitClient.getName() + ' quit: ' + quitMessage,[self.mName,channel.getName()])
        #Remove user from user list on all channels
        for channel in self.mChannelList:
            channel.removeUser(quitClient)
        #Remove auth stuff from user
        if('auth_op' in self.mHallo.core['server'][self.mName] and quitClient.getName().lower() in self.mHallo.core['server'][self.mName]['auth_op']):
            self.mHallo.core['server'][self.mName]['auth_op'].remove(quitClient.getName().lower())
        if('auth_god' in self.mHallo.core['server'][self.mName] and quitClient.getName().lower() in self.mHallo.core['server'][self.mName]['auth_god']):
            self.mHallo.core['server'][self.mName]['auth_god'].remove(quitClient.getName().lower())
        
    def parseLineMode(self,modeLine):
        'Parses a MODE message from the server'
        #Parsing out MODE data
        modeChannelName = modeLine.split()[2].lower()
        modeClientName = modeLine.split('!')[0][1:]
        modeMode = modeLine.split()[3]
        if(len(modeLine.split())>=4):
            modeArgs = ' '.join(modeLine.split()[4:])
        else:
            modeArgs = ''
        #Get client and channel objects
        modeChannel = self.getChannelByName(modeChannelName)
        modeClient = self.getUserByName(modeClientName)
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + modeClient.getName() + ' set ' + modeMode + ' ' + modeArgs + ' on ' + modeChannel.getName())
        #Logging, if enabled
        if(modeChannel.getLogging()):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + modeClient.getName() + ' set ' + modeMode + ' ' + modeArgs + ' on ' + modeChannel.getName(),[self.mName,modeChannel.getName()])
        #If a channel password has been set, store it
        if(modeMode=='-k'):
            modeChannel.setPassword(None)
        elif(modeMode=='+k'):
            modeChannel.setPassword(modeArgs)
    
    def parseLineNotice(self,noticeLine):
        'Parses a NOTICE message from the server'
        #Parsing out NOTICE data
        noticeChannelName = noticeLine.split()[2]
        noticeClientName = noticeLine.split('!')[0][1:]
        noticeMessage = ':'.join(noticeLine.split(':')[2:])
        #Get client and channel objects
        noticeChannel = self.getChannelByName(noticeChannelName)
        noticeClient = self.getUserByName(noticeClientName)
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + noticeChannel.getName() + ' Notice from ' + noticeClient.getName() + ': ' + noticeMessage)
        #Logging, if enabled
        if(noticeChannel.getLogging()):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + noticeChannel.getName() + ' notice from ' + noticeClient.getName() + ': ' + noticeMessage,[self.mName,noticeChannel.getName()])
        #TODO: DEPRICATED. I am sure this is not required.
        if(self.mHallo.core['server'][self.mName]['connected'] == False):
            self.mHallo.core['server'][self.mName]['connected'] = True
            print(Commons.currentTimestamp() + ' [' + self.mName + "] ok we're connected now.")
        #Checking for end of MOTD.
        if('endofmessage' in noticeMessage.replace(' ','').lower() and self.mHallo.core['server'][self.mName]['motdend'] == False):
            self.mHallo.core['server'][self.mName]['motdend'] = True
        #Checking if user is registered
        #TODO: deprecate this. Use locks, and use STATUS or ACC commands to nickserv
        if(any(nickservmsg in noticeMessage.replace(' ','').lower() for nickservmsg in self.mHallo.conf['nickserv']['online']) and noticeClient.getName().lower()=='nickserv' and self.mHallo.core['server'][self.mName]['check']['userregistered'] == False):
            self.mHallo.core['server'][self.mName]['check']['userregistered'] = True
        if(any(nickservmsg in noticeMessage.replace(' ','').lower() for nickservmsg in self.mHallo.conf['nickserv']['registered']) and noticeClient.getName().lower()=='nickserv' and self.mHallo.core['server'][self.mName]['check']['nickregistered'] == False):
            self.mHallo.core['server'][self.mName]['check']['nickregistered'] = True
        
    def parseLineNick(self,nickLine):
        'Parses a NICK message from the server'
        #Parse out NICK change data
        nickClientName = nickLine.split('!')[0][1:]
        if(nickLine.count(':')>1):
            nickNewNick = nickLine.split(':')[2]
        else:
            nickNewNick = nickLine.split()[2]
        #Get user object
        nickClient = self.getUserByName(nickClientName)
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] Nick change: ' + nickClient.getName() + ' -> ' + nickNewNick)
        #Log, if logging
        for channel in self.mChannelList:
            if(channel.isInChannel() and channel.getLogging() and channel.isUserInChannel(nickClient)):
                self.mHallo.base_addlog(Commons.currentTimestamp() + ' Nick change: ' + nickClient.getName() + ' -> ' + nickNewNick,[self.mName,channel.getName()])
        #If it was the bots nick that just changed, update that.
        if(nickClient.getName() == self.getNick()):
            self.mNick = nickNewNick
        #Update auth_op lists
        if('auth_op' in self.mHallo.core['server'][self.mName] and nickClient.getName().lower() in self.mHallo.core['server'][self.mName]['auth_op']):
            self.mHallo.core['server'][self.mName]['auth_op'].remove(nickClient.getName().lower())
            self.mHallo.core['server'][self.mName]['auth_op'].append(nickNewNick.lower())
        #Update auth_god lists
        if('auth_god' in self.mHallo.core['server'][self.mName] and nickClient.getName().lower() in self.mHallo.core['server'][self.mName]['auth_god']):
            self.mHallo.core['server'][self.mName]['auth_god'].remove(nickClient.getName().lower())
            self.mHallo.core['server'][self.mName]['auth_god'].append(nickNewNick.lower())
        #Check whether this verifies anything that means automatic flags need to be applied
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if('auto_list' in self.mHallo.conf['server'][self.mName]['channel'][channel]):
                for entry in self.mHallo.conf['server'][self.mName]['channel'][channel]['auto_list']:
                    if(nickNewNick == entry['user']):
                        for _ in range(7):
                            if(ircbot_chk.ircbot_chk.chk_userregistered(self.mHallo,self.mName,nickNewNick)):
                                self.send('MODE ' + channel + ' ' + entry['flag'] + ' ' + nickNewNick,None,"raw")
                                break
                            time.sleep(5)
        #Update name for user object
        nickClient.setName(nickNewNick)
        
    def parseLineInvite(self,inviteLine):
        'Parses an INVITE message from the server'
        #Parse out INVITE data
        inviteClientName = inviteLine.split('!')[0][1:]
        inviteChannelName = ':'.join(inviteLine.split(':')[2:])
        #Get destination objects
        inviteClient = self.getUserByName(inviteClientName)
        inviteChannel = self.getChannelByName(inviteChannelName)
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] invite to ' + inviteChannel.getName() + ' from ' + inviteClient.getName())
        #Logging, if applicable
        if(inviteChannel.getName() in self.mHallo.conf['server'][self.mName]['channel'] and inviteChannel.getLogging()):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' invite to ' + inviteChannel.getName() + ' from ' + inviteClient.getName(),[self.mName,'@SERVER'])
        #Check if they are an op, then join the channel.
        #TODO: change this logic, when channel object exists
        if(inviteClient.rightsCheck("invite_channel",inviteChannel)):
            self.joinChannel(inviteChannel)
        
    def parseLineKick(self,kickLine):
        'Parses a KICK message from the server'
        #Parse out KICK data
        kickChannelName = kickLine.split()[2]
        kickClientName = kickLine.split()[3]
        kickMessage = ':'.join(kickLine.split(':')[4:])
        #GetObjects
        kickChannel = self.getChannelByName(kickChannelName)
        kickClient = self.getUserByName(kickClientName)
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + kickClient.getName() + ' was kicked from ' + kickChannel.getName() + ': ' + kickMessage)
        #Log, if applicable
        if(kickChannel.getLogging()):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + kickClient.getName() + ' was kicked from ' + kickChannel.getName() + ': ' + kickMessage,[self.mName,kickChannel.getName()])
        #Remove kicked user from userlist
        kickChannel.removeUser(kickClient)
        #If it was the bot who was kicked, set "in channel" status to False
        if(kickClient.getName() == self.getNick()):
            kickChannel.setInChannel(False)

    def parseLineNumeric(self,numericLine):
        'Parses a numeric message from the server'
        #Parse out numeric line data
        numericCode = numericLine.split()[1]
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] Server info: ' + numericLine)
        #TODO: add logging?
        #Check for end of MOTD
        #TODO: deprecate
        if(numericCode == "376"):
            self.mHallo.core['server'][self.mName]['motdend'] = True
        #Check for ISON response, telling you which users are online
        elif(numericCode == "303"):
            #Parse out data
            usersOnline = ':'.join(numericLine.split(':')[2:])
            usersOnlineList = usersOnline.split()
            #Check if users are being checked
            if(all([usersOnlineList in self.mCheckUsersOnlineCheckList])):
                    self.mCheckUsersOnlineOnlineList = usersOnlineList
        #Check for NAMES request reply, telling you who is in a channel.
        elif(numericCode == "353"):
            #Parse out data
            channelName = numericLine.split(':')[1].split()[-1].lower()
            channelUserList = ':'.join(numericLine.split(':')[2:])
            #Get channel object
            channelObject = self.getChannelByName(channelName)
            #Check channel is being checked
            if(channelObject == self.mCheckChannelUserListChannel):
                #Set user list
                self.mCheckChannelUserListUserList = channelUserList.split()

    def parseLineUnhandled(self,unhandledLine):
        'Parses an unhandled message from the server'
        #Print it to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] Unhandled data: ' + unhandledLine)
        
    def parseLineRaw(self,rawLine,lineType):
        'Handed all raw data, along with the type of message'

    def readLineFromSocket(self):
        'Private method to read a line from the IRC socket.'
        nextLine = b""
        while(self.mOpen):
            try:
                nextByte = self.mSocket.recv(1)
            except:
                #Raise an exception, to reconnect.
                raise ServerException
            nextLine = nextLine + nextByte
            if(nextLine.endswith(endl.encode())):
                return self.decodeLine(nextLine[:-len(endl)])

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
    
    def checkChannelUserList(self,channelObject):
        'Checks and updates the user list of a specified channel'
        #get lock
        self.mCheckChannelUserListLock.acquire()
        self.mCheckChannelUserListChannel = channelObject
        self.mCheckChannelUserListUserList = None
        #send request
        self.send("NAMES "+channelObject.getName(),None,"raw")
        #loop for 5 seconds
        for _ in range(10):
            #if reply is here
            if(self.mCheckChannelUserListUserList is not None):
                #use response
                userObjectList = set()
                for userName in self.mCheckChannelUserListUserList:
                    #Strip flags from user name
                    while(userName[0] in ['~','&','@','%','+']):
                        userName = userName[1:]
                    userObject = self.getUserByName(userName)
                    userObjectList.add(userObject)
                channelObject.setUserList(userObjectList)
                #release lock
                self.mCheckChannelUserListChannel = None
                self.mCheckChannelUserListUserList = None
                self.mCheckChannelUserListLock.release()
                #return
                return
            #sleep 0.5seconds
            time.sleep(0.5)
        #release lock
        self.mCheckChannelUserListChannel = None
        self.mCheckChannelUserListUserList = None
        self.mCheckChannelUserListLock.release()
        #return
        return
    
    def checkUsersOnline(self,checkUserList):
        'Checks a list of users to see which are online, returns a list of online users'
        #get lock
        self.mCheckChannelUserListLock.aquire()
        self.mCheckUsersOnlineCheckList = checkUserList
        self.mCheckUsersOnlineOnlineList = None
        #send request
        self.send("ISON " + " ".join(checkUserList),None,"raw")
        #loop for 5 seconds
        for _ in range(10):
            #if reply is here
            if(self.mCheckUsersOnlineOnlineList is not None):
                #use response
                for userName in self.mCheckUsersOnlineCheckList:
                    userObject = self.getUserByName(userName)
                    if(userName in self.mCheckUsersOnlineOnlineList):
                        userObject.setOnline(True)
                    else:
                        userObject.setOnline(False)
                #release lock
                response = self.mCheckUsersOnlineOnlineList
                self.mCheckUsersOnlineCheckList = None
                self.mCheckUsersOnlineOnlineList = None
                self.mCheckUsersOnlineLock.release()
                #return response
                return response
            #sleep 0.5 seconds
            time.sleep(0.5)
        #release lock
        self.mCheckUsersOnlineCheckList = None
        self.mCheckUsersOnlineOnlineList = None
        self.mCheckUsersOnlineLock.release()
        #return empty list
        return []

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
        if(len(doc.getElementsByTagName("nickserv"))==0):
            newServer.mNickservNick = None
            newServer.mNickservPass = None
            newServer.mNickservIdentCommand = None
            newServer.mNickservIdentResponse = None
        else:
            nickservElement = doc.getElementsByTagName("nickserv")[0]
            newServer.mNickservNick = nickservElement.getElementsByTagName("nick")[0].firstChild.data
            newServer.mNickservIdentCommand = nickservElement.getElementsByTagName("identity_command")[0].firstChild.data
            newServer.mNickservIdentResponse = nickservElement.getElementsByTagName("identity_response")[0].firstChild.data
            if(len(nickservElement.getElementsByTagName("password"))!=0):
                newServer.mNickservPass = nickservElement.getElementsByTagName("password")[0].firstChild.data
        #Load channels
        channelListXml = doc.getElementsByTagName("channel_list")[0]
        for channelXml in channelListXml.getElementsByTagName("channel"):
            channelObject = Channel.fromXml(channelXml.toxml(),newServer)
            newServer.addChannel(channelObject)
        if(len(doc.getElementsByTagName("permission_mask"))!=0):
            newServer.mPermissionMask = PermissionMask.fromXml(doc.getElementsByTagName("permission_mask")[0].toxml())
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
        #create channel list
        channelListElement = doc.createElement("channel_list")
        for channelItem in self.mChannelList:
            channelElement = minidom.parse(channelItem.toXml()).firstChild
            channelListElement.appendChild(channelElement)
        root.appendChild(channelListElement)
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
        #Create nickserv element
        if(self.mNickservNick is not None):
            nickservElement = doc.createElement("nickserv")
            #Nickserv nick element
            nickservNickElement = doc.createElement("nick")
            nickservNickElement.appendChild(doc.createTextNode(self.mNickservNick))
            nickservElement.appendChild(nickservNickElement)
            #Nickserv password element
            if(self.mNickservPass is not None):
                nickservPassElement = doc.createElement("password")
                nickservPassElement.appendChild(doc.createTextNode(self.mNickservPass))
                nickservElement.appendChild(nickservPassElement)
            #Nickserv identity check command element
            nickservIdentCommandElement = doc.createElement("identity_command")
            nickservIdentCommandElement.appendChild(doc.createTextNode(self.mNickservIdentCommand))
            nickservElement.appendChild(nickservIdentCommandElement)
            #Nickserv identity check response element
            nickservIdentResponseElement = doc.createElement("identity_response")
            nickservIdentResponseElement.appendChild(doc.createTextNode(self.mNickservIdentResponse))
            nickservElement.appendChild(nickservIdentResponseElement)
            #Add nickserv element to document
            root.appendChild(nickservElement)
        #create permission_mask element
        if(not self.mPermissionMask.isEmpty()):
            permissionMaskElement = minidom.parse(self.mPermissionMask.toXml()).firstChild
            root.appendChild(permissionMaskElement)
        #output XML string
        return doc.toxml()

        