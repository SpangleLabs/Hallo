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
    help_name = "join"
    # Names which can be used to address the function
    names = {"join channel", "join", "channel"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Join a channel. Password as optional argument. Server can be specified with \"server=<servername>\"." \
                " Format: \"join <channel> <password?>\"."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Check for server name in input line
        serverName = self.findParameter("server", line)
        if serverName is None:
            serverObject = user_obj.get_server()
        else:
            serverObject = user_obj.get_server().get_hallo().get_server_by_name(serverName)
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
        channelObject = serverObject.get_channel_by_name(channelName)
        channelObject.set_password(channelPassword)
        # Join channel if not already in channel.
        if channelObject.is_in_channel():
            return "I'm already in that channel."
        serverObject.join_channel(channelObject)
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
    help_name = "leave"
    # Names which can be used to address the function
    names = {"leave channel", "leave", "part"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Leave a channel. Server can be specified with \"server=<servername>\". Format: \"leave <channel>\"."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Check for server name in input line
        serverName = self.findParameter("server", line)
        if serverName is None:
            serverObject = user_obj.get_server()
        else:
            serverObject = user_obj.get_server().get_hallo().get_server_by_name(serverName)
            line = line.replace("server=" + serverName, "").strip()
        if serverObject is None:
            return "Invalid server specified."
        # Find channel object
        channelName = line.split()[0].lower()
        channelObject = serverObject.get_channel_by_name(channelName)
        # Leave channel, provided hallo is in channel.
        if not channelObject.is_in_channel():
            return "I'm not in that channel."
        serverObject.leave_channel(channelObject)
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
    help_name = "shutdown"
    # Names which can be used to address the Function
    names = {"shutdown"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Shuts down hallo entirely."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        serverObject = user_obj.get_server()
        halloObject = serverObject.get_hallo()
        halloObject.close()
        return "Shutting down."


class Disconnect(Function):
    """
    Disconnects from a Server
    """
    # Name for use in help listing
    help_name = "disconnect"
    # Names which can be used to address the Function
    names = {"disconnect", "quit"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Disconnects from a server."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        serverObject = user_obj.get_server()
        halloObject = serverObject.get_hallo()
        if line.strip() != "":
            serverObject = halloObject.get_server_by_name(line)
        if serverObject is None:
            return "Invalid server."
        serverObject.set_auto_connect(False)
        serverObject.disconnect()
        return "Disconnected from server: " + serverObject.get_name() + "."


class Connect(Function):
    """
    Connects to a Server
    """
    # Name for use in help listing
    help_name = "connect"
    # Names which can be used to address the Function
    names = {"connect", "new server"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Connects to an existing or a new server."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """Runs the function"""
        currentServer = user_obj.get_server()
        halloObject = currentServer.get_hallo()
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
            serverProtocol = currentServer.get_type()
        # Go through protocols branching to whatever function to handle that protocol
        if serverProtocol == Server.TYPE_IRC:
            return self.connectToNewServerIrc(line, user_obj, destination_obj)
        # Add in ELIF statements here, to make user Connect Function support other protocols
        else:
            return "Unrecognised server protocol"

    def connectToKnownServer(self, serverObject):
        """Connects to a known server."""
        serverObject.set_auto_connect(True)
        if serverObject.is_connected():
            return "Already connected to that server"
        Thread(target=serverObject.run).start()
        return "Connected to server: " + serverObject.get_name() + "."

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
        halloObject = currentServer.get_hallo()
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
            serverPort = currentServer.get_server_port()
        # Get server name
        serverName = self.findParameter("name", line) or serverName
        serverName = self.findParameter("server_name", line) or serverName
        # if server name is null, get it from serverAddress
        if serverName is None:
            serverName = Commons.get_domain_name(serverAddress)
        # Get other parameters, if set.
        autoConnect = Commons.string_to_bool(self.findParameter("auto_connect", line)) or True
        serverNick = self.findParameter("server_nick", line) or self.findParameter("nick", line)
        serverPrefix = self.findParameter("server_prefix", line) or self.findParameter("prefix", line)
        fullName = self.findParameter("full_name", line)
        nickservNick = "nickserv"
        nickservIdentityCommand = "status"
        nickservIdentityResponse = "^status [^ ]+ 3$"
        nickservPassword = None
        if currentServer.get_type() == Server.TYPE_IRC:
            nickservNick = currentServer.get_nickserv_nick()
            nickservIdentityCommand = currentServer.get_nickserv_ident_command()
            nickservIdentityResponse = currentServer.get_nickserv_ident_response()
            nickservPassword = currentServer.getNickservPassword()
        nickservNick = self.findParameter("nickserv_nick", line) or nickservNick
        nickservIdentityCommand = self.findParameter("nickserv_identity_command", line) or nickservIdentityCommand
        nickservIdentityResponse = self.findParameter("nickserv_identity_response", line) or nickservIdentityResponse
        nickservPassword = self.findParameter("nickserv_password", line) or nickservPassword
        # Create this serverIRC object
        newServerObject = ServerIRC(halloObject, serverName, serverAddress, serverPort)
        newServerObject.set_auto_connect(autoConnect)
        newServerObject.set_nick(serverNick)
        newServerObject.set_prefix(serverPrefix)
        newServerObject.set_full_name(fullName)
        newServerObject.set_nickserv_nick(nickservNick)
        newServerObject.set_nickserv_ident_command(nickservIdentityCommand)
        newServerObject.set_nickserv_ident_response(nickservIdentityResponse)
        newServerObject.set_nickserv_pass(nickservPassword)
        # Add the new object to Hallo's list
        halloObject.add_server(newServerObject)
        # Connect to the new server object.
        Thread(target=newServerObject.run).start()
        return "Connected to new IRC server: " + newServerObject.get_name() + "."


class Say(Function):
    """
    Function to enable speaking through hallo
    """
    # Name for use in help listing
    help_name = "say"
    # Names which can be used to address the Function
    names = {"say", "message", "msg"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Say a message into a channel or server/channel pair (in the format \"{server,channel}\"). " \
                "Format: say <channel> <message>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """
        Say a message into a channel or server/channel pair (in the format "{server,channel}").
        Format: say <channel> <message>
        """
        # Setting up variables
        halloObject = user_obj.get_server().get_hallo()
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
            serverObjs = [user_obj.get_server()]
        else:
            # Create a regex query from their input
            serverRegex = re.escape(serverName).replace("\*", ".*")
            serverList = halloObject.get_server_list()
            for serverObj in serverList:
                if not serverObj.is_connected():
                    continue
                if re.match(serverRegex, serverObj.get_name(), re.IGNORECASE):
                    serverObjs.append(serverObj)
        # If server is not recognised or found, respond with an error
        if len(serverObjs) == 0:
            return "Unrecognised server."
        # Get channelObj list from serverObj and channelName
        channelObjs = []
        for serverObj in serverObjs:
            channelRegex = re.escape(channelName).replace("\*", ".*")
            channelList = serverObj.get_channel_list()
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
    help_name = "edit server"
    # Names which can be used to address the Function
    names = {"edit server", "server edit"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Edits a server's configuration."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """Runs the function"""
        currentServer = user_obj.get_server()
        halloObject = currentServer.get_hallo()
        # Split line, to find server name
        lineSplit = line.split()
        serverName = lineSplit[0]
        # See is a server by this name is known
        serverObject = halloObject.get_server_by_name(serverName)
        if serverObject is None:
            return "This is not a recognised server name. Please specify server name, " \
                   "then whichever variables and values you wish to set. In variable=value pairs."
        # Get protocol and go through protocols branching to whatever function to handle modifying servers of it.
        serverProtocol = serverObject.get_type()
        if serverProtocol == Server.TYPE_IRC:
            return self.editServerIrc(line, serverObject, user_obj, destination_obj)
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
        autoConnect = Commons.string_to_bool(self.findParameter("auto_connect", line)) or serverObject.get_auto_connect()
        serverNick = self.findParameter("server_nick", line) or self.findParameter("nick",
                                                                                   line) or serverObject.get_nick()
        serverPrefix = self.findParameter("server_prefix", line) or self.findParameter("prefix",
                                                                                       line) or serverObject.get_prefix()
        fullName = self.findParameter("full_name", line) or serverObject.get_full_name()
        nickservNick = self.findParameter("nickserv_nick", line) or serverObject.get_nickserv_nick()
        nickservIdentityCommand = self.findParameter("nickserv_identity_command",
                                                     line) or serverObject.get_nickserv_ident_command()
        nickservIdentityResponse = self.findParameter("nickserv_identity_response",
                                                      line) or serverObject.get_nickserv_ident_response()
        nickservPassword = self.findParameter("nickserv_password", line) or serverObject.get_nickserv_pass()
        # Set all the new variables
        serverObject.set_auto_connect(autoConnect)
        serverObject.set_nick(serverNick)
        serverObject.set_prefix(serverPrefix)
        serverObject.set_full_name(fullName)
        serverObject.set_nickserv_nick(nickservNick)
        serverObject.set_nickserv_ident_command(nickservIdentityCommand)
        serverObject.set_nickserv_ident_response(nickservIdentityResponse)
        serverObject.get_nickserv_pass(nickservPassword)
        # If server address or server port was changed, reconnect.
        if serverPort is not None or serverAddress is not None:
            serverObject.reconnect()
        return "Modified the IRC server: " + serverObject.get_name() + "."


class ListUsers(Function):
    """
    Lists users in a specified channel.
    """
    # Name for use in help listing
    help_name = "list users"
    # Names which can be used to address the Function
    names = {"list users", "nick list", "nicklist", "list channel"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Returns a user list for a given channel."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        lineClean = line.strip().lower()
        # Useful object
        halloObject = user_obj.get_server().get_hallo()
        # See if a server was specified.
        serverName = self.findParameter("server", line)
        # Get server object. If invalid, use current
        if serverName is None:
            serverObject = user_obj.get_server()
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
            if destination_obj is None or not destination_obj.is_channel():
                return "I don't recognise that channel name."
            channelName = destination_obj.get_name()
        # If they've specified all channels, display the server list.
        if channelName in ["*", "all"]:
            outputString = "Users on " + serverObject.get_name() + ": "
            userList = serverObject.get_user_list()
            outputString += ", ".join([user.get_name() for user in userList if user.is_online()])
            outputString += "."
            return outputString
        # Get channel object
        channelObject = serverObject.get_channel_by_name(channelName)
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
    help_name = "list channels"
    # Names which can be used to address the Function
    names = {"list channels", "channel list", "chanlist", "channels"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Hallo will tell you which channels he is in. Format: \"list channels\" " \
                "for channels on current server, \"list channels all\" for all channels on all servers."

    HALLO_NAMES = ["hallo", "core", "all", "*", "default"]
    SERVER_NAMES = ["server", "serv", "s"]

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """
        Hallo will tell you which channels he is in, ops only.
        Format: "channels" for channels on current server, "channels all" for all channels on all servers.
        """
        lineClean = line.strip().lower()
        halloObject = user_obj.get_server().get_hallo()
        # If they ask for all channels, give them all channels.
        if lineClean in self.HALLO_NAMES:
            outputString = "On all servers, I am on these channels: "
            serverList = halloObject.get_server_list()
            channelTitleList = []
            for serverObject in serverList:
                serverName = serverObject.get_name()
                inChannelNameList = self.getInChannelNamesList(serverObject)
                channelTitleList += [serverName + "-" + channelName for channelName in inChannelNameList]
            outputString += ', '.join(channelTitleList)
            outputString += "."
            return outputString
        # If nothing specified, or "server", then output current server channel list
        if lineClean == "" or lineClean in self.SERVER_NAMES:
            serverObject = user_obj.get_server()
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
            outputString = "On " + serverObject.get_name() + " server, I'm in these channels: "
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
        outputString = "On " + serverObject.get_name() + " server, I'm in these channels: "
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
        channelList = serverObject.get_channel_list()
        inChannelList = [channel for channel in channelList if channel.is_in_channel()]
        inChannelNamesList = [channel.get_name() for channel in inChannelList]
        return inChannelNamesList
