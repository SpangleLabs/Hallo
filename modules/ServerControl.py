from Function import Function
from threading import Thread
import re
from inc.commons import Commons
from Server import Server, ServerIRC


class JoinChannel(Function):
    """
    Joins a channel on a specified server
    """
    # Name for use in help listing
    mHelpName = "join"
    # Names which can be used to address the function
    mNames = {"join channel", "join", "channel"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Join a channel. Password as optional argument. Server can be specified with \"server=<servername>\"." \
                " Format: \"join <channel> <password?>\"."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        # Check for server name in input line
        serverName = self.findParameter("server", line)
        if serverName is None:
            serverObject = userObject.get_server()
        else:
            serverObject = userObject.get_server().getHallo().get_server_by_name(serverName)
            line = line.replace("server=" + serverName, "").strip()
        if serverObject is None:
            return "Invalid server specified."
        # Get channel name
        channelName = line.split()[0].lower()
        # Check for channel password
        channelPassword = None
        if channelName != line:
            channelPassword = line[len(channelName):]
        # Get channel object, set password
        channelObject = serverObject.getChannelByName(channelName)
        channelObject.set_password(channelPassword)
        # Join channel if not already in channel.
        if channelObject.is_in_channel():
            return "I'm already in that channel."
        serverObject.joinChannel(channelObject)
        return "Joined " + channelName + "."

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue


class LeaveChannel(Function):
    """
    Leaves a channel on a specified server
    """
    # Name for use in help listing
    mHelpName = "leave"
    # Names which can be used to address the function
    mNames = {"leave channel", "leave", "part"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Leave a channel. Server can be specified with \"server=<servername>\". Format: \"leave <channel>\"."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        # Check for server name in input line
        serverName = self.findParameter("server", line)
        if serverName is None:
            serverObject = userObject.get_server()
        else:
            serverObject = userObject.get_server().getHallo().get_server_by_name(serverName)
            line = line.replace("server=" + serverName, "").strip()
        if serverObject is None:
            return "Invalid server specified."
        # Find channel object
        channelName = line.split()[0].lower()
        channelObject = serverObject.getChannelByName(channelName)
        # Leave channel, provided hallo is in channel.
        if not channelObject.is_in_channel():
            return "I'm not in that channel."
        serverObject.leaveChannel(channelObject)
        return "Left " + channelName + "."

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue


class Shutdown(Function):
    """
    Shuts down hallo entirely.
    """
    # Name for use in help listing
    mHelpName = "shutdown"
    # Names which can be used to address the Function
    mNames = {"shutdown"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Shuts down hallo entirely."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        serverObject = userObject.get_server()
        halloObject = serverObject.getHallo()
        halloObject.close()
        return "Shutting down."


class Disconnect(Function):
    """
    Disconnects from a Server
    """
    # Name for use in help listing
    mHelpName = "disconnect"
    # Names which can be used to address the Function
    mNames = {"disconnect", "quit"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Disconnects from a server."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        serverObject = userObject.get_server()
        halloObject = serverObject.getHallo()
        if line.strip() != "":
            serverObject = halloObject.get_server_by_name(line)
        if serverObject is None:
            return "Invalid server."
        serverObject.setAutoConnect(False)
        serverObject.disconnect()
        return "Disconnected from server: " + serverObject.getName() + "."


class Connect(Function):
    """
    Connects to a Server
    """
    # Name for use in help listing
    mHelpName = "connect"
    # Names which can be used to address the Function
    mNames = {"connect", "new server"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Connects to an existing or a new server."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """Runs the function"""
        currentServer = userObject.get_server()
        halloObject = currentServer.getHallo()
        # Try and see if it's a server we already know
        existingServer = halloObject.get_server_by_name(line)
        if existingServer is not None:
            return self.connectToKnownServer(existingServer)
        # Try to find what protocol is specififed, or use whatever protocol the user is using.
        lineSplit = line.split()
        validProtocols = [Server.TYPE_IRC]
        serverProtocol = None
        if any([prot in [arg.lower() for arg in lineSplit] for prot in validProtocols]):
            for protocol in validProtocols:
                if protocol in [arg.lower() for arg in lineSplit]:
                    serverProtocol = protocol
                    protocolRegex = re.compile("\s" + protocol + "\s", re.IGNORECASE)
                    line = protocolRegex.sub(" ", line)
                    break
        else:
            serverProtocol = currentServer.getType()
        # Go through protocols branching to whatever function to handle that protocol
        if serverProtocol == Server.TYPE_IRC:
            return self.connectToNewServerIrc(line, userObject, destinationObject)
        # Add in ELIF statements here, to make user Connect Function support other protocols
        else:
            return "Unrecognised server protocol"

    def connectToKnownServer(self, serverObject):
        """Connects to a known server."""
        serverObject.setAutoConnect(True)
        if serverObject.isConnected():
            return "Already connected to that server"
        Thread(target=serverObject.run).start()
        return "Connected to server: " + serverObject.getName() + "."

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue

    def connectToNewServerIrc(self, line, userObject, destinationObject):
        """Processes arguments in order to connect to a new IRC server"""
        # Get some handy objects
        currentServer = userObject.get_server()
        halloObject = currentServer.getHallo()
        # Set all variables to none as default
        serverAddress, serverPort = None, None
        serverName = None
        # Find the URL, if specified
        urlRegex = re.compile("(^|\s)(irc://)?(([a-z.]+\.[a-z]+)(:([0-9]+))?)(\s|$)", re.IGNORECASE)
        urlSearch = urlRegex.search(line)
        if urlSearch is not None:
            line = line.replace(urlSearch.group(0), " ")
            serverAddress = urlSearch.group(4).lower()
            serverPort = int(urlSearch.group(6))
        # Find the serverAddress, if specified with equals notation
        serverAddress = self.findParameter("server_address", line) or serverAddress
        # Find the serverPort, if specified with equals notation
        serverPortParam = self.findParameter("server_port", line)
        if serverPortParam is not None:
            try:
                serverPort = int(serverPortParam)
            except ValueError:
                return "Invalid port number."
        # Check serverAddress and serverPort are set
        if serverAddress is None:
            return "No server address specified."
        if serverPort is None:
            serverPort = currentServer.getServerPort()
        # Get server name
        serverName = self.findParameter("name", line) or serverName
        serverName = self.findParameter("server_name", line) or serverName
        # if server name is null, get it from serverAddress
        if serverName is None:
            serverName = Commons.getDomainName(serverAddress)
        # Get other parameters, if set.
        autoConnect = Commons.stringToBool(self.findParameter("auto_connect", line)) or True
        serverNick = self.findParameter("server_nick", line) or self.findParameter("nick", line)
        serverPrefix = self.findParameter("server_prefix", line) or self.findParameter("prefix", line)
        fullName = self.findParameter("full_name", line)
        nickservNick = "nickserv"
        nickservIdentityCommand = "status"
        nickservIdentityResponse = "^status [^ ]+ 3$"
        nickservPassword = None
        if currentServer.getType() == Server.TYPE_IRC:
            nickservNick = currentServer.getNickservNick()
            nickservIdentityCommand = currentServer.getNickservIdentityCommand()
            nickservIdentityResponse = currentServer.getNickservIdentityResponse()
            nickservPassword = currentServer.getNickservPassword()
        nickservNick = self.findParameter("nickserv_nick", line) or nickservNick
        nickservIdentityCommand = self.findParameter("nickserv_identity_command", line) or nickservIdentityCommand
        nickservIdentityResponse = self.findParameter("nickserv_identity_response", line) or nickservIdentityResponse
        nickservPassword = self.findParameter("nickserv_password", line) or nickservPassword
        # Create this serverIRC object
        newServerObject = ServerIRC(halloObject, serverName, serverAddress, serverPort)
        newServerObject.setAutoConnect(autoConnect)
        newServerObject.setNick(serverNick)
        newServerObject.setPrefix(serverPrefix)
        newServerObject.setFullName(fullName)
        newServerObject.setNickservNick(nickservNick)
        newServerObject.setNickservIdentityCommand(nickservIdentityCommand)
        newServerObject.setNickservIdentityResponse(nickservIdentityResponse)
        newServerObject.setNickservPass(nickservPassword)
        # Add the new object to Hallo's list
        halloObject.add_server(newServerObject)
        # Connect to the new server object.
        Thread(target=newServerObject.run).start()
        return "Connected to new IRC server: " + newServerObject.getName() + "."


class Say(Function):
    """
    Function to enable speaking through hallo
    """
    # Name for use in help listing
    mHelpName = "say"
    # Names which can be used to address the Function
    mNames = {"say", "message", "msg"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Say a message into a channel or server/channel pair (in the format \"{server,channel}\"). " \
                "Format: say <channel> <message>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """
        Say a message into a channel or server/channel pair (in the format "{server,channel}").
        Format: say <channel> <message>
        """
        # Setting up variables
        halloObject = userObject.get_server().getHallo()
        # See if server and channel are specified as parameters
        serverName = self.findParameter("server", line)
        if serverName is not None:
            line = line.replace("server=" + serverName, "").strip()
        channelName = self.findParameter("channel", line)
        if channelName is not None:
            line = line.replace("channel=" + channelName, "").strip()
        # If channelName is not found as a parameter, see if server/channel is given as a first argument pair.
        if channelName is None:
            destinationPair = line.split()[0]
            line = line[len(destinationPair):].strip()
            destinationSeparators = ["->", ">", ",", ".", "/", ":"]
            for destinationSeparator in destinationSeparators:
                if destinationPair.count(destinationSeparator) != 0:
                    serverName = destinationPair.split(destinationSeparator)[0]
                    channelName = destinationPair.split(destinationSeparator)[1]
                    break
            if channelName is None:
                channelName = destinationPair
        # Get serverObj list from serverName
        serverObjs = []
        if serverName is None:
            serverObjs = [userObject.get_server()]
        else:
            # Create a regex query from their input
            serverRegex = re.escape(serverName).replace("\*", ".*")
            serverList = halloObject.get_server_list()
            for serverObj in serverList:
                if not serverObj.isConnected():
                    continue
                if re.match(serverRegex, serverObj.getName(), re.IGNORECASE):
                    serverObjs.append(serverObj)
        # If server is not recognised or found, respond with an error
        if len(serverObjs) == 0:
            return "Unrecognised server."
        # Get channelObj list from serverObj and channelName
        channelObjs = []
        for serverObj in serverObjs:
            channelRegex = re.escape(channelName).replace("\*", ".*")
            channelList = serverObj.getChannelList()
            for channelObj in channelList:
                if not channelObj.is_in_channel():
                    continue
                if re.match(channelRegex, channelObj.get_name(), re.IGNORECASE):
                    channelObjs.append(channelObj)
        # If no channels were found that match, respond with an error
        if len(channelObjs) == 0:
            return "Unrecognised channel."
        # Send message to all matching channels
        for channelObj in channelObjs:
            channelObj.send(line)
        return "Message sent."

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue


class EditServer(Function):
    """
    Edits a Server
    """
    # Name for use in help listing
    mHelpName = "edit server"
    # Names which can be used to address the Function
    mNames = {"edit server", "server edit"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Edits a server's configuration."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """Runs the function"""
        currentServer = userObject.get_server()
        halloObject = currentServer.getHallo()
        # Split line, to find server name
        lineSplit = line.split()
        serverName = lineSplit[0]
        # See is a server by this name is known
        serverObject = halloObject.get_server_by_name(serverName)
        if serverObject is None:
            return "This is not a recognised server name. Please specify server name, " \
                   "then whichever variables and values you wish to set. In variable=value pairs."
        # Get protocol and go through protocols branching to whatever function to handle modifying servers of it.
        serverProtocol = serverObject.getType()
        if serverProtocol == Server.TYPE_IRC:
            return self.editServerIrc(line, serverObject, userObject, destinationObject)
        # Add in ELIF statements here, to make user Connect Function support other protocols
        else:
            return "Unrecognised server protocol"

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue

    def editServerIrc(self, line, serverObject, userObject, destinationObject):
        """Processes arguments in order to edit an IRC server"""
        # Set all variables to none as default
        serverAddress, serverPort = None, None
        # Find the URL, if specified
        urlRegex = re.compile("(^|\s)(irc://)?(([a-z.]+\.[a-z]+)(:([0-9]+))?)(\s|$)", re.IGNORECASE)
        urlSearch = urlRegex.search(line)
        if urlSearch is not None:
            line = line.replace(urlSearch.group(0), " ")
            serverAddress = urlSearch.group(4).lower()
            serverPort = int(urlSearch.group(6))
        # Find the serverAddress, if specified with equals notation
        serverAddress = self.findParameter("server_address", line) or serverAddress
        # Find the serverPort, if specified with equals notation
        serverPortParam = self.findParameter("server_port", line)
        if serverPortParam is not None:
            try:
                serverPort = int(serverPortParam)
            except ValueError:
                return "Invalid port number."
        # If serverAddress or serverPort are set, edit those and reconnect.
        if serverAddress is not None:
            serverObject.setServerAddress(serverAddress)
        if serverPort is not None:
            serverObject.setServerPort(serverPort)
        # Get other parameters, if set. defaulting to whatever server defaults.
        autoConnect = Commons.stringToBool(self.findParameter("auto_connect", line)) or serverObject.getAutoConnect()
        serverNick = self.findParameter("server_nick", line) or self.findParameter("nick",
                                                                                   line) or serverObject.getNick()
        serverPrefix = self.findParameter("server_prefix", line) or self.findParameter("prefix",
                                                                                       line) or serverObject.getPrefix()
        fullName = self.findParameter("full_name", line) or serverObject.getFullName()
        nickservNick = self.findParameter("nickserv_nick", line) or serverObject.getNickservNick()
        nickservIdentityCommand = self.findParameter("nickserv_identity_command",
                                                     line) or serverObject.getNickservIdentityCommand()
        nickservIdentityResponse = self.findParameter("nickserv_identity_response",
                                                      line) or serverObject.getNickservIdentityResponse()
        nickservPassword = self.findParameter("nickserv_password", line) or serverObject.getNickservPass()
        # Set all the new variables
        serverObject.setAutoConnect(autoConnect)
        serverObject.setNick(serverNick)
        serverObject.setPrefix(serverPrefix)
        serverObject.setFullName(fullName)
        serverObject.setNickservNick(nickservNick)
        serverObject.setNickservIdentityCommand(nickservIdentityCommand)
        serverObject.setNickservIdentityResponse(nickservIdentityResponse)
        serverObject.getNickservPass(nickservPassword)
        # If server address or server port was changed, reconnect.
        if serverPort is not None or serverAddress is not None:
            serverObject.reconnect()
        return "Modified the IRC server: " + serverObject.getName() + "."


class ListUsers(Function):
    """
    Lists users in a specified channel.
    """
    # Name for use in help listing
    mHelpName = "list users"
    # Names which can be used to address the Function
    mNames = {"list users", "nick list", "nicklist", "list channel"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a user list for a given channel."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        lineClean = line.strip().lower()
        # Useful object
        halloObject = userObject.get_server().getHallo()
        # See if a server was specified.
        serverName = self.findParameter("server", line)
        # Get server object. If invalid, use current
        if serverName is None:
            serverObject = userObject.get_server()
        else:
            serverObject = halloObject.get_server_by_name(serverName)
            if serverObject is None:
                return "I don't recognise that server name."
            # Remove server name from line and trim
            lineClean = lineClean.replace("server=" + serverName, "").strip()
        # See if channel was specified with equals syntax
        channelName = self.findParameter("channel", lineClean) or self.findParameter("chan", lineClean)
        # If not specified with equals syntax, check if just said.
        if channelName is None:
            channelName = lineClean
        if channelName == "":
            if destinationObject is None or not destinationObject.is_channel():
                return "I don't recognise that channel name."
            channelName = destinationObject.get_name()
        # If they've specified all channels, display the server list.
        if channelName in ["*", "all"]:
            outputString = "Users on " + serverObject.getName() + ": "
            userList = serverObject.getUserList()
            outputString += ", ".join([user.get_name() for user in userList if user.is_online()])
            outputString += "."
            return outputString
        # Get channel object
        channelObject = serverObject.getChannelByName(channelName)
        # Get user list
        userList = channelObject.get_user_list()
        # Output
        outputString = "Users in " + channelName + ": "
        outputString += ", ".join([user.get_name() for user in userList])
        outputString += "."
        return outputString

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue


class ListChannels(Function):
    """
    Lists channels in a specified server, or for all of hallo.
    """
    # Name for use in help listing
    mHelpName = "list channels"
    # Names which can be used to address the Function
    mNames = {"list channels", "channel list", "chanlist", "channels"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Hallo will tell you which channels he is in. Format: \"list channels\" " \
                "for channels on current server, \"list channels all\" for all channels on all servers."

    HALLO_NAMES = ["hallo", "core", "all", "*", "default"]
    SERVER_NAMES = ["server", "serv", "s"]

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        """
        Hallo will tell you which channels he is in, ops only.
        Format: "channels" for channels on current server, "channels all" for all channels on all servers.
        """
        lineClean = line.strip().lower()
        halloObject = userObject.get_server().getHallo()
        # If they ask for all channels, give them all channels.
        if lineClean in self.HALLO_NAMES:
            outputString = "On all servers, I am on these channels: "
            serverList = halloObject.get_server_list()
            channelTitleList = []
            for serverObject in serverList:
                serverName = serverObject.getName()
                inChannelNameList = self.getInChannelNamesList(serverObject)
                channelTitleList += [serverName + "-" + channelName for channelName in inChannelNameList]
            outputString += ', '.join(channelTitleList)
            outputString += "."
            return outputString
        # If nothing specified, or "server", then output current server channel list
        if lineClean == "" or lineClean in self.SERVER_NAMES:
            serverObject = userObject.get_server()
            inChannelNameList = self.getInChannelNamesList(serverObject)
            outputString = "On this server, I'm in these channels: "
            outputString += ', '.join(inChannelNameList) + "."
            return outputString
        # If a server is specified, get that server's channel list
        if self.findAnyParameter(self.SERVER_NAMES, lineClean):
            serverName = lineClean.split("=")[1]
            serverObject = halloObject.get_server_by_name(serverName)
            if serverObject is None:
                return "I don't recognise that server name."
            inChannelNameList = self.getInChannelNamesList(serverObject)
            outputString = "On " + serverObject.getName() + " server, I'm in these channels: "
            outputString += ', '.join(inChannelNameList) + "."
            return outputString
        # Check if whatever input they gave is a server
        serverObject = halloObject.get_server_by_name(lineClean)
        if serverObject is None:
            # Otherwise, return an error
            outputString = "I don't understand your input, please specify a server, or hallo, " \
                           "or no input to get the current server's list"
            return outputString
        inChannelNameList = self.getInChannelNamesList(serverObject)
        outputString = "On " + serverObject.getName() + " server, I'm in these channels: "
        outputString += ', '.join(inChannelNameList) + "."
        return outputString

    def findParameter(self, paramName, line):
        """Finds a parameter value in a line, if the format parameter=value exists in the line"""
        paramValue = None
        paramRegex = re.compile("(^|\s)" + paramName + "=([^\s]+)(\s|$)", re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if paramSearch is not None:
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self, paramList, line):
        """Finds one of any parameter in a line."""
        for paramName in paramList:
            if self.findParameter(paramName, line) is not None:
                return True
        return False

    def getInChannelNamesList(self, serverObject):
        channelList = serverObject.getChannelList()
        inChannelList = [channel for channel in channelList if channel.is_in_channel()]
        inChannelNamesList = [channel.get_name() for channel in inChannelList]
        return inChannelNamesList
