from xml.dom import minidom
from inc.commons import Commons
from threading import Thread
import socket
import time

#TODO: I would rather depricate these
import ircbot_chk
import hallobase_ctrl

#TODO: investigate this
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
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server

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
        
    def getChannelByName(self,channelName):
        'Returns a Channel object with the specified channel name.'
        for channel in self.mChannelList:
            if(channel.getName()==channelName):
                return channel
        return None
        
    def getUserByName(self,userName):
        'Returns a User object with the specified user name.'
        for user in self.mUserList:
            if(user.getName()==userName):
                return user
        return None
        
        
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
    #Dynamic/unsaved class variables
    mOpen = False               #Whether or not to keep reading from server
    #IRC specific variables
    mServerAddress = None       #Address to connect to server
    mServerPort = None          #Port to connect to server
    mNickservPass = None        #Password to identify with nickserv
    #IRC specific dynamic variables
    mSocket = None              #Socket to communicate to the server
    mWelcomeMessage = ""        #Server's welcome message when connecting. MOTD and all.
    
    def __init__(self,hallo,serverName=None,serverUrl=None,serverPort=6667):
        '''
        Constructor for server object
        '''
        self.mHallo = hallo
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
            #TODO: remove line
            self.mHallo.core['server'][self.mName]['open'] = False
        #Wait for the first message back from the server.
        print(Commons.currentTimestamp() + " waiting for first message from server: " + self.mName)
        firstLine = self.readLineFromSocket()  #TODO: make this timeout somehow.
        self.mWelcomeMessage += firstLine+"\n"
        #Send nick and full name to server
        print(Commons.currentTimestamp() + " sending nick and user info to server: " + self.mName)
        self.sendRaw('NICK ' + self.getNick())
        self.sendRaw('USER ' + self.getFullName())
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
                    self.sendRaw('JOIN ' + channel)
                else:
                    self.sendRaw('JOIN ' + channel + ' ' + self.mHallo.conf['server'][self.mName]['channel'][channel]['pass'])
    
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
            self.sendRaw('QUIT :Will I dream?')
            self.mSocket.close()
            self.mOpen = False
            #Remove self from Hallo's server list
            self.mHallo.removeServer(self)
            
    
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
        #TODO: get channel address
        destinationName = channel.getAddress()
        #Get max line length
        maxLineLength = maxMsgLength-len(msgTypeName+' '+destinationName+' '+endl)
        #Split and send
        for dataLine in data.split("\n"):
            dataLineSplit = Commons.chunkStringDot(dataLine,maxLineLength)
            for dataLineLine in dataLineSplit:
                self.sendRaw(msgTypeName+' '+destinationName+' '+dataLineLine)

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
        self.sendRaw("PONG "+pingNumber)
        
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
            self.sendRaw('NOTICE ' + messageSenderName + ' :\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01')
        elif(messageCtcpCommand.lower()=='time'):
            self.sendRaw('NOTICE ' + messageSenderName + ' :\x01TIME Fribsday 15 Nov 2024 ' + str(time.gmtime()[3]+100).rjust(2,'0') + ':' + str(time.gmtime()[4]+20).rjust(2,'0') + ':' + str(time.gmtime()[5]).rjust(2,'0') + 'GMT\x01')
        elif(messageCtcpCommand.lower()=='ping'):
            self.sendRaw('NOTICE ' + messageSenderName + ' :\x01PING ' + messageCtcpArguments + '\x01')
        elif(messageCtcpCommand.lower()=='userinfo'):
            self.sendRaw('NOTICE ' + messageSenderName + " :\x01Hello, I'm hallo, I'm a robot who does a few different things, mostly roll numbers and choose things, occassionally giving my input on who is the best pony. dr-spangle built me, if you have any questions he tends to be better at replying than I.\x01")
        elif(messageCtcpCommand.lower()=='clientinfo'):
            self.sendRaw('NOTICE ' + messageSenderName + ' :\x01VERSION, NOTICE, TIME, USERINFO and obviously CLIENTINFO are supported.\x01')

        
    def parseLineJoin(self,joinLine):
        'Parses a JOIN message from the server'
        #Parse out the channel and client from the JOIN data
        joinChannel = ':'.join(joinLine.split(':')[2:]).lower()
        joinClient = joinLine.split('!')[0][1:]
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + joinClient + ' joined ' + joinChannel)
        #If channel does logging, log
        #TODO: replace with newer logging
        if(self.mHallo.conf['server'][self.mName]['channel'][joinChannel]['logging']):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + joinClient + ' joined ' + joinChannel,[self.mName,joinChannel])
        #Apply automatic flags as required
        if('auto_list' in self.mHallo.conf['server'][self.mName]['channel'][joinChannel]):
            for entry in self.mHallo.conf['server'][self.mName]['channel'][joinChannel]['auto_list']:
                if(joinClient.lower()==entry['user']):
                    for x in range(7):
                        #TODO: Need a new way to check if users are registered
                        #TODO: http://stackoverflow.com/questions/1682920/determine-if-a-user-is-idented-on-irc
                        if(ircbot_chk.ircbot_chk.chk_userregistered(self.mHallo,self.mName,joinClient)):
                            self.sendRaw('MODE ' + joinChannel + ' ' + entry['flag'] + ' ' + joinClient)
                            break
                        time.sleep(5)
        #If hallo has joined a channel, get the user list and apply automatic flags as required
        if(joinClient.lower() == self.getNick().lower()):
            self.mHallo.conf['server'][self.mName]['channel'][joinChannel]['in_channel'] = True
            namesonline = ircbot_chk.ircbot_chk.chk_names(self.mHallo,self.mName,joinChannel)
            namesonline = [x.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','').lower() for x in namesonline]
            self.mHallo.core['server'][self.mName]['channel'][joinChannel]['user_list'] = namesonline
            if('auto_list' in self.mHallo.conf['server'][self.mName]['channel'][joinChannel]):
                for entry in self.mHallo.conf['server'][self.mName]['channel'][joinChannel]['auto_list']:
                    if(entry['user'] in namesonline):
                        for x in range(7):
                            #TODO: Replace this with a new way to check users are registered
                            if(ircbot_chk.ircbot_chk.chk_userregistered(self,self.mName,entry['user'])):
                                self.sendRaw('MODE ' + joinChannel + ' ' + entry['flag'] + ' ' + entry['user'])
                                break
                            time.sleep(5)
        else:
            #If it was not hallo joining a channel, add nick to user list
            self.mHallo.core['server'][self.mName]['channel'][joinChannel]['user_list'].append(joinClient.lower())
        
    def parseLinePart(self,partLine):
        'Parses a PART message from the server'
        #Parse out channel, client and message from PART data
        partChannel = partLine.split()[2]
        partClient = partLine.split('!')[0][1:]
        partMessage = ':'.join(partLine.split(':')[2:])
        #Print message to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + partClient + ' left ' + partChannel + ' (' + partMessage + ')')
        #If channel does logging, log the PART data
        #TODO: replace with newer logging
        if(self.mHallo.conf['server'][self.mName]['channel'][partChannel]['logging']):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + partClient + ' left ' + partChannel + ' (' + partMessage + ')',[self.mName,partChannel])
        #Remove user from channel's user list
        self.mHallo.core['server'][self.mName]['channel'][partChannel]['user_list'].remove(partClient.lower())
        #Try to work out if the user is still on the server
        #TODO: this needs to be nicer
        stillonserver = False
        for channel_server in self.mHallo.core['server'][self.mName]['channel']:
            if(partClient.lower() in self.mHallo.core['server'][self.mName]['channel'][channel_server]['user_list']):
                stillonserver = True
        if(not stillonserver):
            if(partClient.lower() in self.mHallo.core['server'][self.mName]['auth_op']):
                self.mHallo.core['server'][self.mHallo.mName]['auth_op'].remove(partClient.lower())
            if(partClient.lower() in self.mHallo.core['server'][self.mName]['auth_god']):
                self.mHallo.core['server'][self.mName]['auth_god'].remove(partClient.lower())
    
    def parseLineQuit(self,quitLine):
        'Parses a QUIT message from the server'
        #Parse client and message
        quitClient = quitLine.split('!')[0][1:]
        quitMessage = ':'.join(quitLine.split(':')[2:])
        #Print message to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + quitClient + ' quit: ' + quitMessage)
        #Log to all channels on server
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if(self.mHallo.conf['server'][self.mName]['channel'][channel]['in_channel'] and self.mHallo.conf['server'][self.mName]['channel'][channel]['logging'] and quitClient in self.mHallo.core['server'][self.mName]['channel'][channel]['user_list']):
                self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + quitClient + ' quit: ' + quitMessage,[self.mName,channel])
        #Remove user from user list on all channels
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if(quitClient.lower() in self.mHallo.core['server'][self.mName]['channel'][channel]['user_list']):
                self.mHallo.core['server'][self.mName]['channel'][channel]['user_list'].remove(quitClient.lower())
        #Remove auth stuff from user
        if('auth_op' in self.mHallo.core['server'][self.mName] and quitClient.lower() in self.mHallo.core['server'][self.mName]['auth_op']):
            self.mHallo.core['server'][self.mName]['auth_op'].remove(quitClient.lower())
        if('auth_god' in self.mHallo.core['server'][self.mName] and quitClient.lower() in self.mHallo.core['server'][self.mName]['auth_god']):
            self.mHallo.core['server'][self.mName]['auth_god'].remove(quitClient.lower())
        
    def parseLineMode(self,modeLine):
        'Parses a MODE message from the server'
        #Parsing out MODE data
        modeChannel = modeLine.split()[2].lower()
        modeClient = modeLine.split('!')[0][1:]
        modeMode = modeLine.split()[3]
        if(len(modeLine.split())>=4):
            modeArgs = ' '.join(modeLine.split()[4:])
        else:
            modeArgs = ''
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + modeClient + ' set ' + modeMode + ' ' + modeArgs + ' on ' + modeChannel)
        #Logging, if enabled
        if(modeChannel in self.mHallo.conf['server'][self.mName]['channel'] and 'logging' in self.mHallo.conf['server'][self.mName]['channel'][modeChannel] and self.mHallo.conf['server'][self.mName]['channel'][modeChannel]['logging']):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + modeClient + ' set ' + modeMode + ' ' + modeArgs + ' on ' + modeChannel,[self.mName,modeChannel])
        #If a channel password has been set, store it
        if(modeMode=='-k'):
            self.mHallo.conf['server'][self.mName]['channel'][modeChannel]['pass'] = ''
        elif(modeMode=='+k'):
            self.mHallo.conf['server'][self.mName]['channel'][modeChannel]['pass'] = modeArgs
    
    def parseLineNotice(self,noticeLine):
        'Parses a NOTICE message from the server'
        #Parsing out NOTICE data
        noticeChannel = noticeLine.split()[2]
        noticeClient = noticeLine.split('!')[0][1:]
        noticeMessage = ':'.join(noticeLine.split(':')[2:])
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + noticeChannel + ' Notice from ' + noticeClient + ': ' + noticeMessage)
        #Logging, if enabled
        if(noticeChannel in self.mHallo.conf['server'][self.mName]['channel'] and 'logging' in self.mHallo.conf['server'][self.mName]['channel'][noticeChannel] and self.mHallo.conf['server'][self.mName]['channel'][noticeChannel]['logging']):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + noticeChannel + ' notice from ' + noticeClient + ': ' + noticeMessage,[self.mName,noticeChannel])
        #TODO: DEPRICATED. I am sure this is not required.
        if(self.mHallo.core['server'][self.mName]['connected'] == False):
            self.mHallo.core['server'][self.mName]['connected'] = True
            print(Commons.currentTimestamp() + ' [' + self.mName + "] ok we're connected now.")
        #Checking for end of MOTD.
        if('endofmessage' in noticeMessage.replace(' ','').lower() and self.mHallo.core['server'][self.mName]['motdend'] == False):
            self.mHallo.core['server'][self.mName]['motdend'] = True
        #Checking if user is registered
        #TODO: deprecate this. Use locks, and use STATUS or ACC commands to nickserv
        if(any(nickservmsg in noticeMessage.replace(' ','').lower() for nickservmsg in self.mHallo.conf['nickserv']['online']) and noticeClient.lower()=='nickserv' and self.mHallo.core['server'][self.mName]['check']['userregistered'] == False):
            self.mHallo.core['server'][self.mName]['check']['userregistered'] = True
        if(any(nickservmsg in noticeMessage.replace(' ','').lower() for nickservmsg in self.mHallo.conf['nickserv']['registered']) and noticeClient.lower()=='nickserv' and self.mHallo.core['server'][self.mName]['check']['nickregistered'] == False):
            self.mHallo.core['server'][self.mName]['check']['nickregistered'] = True
        
    def parseLineNick(self,nickLine):
        'Parses a NICK message from the server'
        #Parse out NICK change data
        nickClient = nickLine.split('!')[0][1:]
        if(nickLine.count(':')>1):
            nickNewNick = nickLine.split(':')[2]
        else:
            nickNewNick = nickLine.split()[2]
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] Nick change: ' + nickClient + ' -> ' + nickNewNick)
        #Log, if logging
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if(self.mHallo.conf['server'][self.mName]['channel'][channel]['in_channel'] and self.mHallo.conf['server'][self.mName]['channel'][channel]['logging'] and nickClient in self.mHallo.core['server'][self.mName]['channel'][channel]['user_list']):
                self.mHallo.base_addlog(Commons.currentTimestamp() + ' Nick change: ' + nickClient + ' -> ' + nickNewNick,[self.mName,channel])
        #Update nick list for each channel
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if(nickClient.lower() in self.mHallo.core['server'][self.mName]['channel'][channel]['user_list']):
                self.mHallo.core['server'][self.mName]['channel'][channel]['user_list'].remove(nickClient.lower())
                self.mHallo.core['server'][self.mName]['channel'][channel]['user_list'].append(nickNewNick.lower())
        #If it was the bots nick that just changed, update that.
        if(nickClient == self.getNick()):
            self.mNick = nickNewNick
        #Update auth_op lists
        if('auth_op' in self.mHallo.core['server'][self.mName] and nickClient.lower() in self.mHallo.core['server'][self.mName]['auth_op']):
            self.mHallo.core['server'][self.mName]['auth_op'].remove(nickClient.lower())
            self.mHallo.core['server'][self.mName]['auth_op'].append(nickNewNick.lower())
        #Update auth_god lists
        if('auth_god' in self.mHallo.core['server'][self.mName] and nickClient.lower() in self.mHallo.core['server'][self.mName]['auth_god']):
            self.mHallo.core['server'][self.mName]['auth_god'].remove(nickClient.lower())
            self.mHallo.core['server'][self.mName]['auth_god'].append(nickNewNick.lower())
        #Check whether this verifies anything that means automatic flags need to be applied
        for channel in self.mHallo.conf['server'][self.mName]['channel']:
            if('auto_list' in self.mHallo.conf['server'][self.mName]['channel'][channel]):
                for entry in self.mHallo.conf['server'][self.mName]['channel'][channel]['auto_list']:
                    if(nickNewNick == entry['user']):
                        for _ in range(7):
                            if(ircbot_chk.ircbot_chk.chk_userregistered(self.mHallo,self.mName,nickNewNick)):
                                self.sendRaw('MODE ' + channel + ' ' + entry['flag'] + ' ' + nickNewNick)
                                break
                            time.sleep(5)
        
    def parseLineInvite(self,inviteLine):
        'Parses an INVITE message from the server'
        #Parse out INVITE data
        inviteClient = inviteLine.split('!')[0][1:]
        inviteChannel = ':'.join(inviteLine.split(':')[2:])
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] invite to ' + inviteChannel + ' from ' + inviteClient)
        #Logging, if applicable
        if(inviteChannel in self.mHallo.conf['server'][self.mName]['channel'] and 'logging' in self.mHallo.conf['server'][self.mName]['channel'][inviteChannel] and self.mHallo.conf['server'][self.mName]['channel'][inviteChannel]['logging']):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' invite to ' + inviteChannel + ' from ' + inviteClient,[self.mName,'@SERVER'])
        #Check if they are an op, then join the channel.
        #TODO: change this logic, when channel object exists
        if(ircbot_chk.ircbot_chk.chk_op(self.mHallo,self.mName,inviteClient)):
            hallobase_ctrl.hallobase_ctrl.fn_join(self.mHallo,inviteChannel,inviteClient,[self.mName,''])
        
    def parseLineKick(self,kickLine):
        'Parses a KICK message from the server'
        #Parse out KICK data
        kickChannel = kickLine.split()[2]
        kickClient = kickLine.split()[3]
        kickMessage = ':'.join(kickLine.split(':')[4:])
        #Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] ' + kickClient + ' was kicked from ' + kickChannel + ': ' + kickMessage)
        #Log, if applicable
        if(self.mHallo.conf['server'][self.mName]['channel'][kickChannel]['logging']):
            self.mHallo.base_addlog(Commons.currentTimestamp() + ' ' + kickClient + ' was kicked from ' + kickChannel + ': ' + kickMessage,[self.mName,kickChannel])
        #Remove kicked user from userlist
        self.mHallo.core['server'][self.mName]['channel'][kickChannel]['user_list'].remove(kickClient.lower())
        #If it was the bot who was kicked, set "in channel" status to False
        if(kickClient == self.mHallo.conf['server'][self.mName]['nick']):
            self.mHallo.conf['server'][self.mName]['channel'][kickChannel]['in_channel'] = False

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
        #TODO: use locks to make this pleasant.
        elif(numericCode == "303"):
            self.mHallo.core['server'][self.mName]['check']['recipientonline'] = ':'.join(numericLine.split(':')[2:])
            if(self.mHallo.core['server'][self.mName]['check']['recipientonline']==''):
                self.mHallo.core['server'][self.mName]['check']['recipientonline'] = ' '
        #Check for NAMES request reply, telling you who is in a channel.
        #TODO: use locks to make this pleasant.
        elif(numericCode == "353"):
            channel = numericLine.split(':')[1].split()[-1].lower()
            self.mHallo.core['server'][self.mName]['check']['names'] = ':'.join(numericLine.split(':')[2:])
            self.mHallo.core['server'][self.mName]['channel'][channel]['user_list'] = [nick.replace('~','').replace('&','').replace('@','').replace('%','').replace('+','').lower() for nick in self.mHallo.core['server'][self.mName]['check']['names'].split()]

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
        if(len(doc.getElementsByTagName("nickserv_pass"))!=0):
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
        if(self.mNickservPass is not None):
            nickservPassElement = doc.createElement("nickserv_pass")
            nickservPassElement.appendChild(doc.createTextNode(self.mNickservPass))
            root.appendChild(nickservPassElement)
        #output XML string
        return doc.toxml()

        