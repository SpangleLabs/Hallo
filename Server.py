from abc import ABCMeta
from xml.dom import minidom
from inc.commons import Commons
from threading import Thread, Lock
import socket
import time
import re

from Destination import Channel, User
from PermissionMask import PermissionMask
from Function import Function

endl = Commons.mEndLine


class ServerException(Exception):
    pass


class ServerFactory:
    """
    Server factory, makes servers.
    Basically looks at xml, finds server type, and passes to appropriate Server object constructor
    """
    mHallo = None  # Parent Hallo object

    def __init__(self, hallo):
        """
        Constructs the Server Factory, stores Hallo object.
        :type hallo: Hallo object which owns this server factory
        """
        self.mHallo = hallo

    def newServerFromXml(self, xmlString):
        doc = minidom.parseString(xmlString)
        serverType = doc.getElementsByTagName("server_type")[0].firstChild.data
        if serverType == Server.TYPE_IRC:
            return ServerIRC.fromXml(xmlString, self.mHallo)
        else:
            return None


class Server(metaclass=ABCMeta):
    """
    Generic server object. An interface for ServerIRC or ServerSkype or whatever objects.
    """
    mHallo = None  # The hallo object that created this server
    # Persistent/saved class variables
    mName = None  # Server name
    mAutoConnect = True  # Whether to automatically connect to this server when hallo starts
    mChannelList = None  # List of channels on this server (which may or may not be currently active)
    mUserList = None  # Users on this server (not all of which are online)
    mNick = None  # Nickname to use on this server
    mPrefix = None  # Prefix to use with functions on this server
    mFullName = None  # Full name to use on this server
    mPermissionMask = None  # PermissionMask for the server
    # Dynamic/unsaved class variables
    mOpen = False  # Whether or not to keep reading from server

    # Constants
    TYPE_IRC = "irc"

    def __init__(self, hallo):
        """
        Constructor for server object
        :type hallo: Hallo Instance of hallo that contains this server object
        """
        self.mChannelList = []
        self.mUserList = []
        self.mHallo = hallo
        self.mPermissionMask = PermissionMask()
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def reconnect(self):
        raise NotImplementedError

    def run(self):
        """
        Method to read from stream and process. Will call an internal parsing method or whatnot
        """
        raise NotImplementedError

    def send(self, data, destinationObject=None, msgType="message"):
        """
        Sends a message to the server, or a specific channel in the server
        :param data: Line of data to send to server
        :param destinationObject: Destination to send data to
        :param msgType: Type of message which is being sent
        """
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString, hallo):
        """
        Constructor to build a new server object from xml
        :param xmlString: XML string representation of the server
        :param hallo: Hallo object which is connected to this server
        """
        raise NotImplementedError

    def toXml(self):
        """
        Returns an XML representation of the server object
        """
        raise NotImplementedError

    def getHallo(self):
        """Returns the Hallo instance that created this Server"""
        return self.mHallo

    def getName(self):
        """Name getter"""
        return self.mName

    def getNick(self):
        """Nick getter"""
        if self.mNick is None:
            return self.mHallo.getDefaultNick()
        return self.mNick

    def setNick(self, nick):
        """
        Nick setter
        :param nick: New nick for hallo to use on this server
        """
        self.mNick = nick

    def getPrefix(self):
        """Prefix getter"""
        if self.mPrefix is None:
            return self.mHallo.getDefaultPrefix()
        return self.mPrefix

    def setPrefix(self, prefix):
        """
        Prefix setter
        :param prefix: Prefix for hallo to use for function calls on this server
        """
        self.mPrefix = prefix

    def getFullName(self):
        """Full name getter"""
        if self.mFullName is None:
            return self.mHallo.getDefaultFullName()
        return self.mFullName

    def setFullName(self, fullName):
        """
        Full name setter
        :param fullName: Full name for Hallo to use on this server
        """
        self.mFullName = fullName

    def getAutoConnect(self):
        """AutoConnect getter"""
        return self.mAutoConnect

    def setAutoConnect(self, autoConnect):
        """
        AutoConnect setter
        :param autoConnect: Whether or not to autoconnect to the server
        """
        self.mAutoConnect = autoConnect

    def getType(self):
        """Type getter"""
        raise NotImplementedError

    def getPermissionMask(self):
        return self.mPermissionMask

    def isConnected(self):
        """Returns boolean representing whether the server is connected or not."""
        return self.mOpen

    def getChannelByName(self, channelName):
        """
        Returns a Channel object with the specified channel name.
        :param channelName: Name of the channel which is being searched for
        """
        channelName = channelName.lower()
        for channel in self.mChannelList:
            if channel.getName() == channelName:
                return channel
        newChannel = Channel(channelName, self)
        self.addChannel(newChannel)
        return newChannel

    def getChannelList(self):
        return self.mChannelList

    def addChannel(self, channelObject):
        """
        Adds a channel to the channel list
        :param channelObject: Adds a channel to the list, without joining it
        """
        self.mChannelList.append(channelObject)

    def joinChannel(self, channelObject):
        """
        Joins a specified channel
        :param channelObject: Channel to join
        """
        raise NotImplementedError

    def leaveChannel(self, channelObject):
        """
        Leaves a specified channel
        :param channelObject: Channel for hallo to leave
        """
        raise NotImplementedError

    def getUserByName(self, userName):
        """
        Returns a User object with the specified user name.
        :param userName: Name of user which is being searched for
        """
        userName = userName.lower()
        for user in self.mUserList:
            if user.getName() == userName:
                return user
        # No user by that name exists, so create one.
        newUser = User(userName, self)
        self.addUser(newUser)
        return newUser

    def getUserList(self):
        """Returns the full list of users on this server."""
        return self.mUserList

    def addUser(self, userObject):
        """
        Adds a user to the user list
        :param userObject: User to add to user list
        """
        self.mUserList.append(userObject)

    def rightsCheck(self, rightName):
        """
        Checks the value of the right with the specified name. Returns boolean
        :type rightName: Name of the right to check default server value for
        """
        if self.mPermissionMask is not None:
            rightValue = self.mPermissionMask.getRight(rightName)
            # If PermissionMask contains that right, return it.
            if rightValue in [True, False]:
                return rightValue
        # Fallback to the parent Hallo's decision.
        return self.mHallo.rightsCheck(rightName)

    def checkUserIdentity(self, userObject):
        """
        Check if a user is identified and verified
        :param userObject: User to check identity of
        """
        raise NotImplementedError


class ServerIRC(Server):
    mHallo = None  # The hallo object that created this server
    # Persistent/saved class variables
    mName = None  # Server name
    mAutoConnect = True  # Whether to automatically connect to this server when hallo starts
    mChannelList = None  # list of channels on this server (which may or may not be currently active)
    mUserList = None  # Users on this server (not all of which are online)
    mConnection = None  # Connection for the server, socket or whatnot
    mNick = None  # Nickname to use on this server
    mPrefix = None  # Prefix to use with functions on this server
    mFullName = None  # Full name to use on this server
    mPermissionMask = None  # PermissionMask for the server
    # Dynamic/unsaved class variables
    mOpen = False  # Whether or not to keep reading from server
    # IRC specific variables
    mServerAddress = None  # Address to connect to server
    mServerPort = None  # Port to connect to server
    mNickservPass = None  # Password to identify with nickserv
    mNickservNick = "nickserv"  # Nickserv's nick, None if nickserv does not exist
    mNickservIdentCommand = "STATUS"  # Command to send to nickserv to check if a user is identified
    mNickservIdentResponse = "\\b3\\b"  # Regex to search for to validate identity in response to IdentCommand
    # IRC specific dynamic variables
    mSocket = None  # Socket to communicate to the server
    mWelcomeMessage = ""  # Server's welcome message when connecting. MOTD and all.
    mCheckChannelUserListLock = None  # Thread lock for checking a channel's user list
    mCheckChannelUserListChannel = None  # Channel to check user list of
    mCheckChannelUserListUserList = None  # User name list of checked channel
    mCheckUsersOnlineLock = None  # Thread lock for checking which users are online
    mCheckUsersOnlineCheckList = None  # List of users' names to check
    mCheckUsersOnlineOnlineList = None  # List of users' names who are online
    mCheckUserIdentityLock = None  # Thread lock for checking if a user is identified with nickserv
    mCheckUserIdentityUser = None  # User name which is being checked
    mCheckUserIdentityResult = None  # Boolean, whether or not the user is identified

    def __init__(self, hallo, serverName=None, serverUrl=None, serverPort=6667):
        """
        Constructor for server object
        :param hallo: Hallo instance which owns this server
        :type serverName: Name of the IRC server
        :type serverUrl: URL of the IRC server
        :type serverPort: port of the IRC server
        """
        super().__init__(hallo)
        self.mChannelList = []
        self.mUserList = []
        self.mHallo = hallo
        self.mPermissionMask = PermissionMask()
        self.mCheckChannelUserListLock = Lock()
        self.mCheckUsersOnlineLock = Lock()
        self.mCheckUserIdentityLock = Lock()
        if serverName is not None:
            self.mName = serverName
        if serverUrl is not None:
            self.mServerAddress = serverUrl
            self.mServerPort = serverPort

    def connect(self):
        while True:
            try:
                self.rawConnect()
                break
            except ServerException:
                print("Failed to connect. Waiting 3 seconds before reconnect.")
                time.sleep(3)
                continue

    def rawConnect(self):
        # Begin pulling data from a given server
        self.mOpen = True
        # Create new socket
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to socket
            self.mSocket.connect((self.mServerAddress, self.mServerPort))
        except Exception as e:
            print("CONNECTION ERROR: " + str(e))
            self.mOpen = False
        # Wait for the first message back from the server.
        print(Commons.currentTimestamp() + " waiting for first message from server: " + self.mName)
        firstLine = self.readLineFromSocket()
        # If first line is null, that means connection was closed.
        if firstLine is None:
            raise ServerException
        self.mWelcomeMessage = firstLine + "\n"
        # Send nick and full name to server
        print(Commons.currentTimestamp() + " sending nick and user info to server: " + self.mName)
        self.send('NICK ' + self.getNick(), None, "raw")
        self.send('USER ' + self.getFullName(), None, "raw")
        # Wait for MOTD to end
        while True:
            nextWelcomeLine = self.readLineFromSocket()
            if nextWelcomeLine is None:
                raise ServerException
            self.mWelcomeMessage += nextWelcomeLine + "\n"
            if "376" in nextWelcomeLine or "endofmessage" in nextWelcomeLine.replace(' ', '').lower():
                break
            if nextWelcomeLine.split()[0] == "PING":
                self.parseLinePing(nextWelcomeLine)
            if len(nextWelcomeLine.split()[1]) == 3 and nextWelcomeLine.split()[1].isdigit():
                self.parseLineNumeric(nextWelcomeLine, False)
        # Identify with nickserv
        if self.mNickservPass:
            self.send('IDENTIFY ' + self.mNickservPass, self.getUserByName("nickserv"))
        # Join channels
        print(Commons.currentTimestamp() + " joining channels on " + self.mName + ", identifying.")
        # Join relevant channels
        for channel in self.mChannelList:
            if channel.isAutoJoin():
                self.joinChannel(channel)

    def disconnect(self):
        """Disconnect from the server"""
        quitMessage = "Will I dream?"
        # Logging
        for channel in self.mChannelList:
            if channel.isInChannel():
                self.mHallo.getLogger().log(Function.EVENT_QUIT, quitMessage, self, self.getUserByName(self.getNick()),
                                            channel)
                channel.setInChannel(False)
        for user in self.mUserList:
            user.setOnline(False)
        if self.mOpen:
            try:
                self.send("QUIT :" + quitMessage, None, "raw")
            except:
                pass
            self.mSocket.close()
            self.mSocket = None
            self.mOpen = False

    def reconnect(self):
        """
        Reconnect to a given server. Basically just disconnect and reconnect.
        """
        self.disconnect()
        self.connect()

    def run(self):
        """
        Method to read from stream and process. Will call an internal parsing method or whatnot
        """
        if not self.mOpen:
            self.connect()
        while self.mOpen:
            nextLine = None
            try:
                nextLine = self.readLineFromSocket()
            except ServerException:
                print("Server disconnected. Reconnecting.")
                time.sleep(10)
                self.reconnect()
            if nextLine is None:
                self.mOpen = False
            else:
                # Parse line
                Thread(target=self.parseLine, args=(nextLine,)).start()

    def send(self, data, destinationObject=None, msgType="message"):
        """
        Sends a message to the server, or a specific channel in the server
        :param data: Line of data to send to server
        @type data: str

        :param destinationObject: Destination to send data to
        @type destinationObject: Destination or None

        :param msgType: Type of message which is being sent
        @type msgType: str
        """
        maxMsgLength = 462  # Maximum length of a message sent to the server
        if msgType not in ["message", "notice", "raw"]:
            msgType = "message"
        # If it's raw data, just send it.
        if destinationObject is None or msgType == "raw":
            for dataLine in data.split("\n"):
                self.sendRaw(dataLine)
            return
        # Get message type
        if msgType == "notice":
            msgTypeName = "NOTICE"
        else:
            msgTypeName = "PRIVMSG"
        # Get channel or user name and data
        destinationName = destinationObject.getName()
        channelObject = None
        userObject = destinationObject
        if destinationObject.getType() == "channel":
            channelObject = destinationObject
            userObject = None
        # Find out if destination wants caps lock
        if destinationObject.isUpperCase():
            # Find any URLs, convert line to uppercase, then convert URLs back to original
            urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", data)
            data = data.upper()
            for url in urls:
                data = data.replace(url.upper(), url)
        # Get max line length
        maxLineLength = maxMsgLength - len(msgTypeName + ' ' + destinationName + ' :' + endl)
        # Split and send
        for dataLine in data.split("\n"):
            dataLineSplit = Commons.chunkStringDot(dataLine, maxLineLength)
            for dataLineLine in dataLineSplit:
                self.sendRaw(msgTypeName + ' ' + destinationName + ' :' + dataLineLine)
                # Log sent data, if it's not message or notice
                if msgType == "message":
                    self.mHallo.getPrinter().outputFromSelf(Function.EVENT_MESSAGE, dataLineLine, self, userObject,
                                                            channelObject)
                    self.mHallo.getLogger().logFromSelf(Function.EVENT_MESSAGE, dataLineLine, self, userObject,
                                                        channelObject)
                elif msgType == "notice":
                    self.mHallo.getPrinter().outputFromSelf(Function.EVENT_NOTICE, dataLineLine, self, userObject,
                                                            channelObject)
                    self.mHallo.getLogger().logFromSelf(Function.EVENT_NOTICE, dataLineLine, self, userObject,
                                                        channelObject)

    def sendRaw(self, data):
        """Sends raw data to the server
        :param data: Data to send to server
        """
        if self.mOpen:
            self.mSocket.send((data + endl).encode("utf-8"))

    def joinChannel(self, channelObject):
        """Joins a specified channel
        :param channelObject: Channel to join
        """
        # If channel isn't in channel list, add it
        if channelObject not in self.mChannelList:
            self.addChannel(channelObject)
        # Set channel to AutoJoin, for the future
        channelObject.setAutoJoin(True)
        # Send JOIN command
        if channelObject.getPassword() is None:
            self.send('JOIN ' + channelObject.getName(), None, "raw")
        else:
            self.send('JOIN ' + channelObject.getName() + ' ' + channelObject.getPassword(), None, "raw")

    def leaveChannel(self, channelObject):
        """
        Leaves a specified channel
        :param channelObject: Channel to leave
        """
        # If channel isn't in channel list, do nothing
        if channelObject not in self.mChannelList:
            return
        # Set channel to not AutoJoin, for the future
        channelObject.setAutoJoin(False)
        # Set not in channel
        channelObject.setInChannel(False)
        # Send PART command
        self.send('PART ' + channelObject.getName(), None, "raw")

    def parseLine(self, newLine):
        """
        Parses a line from the IRC server
        :param newLine: New line of data from the server to parse
        """
        # Cleaning up carriage returns
        newLine = newLine.replace("\r", "")
        # TODO: add stuff about time last ping was seen, for reconnection checking
        if len(newLine) < 5 or (newLine[0] != ":" and newLine[0:4] != "PING"):
            self.parseLineUnhandled(newLine)
            self.parseLineRaw(newLine, "unhandled")
        elif newLine.split()[0] == "PING":
            self.parseLinePing(newLine)
            self.parseLineRaw(newLine, "ping")
        elif newLine.split()[1] == "PRIVMSG":
            self.parseLineMessage(newLine)
            self.parseLineRaw(newLine, "message")
        elif newLine.split()[1] == "JOIN":
            self.parseLineJoin(newLine)
            self.parseLineRaw(newLine, "join")
        elif newLine.split()[1] == "PART":
            self.parseLinePart(newLine)
            self.parseLineRaw(newLine, "part")
        elif newLine.split()[1] == "QUIT":
            self.parseLineQuit(newLine)
            self.parseLineRaw(newLine, "quit")
        elif newLine.split()[1] == "MODE":
            self.parseLineMode(newLine)
            self.parseLineRaw(newLine, "mode")
        elif newLine.split()[1] == "NOTICE":
            self.parseLineNotice(newLine)
            self.parseLineRaw(newLine, "notice")
        elif newLine.split()[1] == "NICK":
            self.parseLineNick(newLine)
            self.parseLineRaw(newLine, "nick")
        elif newLine.split()[1] == "INVITE":
            self.parseLineInvite(newLine)
            self.parseLineRaw(newLine, "invite")
        elif newLine.split()[1] == "KICK":
            self.parseLineKick(newLine)
            self.parseLineRaw(newLine, "kick")
        elif len(newLine.split()[1]) == 3 and newLine.split()[1].isdigit():
            self.parseLineNumeric(newLine)
            self.parseLineRaw(newLine, "numeric")
        else:
            self.parseLineUnhandled(newLine)
            self.parseLineRaw(newLine, "unhandled")
        return

    def parseLinePing(self, pingLine):
        """
        Parses a PING message from the server
        :param pingLine: str Raw line to be parsed into ping event from the server
        """
        # Get data
        pingNumber = pingLine.split()[1]
        # Respond
        self.send("PONG " + pingNumber, None, "raw")
        # Print and log
        self.mHallo.getPrinter().output(Function.EVENT_PING, pingNumber, self, None, None)
        self.mHallo.getPrinter().outputFromSelf(Function.EVENT_PING, pingNumber, self, None, None)
        self.mHallo.getLogger().log(Function.EVENT_PING, pingNumber, self, None, None)
        self.mHallo.getLogger().logFromSelf(Function.EVENT_PING, pingNumber, self, None, None)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_PING, pingNumber, self, None, None)

    def parseLineMessage(self, messageLine):
        """
        Parses a PRIVMSG message from the server
        :param messageLine: str full privmsg line to parse from server
        """
        # Parse out the message text
        messageText = ':'.join(messageLine.split(':')[2:])
        # Parse out the message sender
        messageSenderName = messageLine.split('!')[0].replace(':', '')
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        messageDestinationName = messageLine.split()[2].lower()
        # Test for CTCP message, hand to CTCP parser if so.
        messageCtcpBool = messageText[0] == '\x01'
        if messageCtcpBool:
            self.parseLineCtcp(messageLine)
            return
        # Test for private message or public message.
        messagePrivateBool = messageDestinationName.lower() == self.getNick().lower()
        messagePublicBool = not messagePrivateBool
        # Get relevant objects.
        messageSender = self.getUserByName(messageSenderName)
        messageSender.updateActivity()
        messageDestination = messageSender
        # Get the prefix
        actingPrefix = self.getPrefix()
        if messagePublicBool:
            messageChannel = self.getChannelByName(messageDestinationName)
            messageChannel.updateActivity()
            messageDestination = messageChannel
            # Print and Log the public message
            self.mHallo.getPrinter().output(Function.EVENT_MESSAGE, messageText, self, messageSender, messageChannel)
            self.mHallo.getLogger().log(Function.EVENT_MESSAGE, messageText, self, messageSender, messageChannel)
            actingPrefix = messageChannel.getPrefix()
        else:
            # Print and Log the private message
            self.mHallo.getPrinter().output(Function.EVENT_MESSAGE, messageText, self, messageSender, None)
            self.mHallo.getLogger().log(Function.EVENT_MESSAGE, messageText, self, messageSender, None)
        # Figure out if the message is a command, Send to FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        if messagePrivateBool:
            functionDispatcher.dispatch(messageText, messageSender, messageDestination)
        elif actingPrefix is False:
            actingPrefix = self.getNick().lower()
            if messageText.lower().startswith(actingPrefix + ":") or messageText.lower().startswith(actingPrefix + ","):
                messageText = messageText[len(actingPrefix) + 1:]
                functionDispatcher.dispatch(messageText, messageSender, messageDestination)
            elif messageText.lower().startswith(actingPrefix):
                messageText = messageText[len(actingPrefix):]
                functionDispatcher.dispatch(messageText, messageSender, messageDestination,
                                            [functionDispatcher.FLAG_HIDE_ERRORS])
            else:
                # Pass to passive function checker
                functionDispatcher.dispatchPassive(Function.EVENT_MESSAGE, messageText, self, messageSender,
                                                   messageChannel)
        elif messageText.lower().startswith(actingPrefix):
            messageText = messageText[len(actingPrefix):]
            functionDispatcher.dispatch(messageText, messageSender, messageDestination)
        else:
            # Pass to passive function checker
            functionDispatcher.dispatchPassive(Function.EVENT_MESSAGE, messageText, self, messageSender, messageChannel)

    def parseLineCtcp(self, ctcpLine):
        """
        Parses a CTCP message from the server
        :param ctcpLine: line of CTCP data to parse from the server
        """
        # Parse out the ctcp message text
        messageText = ':'.join(ctcpLine.split(':')[2:])[1:-1]
        # Parse out the message sender
        messageSenderName = ctcpLine.split('!')[0].replace(':', '')
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        messageDestinationName = ctcpLine.split()[2].lower()
        # Parse out the CTCP command and arguments
        messageCtcpCommand = messageText.split()[0]
        messageCtcpArguments = ' '.join(messageText.split()[1:])
        # Test for private message or public message
        messagePrivateBool = messageDestinationName.lower() == self.getNick().lower()
        messagePublicBool = not messagePrivateBool
        # Get relevant objects.
        messageChannel = None
        if messagePublicBool:
            messageChannel = self.getChannelByName(messageDestinationName)
            messageChannel.updateActivity()
        messageSender = self.getUserByName(messageSenderName)
        messageSender.updateActivity()
        # Print and log the message
        if messagePrivateBool:
            self.mHallo.getPrinter().output(Function.EVENT_CTCP, messageText, self, messageSender, None)
            self.mHallo.getLogger().log(Function.EVENT_CTCP, messageText, self, messageSender, None)
        else:
            self.mHallo.getPrinter().output(Function.EVENT_CTCP, messageText, self, messageSender, messageChannel)
            self.mHallo.getLogger().log(Function.EVENT_CTCP, messageText, self, messageSender, messageChannel)
        # Reply to certain types of CTCP command
        if messageCtcpCommand.lower() == 'version':
            self.send("\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01", messageSender, "notice")
        elif messageCtcpCommand.lower() == 'time':
            self.send("\x01TIME Fribsday 15 Nov 2024 " + str(time.gmtime()[3] + 100).rjust(2, '0') + ":" + str(
                time.gmtime()[4] + 20).rjust(2, '0') + ":" + str(time.gmtime()[5]).rjust(2, '0') + "GMT\x01",
                      messageSender, "notice")
        elif messageCtcpCommand.lower() == 'ping':
            self.send('\x01PING ' + messageCtcpArguments + '\x01', messageSender, "notice")
        elif messageCtcpCommand.lower() == 'userinfo':
            hallo_info = "Hello, I'm hallo, I'm a robot who does a few different things," \
                         " mostly roll numbers and choose things," \
                         " occasionally giving my input on who is the best pony." \
                         " dr-spangle built me, if you have any questions he tends to be better at replying than I."
            self.send("\x01" + hallo_info + "\x01", messageSender, "notice")
        elif messageCtcpCommand.lower() == 'clientinfo':
            self.send('\x01VERSION, NOTICE, TIME, USERINFO and obviously CLIENTINFO are supported.\x01', messageSender,
                      "notice")
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_CTCP, messageText, self, messageSender, messageChannel)

    def parseLineJoin(self, joinLine):
        """
        Parses a JOIN message from the server
        :param joinLine: str Raw line from server for the JOIN event
        """
        # Parse out the channel and client from the JOIN data
        joinChannelName = ':'.join(joinLine.split(':')[2:]).lower()
        joinClientName = joinLine.split('!')[0][1:]
        # Get relevant objects
        joinChannel = self.getChannelByName(joinChannelName)
        joinClient = self.getUserByName(joinClientName)
        joinClient.updateActivity()
        # Print and log
        self.mHallo.getPrinter().output(Function.EVENT_JOIN, None, self, joinClient, joinChannel)
        self.mHallo.getLogger().log(Function.EVENT_JOIN, None, self, joinClient, joinChannel)
        # TODO: Apply automatic flags as required
        # If hallo has joined a channel, get the user list and apply automatic flags as required
        if joinClient.getName().lower() == self.getNick().lower():
            joinChannel.setInChannel(True)
        else:
            # If it was not hallo joining a channel, add nick to user list
            joinChannel.addUser(joinClient)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_JOIN, None, self, joinClient, joinChannel)

    def parseLinePart(self, partLine):
        """
        Parses a PART message from the server
        :param partLine: str Raw line from the server to parse for part event
        """
        # Parse out channel, client and message from PART data
        partChannelName = partLine.split()[2]
        partClientName = partLine.split('!')[0][1:]
        partMessage = ':'.join(partLine.split(':')[2:])
        # Get channel and user object
        partChannel = self.getChannelByName(partChannelName)
        partClient = self.getUserByName(partClientName)
        # Print and log
        self.mHallo.getPrinter().output(Function.EVENT_LEAVE, partMessage, self, partClient, partChannel)
        self.mHallo.getLogger().log(Function.EVENT_LEAVE, partMessage, self, partClient, partChannel)
        # Remove user from channel's user list
        partChannel.removeUser(partClient)
        # Try to work out if the user is still on the server
        # TODO: this needs to be nicer
        userStillOnServer = False
        for channel_server in self.mChannelList:
            if partClient in channel_server.getUserList():
                userStillOnServer = True
        if not userStillOnServer:
            partClient.setOnline(False)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_LEAVE, partMessage, self, partClient, partChannel)

    def parseLineQuit(self, quitLine):
        """
        Parses a QUIT message from the server
        :param quitLine: str Raw line from server to parse for quit event
        """
        # Parse client and message
        quitClientName = quitLine.split('!')[0][1:]
        quitMessage = ':'.join(quitLine.split(':')[2:])
        # Get client object
        quitClient = self.getUserByName(quitClientName)
        # Print and Log to all channels on server
        self.mHallo.getPrinter().output(Function.EVENT_QUIT, quitMessage, self, quitClient, Commons.ALL_CHANNELS)
        for channel in self.mChannelList:
            self.mHallo.getLogger().log(Function.EVENT_QUIT, quitMessage, self, quitClient, channel)
        # Remove user from user list on all channels
        for channel in self.mChannelList:
            channel.removeUser(quitClient)
        # Remove auth stuff from user
        quitClient.setOnline(False)
        # If it was hallo which quit, set all channels to out of channel and all users to offline
        if quitClient.getName().lower() == self.getNick().lower():
            for channel in self.mChannelList:
                channel.setInChannel(False)
            for user in self.mUserList:
                user.setOnline(False)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_QUIT, quitMessage, self, quitClient, None)

    def parseLineMode(self, modeLine):
        """
        Parses a MODE message from the server
        :param modeLine: str Raw line of mode event to be parsed.
        """
        # Parsing out MODE data
        modeChannelName = modeLine.split()[2].lower()
        modeClientName = modeLine.split()[0][1:]
        if "!" in modeClientName:
            modeClientName = modeClientName.split("!")[0]
        modeMode = modeLine.split()[3]
        if modeMode[0] == ":":
            modeMode = modeMode[1:]
        if len(modeLine.split()) >= 4:
            modeArgs = ' '.join(modeLine.split()[4:])
        else:
            modeArgs = ''
        # Get client and channel objects
        modeChannel = self.getChannelByName(modeChannelName)
        modeClient = self.getUserByName(modeClientName)
        # If a channel password has been set, store it
        if modeMode == '-k':
            modeChannel.setPassword(None)
        elif modeMode == '+k':
            modeChannel.setPassword(modeArgs)
        # Printing and logging
        modeFull = modeMode
        if modeArgs != '':
            modeFull = modeMode + ' ' + modeArgs
        self.mHallo.getPrinter().output(Function.EVENT_MODE, modeFull, self, modeClient, modeChannel)
        self.mHallo.getLogger().log(Function.EVENT_MODE, modeFull, self, modeClient, modeChannel)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_MODE, modeFull, self, modeClient, modeChannel)

    def parseLineNotice(self, noticeLine: str):
        """
        Parses a NOTICE message from the server
        :param noticeLine: str Raw line of the NOTICE event from the server
        """
        # Parsing out NOTICE data
        noticeChannelName = noticeLine.split()[2]
        noticeClientName = noticeLine.split('!')[0][1:]
        noticeMessage = ':'.join(noticeLine.split(':')[2:])
        # Get client and channel objects
        noticeChannel = self.getChannelByName(noticeChannelName)
        noticeChannel.updateActivity()
        noticeClient = self.getUserByName(noticeClientName)
        noticeClient.updateActivity()
        # Print to console, log to file
        self.mHallo.getPrinter().output(Function.EVENT_NOTICE, noticeMessage, self, noticeClient, noticeChannel)
        self.mHallo.getLogger().log(Function.EVENT_NOTICE, noticeMessage, self, noticeClient, noticeChannel)
        # Checking if user is registered
        if noticeClient.getName() == self.mNickservNick and \
                        self.mCheckUserIdentityUser is not None and \
                        self.mNickservIdentCommand is not None:
            # check if notice message contains command and user name
            if self.mCheckUserIdentityUser in noticeMessage and self.mNickservIdentCommand in noticeMessage:
                # Make regex query of identity response
                regexIdentResponse = re.compile(self.mNickservIdentResponse, re.IGNORECASE)
                # check if response is in notice message
                if regexIdentResponse.search(noticeMessage) is not None:
                    self.mCheckUserIdentityResult = True
                else:
                    self.mCheckUserIdentityResult = False
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_NOTICE, noticeMessage, self, noticeClient, noticeChannel)

    def parseLineNick(self, nickLine):
        """Parses a NICK message from the server
        :param nickLine: Line from server specifying nick change
        """
        # Parse out NICK change data
        nickClientName = nickLine.split('!')[0][1:]
        if nickLine.count(':') > 1:
            nickNewNick = nickLine.split(':')[2]
        else:
            nickNewNick = nickLine.split()[2]
        # Get user object
        nickClient = self.getUserByName(nickClientName)
        # If it was the bots nick that just changed, update that.
        if nickClient.getName() == self.getNick():
            self.mNick = nickNewNick
        # TODO: Check whether this verifies anything that means automatic flags need to be applied
        # Update name for user object
        nickClient.setName(nickNewNick)
        # Printing and logging
        self.mHallo.getPrinter().output(Function.EVENT_CHNAME, nickClientName, self, nickClient, Commons.ALL_CHANNELS)
        for channel in self.mChannelList:
            self.mHallo.getLogger().log(Function.EVENT_CHNAME, nickClientName, self, nickClient, channel)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_CHNAME, nickClientName, self, nickClient, None)

    def parseLineInvite(self, inviteLine):
        """Parses an INVITE message from the server
        :param inviteLine: Line from the server specifying invite event
        """
        # Parse out INVITE data
        inviteClientName = inviteLine.split('!')[0][1:]
        inviteChannelName = ':'.join(inviteLine.split(':')[2:])
        # Get destination objects
        inviteClient = self.getUserByName(inviteClientName)
        inviteClient.updateActivity()
        inviteChannel = self.getChannelByName(inviteChannelName)
        # Printing and logging
        self.mHallo.getPrinter().output(Function.EVENT_INVITE, None, self, inviteClient, inviteChannel)
        self.mHallo.getLogger().log(Function.EVENT_INVITE, None, self, inviteClient, inviteChannel)
        # Check if they are an op, then join the channel.
        if inviteClient.rightsCheck("invite_channel", inviteChannel):
            self.joinChannel(inviteChannel)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_INVITE, None, self, inviteClient, inviteChannel)

    def parseLineKick(self, kickLine):
        """Parses a KICK message from the server
        :param kickLine: Line from the server specifying kick event
        """
        # Parse out KICK data
        kickChannelName = kickLine.split()[2]
        kickClientName = kickLine.split()[3]
        kickMessage = ':'.join(kickLine.split(':')[4:])
        # GetObjects
        kickChannel = self.getChannelByName(kickChannelName)
        kickClient = self.getUserByName(kickClientName)
        # Log, if applicable
        self.mHallo.getPrinter().output(Function.EVENT_KICK, kickMessage, self, kickClient, kickChannel)
        self.mHallo.getLogger().log(Function.EVENT_KICK, kickMessage, self, kickClient, kickChannel)
        # Remove kicked user from user list
        kickChannel.removeUser(kickClient)
        # If it was the bot who was kicked, set "in channel" status to False
        if kickClient.getName() == self.getNick():
            kickChannel.setInChannel(False)
        # Pass to passive FunctionDispatcher
        functionDispatcher = self.mHallo.getFunctionDispatcher()
        functionDispatcher.dispatchPassive(Function.EVENT_KICK, kickMessage, self, kickClient, kickChannel)

    def parseLineNumeric(self, numericLine, motdEnded=True):
        """
        Parses a numeric message from the server
        :type numericLine: str Numeric type line from server.
        :type motdEnded: bool Whether MOTD has ended.
        """
        # Parse out numeric line data
        numericCode = numericLine.split()[1]
        # Print to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] Numeric server info: ' + numericLine)
        # TODO: add logging?
        # Check for a 433 "ERR_NICKNAMEINUSE"
        if numericCode == "433":
            nickNumber = \
                ([self.mNick[x:] for x in range(len(self.mNick)) if Commons.isFloatString(self.mNick[x:])] + [None])[0]
            if nickNumber is None:
                nickNumber = 0
                nickWord = self.mNick
            else:
                nickWord = self.mNick[:-len(nickNumber)]
                nickNumber = float(nickNumber)
            newNick = nickWord + str(nickNumber + 1)
            self.mNick = newNick
            self.send("NICK" + self.getNick(), None, "raw")
            return
        # Only process further numeric codes if motd has ended
        if not motdEnded:
            return
        # Check for ISON response, telling you which users are online
        if numericCode == "303":
            # Parse out data
            usersOnline = ':'.join(numericLine.split(':')[2:])
            usersOnlineList = usersOnline.split()
            # Mark them all as online
            for userName in usersOnlineList:
                userObj = self.getUserByName(userName)
                userObj.setOnline(True)
            # Check if users are being checked
            if all([usersOnlineList in self.mCheckUsersOnlineCheckList]):
                self.mCheckUsersOnlineOnlineList = usersOnlineList
        # Check for NAMES request reply, telling you who is in a channel.
        elif numericCode == "353":
            # Parse out data
            channelName = numericLine.split(':')[1].split()[-1].lower()
            channelUserList = ':'.join(numericLine.split(':')[2:]).split()
            # Get channel object
            channelObject = self.getChannelByName(channelName)
            # Set all users online and in channel
            channelObject.setUserList(set())
            for userName in channelUserList:
                while userName[0] in ['~', '&', '@', '%', '+']:
                    userName = userName[1:]
                userObj = self.getUserByName(userName)
                userObj.setOnline(True)
                channelObject.addUser(userObj)
            # Check channel is being checked
            if channelObject == self.mCheckChannelUserListChannel:
                # Set user list
                self.mCheckChannelUserListUserList = channelUserList

    def parseLineUnhandled(self, unhandledLine):
        """
        Parses an unhandled message from the server
        :param unhandledLine: str Otherwise unhandled line from the server
        """
        # Print it to console
        print(Commons.currentTimestamp() + ' [' + self.mName + '] Unhandled data: ' + unhandledLine)

    def parseLineRaw(self, rawLine, lineType):
        """Handed all raw data, along with the type of message
        :param rawLine: str Raw line from the server
        :param lineType: str Event or type of the line
        """
        pass

    def readLineFromSocket(self):
        """Private method to read a line from the IRC socket."""
        nextLine = b""
        while self.mOpen:
            try:
                nextByte = self.mSocket.recv(1)
            except:
                # Raise an exception, to reconnect.
                raise ServerException
            if nextByte is None or len(nextByte) != 1:
                raise ServerException
            nextLine = nextLine + nextByte
            if nextLine.endswith(endl.encode()):
                return self.decodeLine(nextLine[:-len(endl)])

    def decodeLine(self, rawBytes):
        """Decodes a line of bytes, trying a couple character sets
        :param rawBytes: Array bytes to be decoded to string.
        """
        try:
            outputLine = rawBytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                outputLine = rawBytes.decode('iso-8859-1')
            except UnicodeDecodeError:
                outputLine = rawBytes.decode('cp1252')
        return outputLine

    def checkChannelUserList(self, channelObject):
        """
        Checks and updates the user list of a specified channel
        :param channelObject: Channel to check user list of
        """
        # get lock
        self.mCheckChannelUserListLock.acquire()
        self.mCheckChannelUserListChannel = channelObject
        self.mCheckChannelUserListUserList = None
        # send request
        self.send("NAMES " + channelObject.getName(), None, "raw")
        # loop for 5 seconds
        for _ in range(10):
            # if reply is here
            if self.mCheckChannelUserListUserList is not None:
                # use response
                userObjectList = set()
                for userName in self.mCheckChannelUserListUserList:
                    # Strip flags from user name
                    while userName[0] in ['~', '&', '@', '%', '+']:
                        userName = userName[1:]
                    userObject = self.getUserByName(userName)
                    userObject.setOnline(True)
                    userObjectList.add(userObject)
                channelObject.setUserList(userObjectList)
                # release lock
                self.mCheckChannelUserListChannel = None
                self.mCheckChannelUserListUserList = None
                self.mCheckChannelUserListLock.release()
                # return
                return
            # sleep 0.5seconds
            time.sleep(0.5)
        # release lock
        self.mCheckChannelUserListChannel = None
        self.mCheckChannelUserListUserList = None
        self.mCheckChannelUserListLock.release()
        # return
        return

    def checkUsersOnline(self, checkUserList):
        """
        Checks a list of users to see which are online, returns a list of online users
        :param checkUserList: List of names of users to check online status of
        """
        # get lock
        self.mCheckChannelUserListLock.aquire()
        self.mCheckUsersOnlineCheckList = checkUserList
        self.mCheckUsersOnlineOnlineList = None
        # send request
        self.send("ISON " + " ".join(checkUserList), None, "raw")
        # loop for 5 seconds
        for _ in range(10):
            # if reply is here
            if self.mCheckUsersOnlineOnlineList is not None:
                # use response
                for userName in self.mCheckUsersOnlineCheckList:
                    userObject = self.getUserByName(userName)
                    if userName in self.mCheckUsersOnlineOnlineList:
                        userObject.setOnline(True)
                    else:
                        userObject.setOnline(False)
                # release lock
                response = self.mCheckUsersOnlineOnlineList
                self.mCheckUsersOnlineCheckList = None
                self.mCheckUsersOnlineOnlineList = None
                self.mCheckUsersOnlineLock.release()
                # return response
                return response
            # sleep 0.5 seconds
            time.sleep(0.5)
        # release lock
        self.mCheckUsersOnlineCheckList = None
        self.mCheckUsersOnlineOnlineList = None
        self.mCheckUsersOnlineLock.release()
        # return empty list
        return []

    def checkUserIdentity(self, userObject):
        """
        Check if a user is identified and verified
        :param userObject: User to check identity and verification for
        """
        if self.mNickservNick is None or self.mNickservIdentCommand is None:
            return False
        # get nickserv object
        nickservObject = self.getUserByName(self.mNickservNick)
        # get check user lock
        self.mCheckUserIdentityLock.aquire()
        self.mCheckUserIdentityUser = userObject.getName()
        self.mCheckUserIdentityResult = None
        # send whatever request
        self.send(self.mNickservIdentCommand + " " + userObject.getName(), nickservObject, "message")
        # loop for 5 seconds
        for _ in range(10):
            # if response
            if self.mCheckUserIdentityResult is not None:
                # use response
                response = self.mCheckUserIdentityResult
                # release lock
                self.mCheckUserIdentityUser = None
                self.mCheckUserIdentityResult = None
                self.mCheckUserIdentityLock.release()
                # return
                return response
            # sleep 0.5
            time.sleep(0.5)
        # release lock
        self.mCheckUserIdentityUser = None
        self.mCheckUserIdentityResult = None
        self.mCheckUserIdentityLock.release()
        # return false
        return False

    def toXml(self):
        """
        Returns an XML representation of the server object
        """
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("server")
        doc.appendChild(root)
        # create type element
        typeElement = doc.createElement("server_type")
        typeElement.appendChild(doc.createTextNode(self.getType()))
        root.appendChild(typeElement)
        # create name element
        nameElement = doc.createElement("server_name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        # create auto connect element
        autoConnectElement = doc.createElement("auto_connect")
        autoConnectElement.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.mAutoConnect]))
        root.appendChild(autoConnectElement)
        # create channel list
        channelListElement = doc.createElement("channel_list")
        for channelItem in self.mChannelList:
            if channelItem.isPersistent():
                channelElement = minidom.parseString(channelItem.toXml()).firstChild
                channelListElement.appendChild(channelElement)
        root.appendChild(channelListElement)
        # create user list
        userListElement = doc.createElement("user_list")
        for userItem in self.mUserList:
            if userItem.isPersistent():
                userElement = minidom.parseString(userItem.toXml()).firstChild
                userListElement.appendChild(userElement)
        root.appendChild(userListElement)
        # create nick element
        if self.mNick is not None:
            nickElement = doc.createElement("server_nick")
            nickElement.appendChild(doc.createTextNode(self.mNick))
            root.appendChild(nickElement)
        # create prefix element
        if self.mPrefix is not None:
            prefixElement = doc.createElement("server_prefix")
            prefixElement.appendChild(doc.createTextNode(self.mPrefix))
            root.appendChild(prefixElement)
        # create full name element
        if self.mFullName is not None:
            fullNameElement = doc.createElement("full_name")
            fullNameElement.appendChild(doc.createTextNode(self.mFullName))
            root.appendChild(fullNameElement)
        # create server address element
        serverAddressElement = doc.createElement("server_address")
        serverAddressElement.appendChild(doc.createTextNode(self.mServerAddress))
        root.appendChild(serverAddressElement)
        # create server port element
        serverPortElement = doc.createElement("server_port")
        serverPortElement.appendChild(doc.createTextNode(str(self.mServerPort)))
        root.appendChild(serverPortElement)
        # Create nickserv element
        if self.mNickservNick is not None:
            nickservElement = doc.createElement("nickserv")
            # Nickserv nick element
            nickservNickElement = doc.createElement("nick")
            nickservNickElement.appendChild(doc.createTextNode(self.mNickservNick))
            nickservElement.appendChild(nickservNickElement)
            # Nickserv password element
            if self.mNickservPass is not None:
                nickservPassElement = doc.createElement("password")
                nickservPassElement.appendChild(doc.createTextNode(self.mNickservPass))
                nickservElement.appendChild(nickservPassElement)
            # Nickserv identity check command element
            if self.mNickservIdentCommand is not None:
                nickservIdentCommandElement = doc.createElement("identity_command")
                nickservIdentCommandElement.appendChild(doc.createTextNode(self.mNickservIdentCommand))
                nickservElement.appendChild(nickservIdentCommandElement)
                # Nickserv identity check response element
                nickservIdentResponseElement = doc.createElement("identity_response")
                nickservIdentResponseElement.appendChild(doc.createTextNode(self.mNickservIdentResponse))
                nickservElement.appendChild(nickservIdentResponseElement)
            # Add nickserv element to document
            root.appendChild(nickservElement)
        # create permission_mask element
        if not self.mPermissionMask.isEmpty():
            permissionMaskElement = minidom.parse(self.mPermissionMask.toXml()).firstChild
            root.appendChild(permissionMaskElement)
        # output XML string
        return doc.toxml()

    def setNick(self, nick):
        """
        Nick setter
        :param nick: New nickname to use on the server
        """
        oldNick = self.getNick()
        self.mNick = nick
        if nick != oldNick:
            self.send("NICK " + self.mNick, None, "raw")
            halloUserObject = self.getUserByName(nick)
            # Log in all channel Hallo is in.
            for channel in self.mChannelList:
                if not channel.isInChannel():
                    continue
                self.mHallo.getLogger().logFromSelf(Function.EVENT_CHNAME, oldNick, self, halloUserObject, channel)

    def getType(self):
        """Type getter"""
        return Server.TYPE_IRC

    def getServerPort(self):
        """mServerPort getter"""
        return self.mServerPort

    def getNickservNick(self):
        """mNickservNick getter"""
        return self.mNickservNick

    def setNickservNick(self, nickservNick):
        """
        mNickservNick setter
        :param nickservNick: Nickname of the nickserv service on this server
        """
        self.mNickservNick = nickservNick

    def getNickservIdentityCommand(self):
        """mNickservIdentityCommand getter"""
        return self.mNickservIdentCommand

    def setNickservIdentityCommand(self, nickservIdentityCommand):
        """mNickservIdentityCommand setter
        :param nickservIdentityCommand: Command to identify to nickserv service on this server
        """
        self.mNickservIdentCommand = nickservIdentityCommand

    def getNickservIdentityResponse(self):
        """mNickservIdentityResponse getter"""
        return self.mNickservIdentResponse

    def setNickservIdentityResponse(self, nickservIdentityResponse):
        """
        mNickservIdentityResponse setter
        :param nickservIdentityResponse: Regex to search for to validate identity in response to identify command
        """
        self.mNickservIdentResponse = nickservIdentityResponse

    def getNickservPass(self):
        """mNickservPass getter"""
        return self.mNickservPass

    def setNickservPass(self, nickservPass):
        """
        mNickservPass setter
        :param nickservPass: Nickserv password for hallo to identify
        """
        self.mNickservPass = nickservPass
        if self.mNickservPass is not None:
            self.send('IDENTIFY ' + self.mNickservPass, self.getUserByName("nickserv"))

    @staticmethod
    def fromXml(xmlString, hallo):
        """
        Constructor to build a new server object from xml
        :param xmlString: XML string representation of IRC server configuration
        :param hallo: Hallo object which is connected to this server
        """
        doc = minidom.parseString(xmlString)
        newServer = ServerIRC(hallo)
        newServer.mName = doc.getElementsByTagName("server_name")[0].firstChild.data
        newServer.mAutoConnect = Commons.stringFromFile(doc.getElementsByTagName("auto_connect")[0].firstChild.data)
        if len(doc.getElementsByTagName("server_nick")) != 0:
            newServer.mNick = doc.getElementsByTagName("server_nick")[0].firstChild.data
        if len(doc.getElementsByTagName("server_prefix")) != 0:
            newServer.mPrefix = doc.getElementsByTagName("server_prefix")[0].firstChild.data
        if len(doc.getElementsByTagName("full_name")) != 0:
            newServer.mFullName = doc.getElementsByTagName("full_name")[0].firstChild.data
        newServer.mServerAddress = doc.getElementsByTagName("server_address")[0].firstChild.data
        newServer.mServerPort = int(doc.getElementsByTagName("server_port")[0].firstChild.data)
        if len(doc.getElementsByTagName("nickserv")) == 0:
            newServer.mNickservNick = None
            newServer.mNickservPass = None
            newServer.mNickservIdentCommand = None
            newServer.mNickservIdentResponse = None
        else:
            nickservElement = doc.getElementsByTagName("nickserv")[0]
            newServer.mNickservNick = nickservElement.getElementsByTagName("nick")[0].firstChild.data
            if len(nickservElement.getElementsByTagName("identity_command")) == 0:
                newServer.mNickservIdentCommand = None
                newServer.mNickservIdentResponse = None
            else:
                newServer.mNickservIdentCommand = nickservElement.getElementsByTagName("identity_command")[
                    0].firstChild.data
                newServer.mNickservIdentResponse = nickservElement.getElementsByTagName("identity_response")[
                    0].firstChild.data
            if len(nickservElement.getElementsByTagName("password")) != 0:
                newServer.mNickservPass = nickservElement.getElementsByTagName("password")[0].firstChild.data
        # Load channels
        channelListXml = doc.getElementsByTagName("channel_list")[0]
        for channelXml in channelListXml.getElementsByTagName("channel"):
            channelObject = Channel.fromXml(channelXml.toxml(), newServer)
            newServer.addChannel(channelObject)
        # Load users
        userListXml = doc.getElementsByTagName("user_list")[0]
        for userXml in userListXml.getElementsByTagName("user"):
            userObject = User.fromXml(userXml.toxml(), newServer)
            newServer.addUser(userObject)
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            newServer.mPermissionMask = PermissionMask.fromXml(doc.getElementsByTagName("permission_mask")[0].toxml())
        return newServer
