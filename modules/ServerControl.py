from Function import Function
from threading import Thread
import re
from inc.Commons import Commons
from Server import Server, ServerIRC


class JoinChannel(Function):
    """
    Joins a channel on a specified server
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "join"
        # Names which can be used to address the function
        self.names = {"join channel", "join", "channel"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Join a channel. Password as optional argument. " \
                         "Server can be specified with \"server=<server_name>\"." \
                         " Format: \"join <channel> <password?>\"."

    def run(self, line, user_obj, destination_obj=None):
        # Check for server name in input line
        server_name = Commons.find_parameter("server", line)
        if server_name is None:
            server_obj = user_obj.get_server()
        else:
            server_obj = user_obj.get_server().get_hallo().get_server_by_name(server_name)
            line = line.replace("server=" + server_name, "").strip()
        if server_obj is None:
            return "Invalid server specified."
        # Get channel name
        channel_name = line.split()[0].lower()
        # Check for channel password
        channel_password = None
        if channel_name != line:
            channel_password = line[len(channel_name):]
        # Get channel object, set password
        channel_obj = server_obj.get_channel_by_name(channel_name)
        channel_obj.set_password(channel_password)
        # Join channel if not already in channel.
        if channel_obj.is_in_channel():
            return "I'm already in that channel."
        server_obj.join_channel(channel_obj)
        return "Joined " + channel_name + "."


class LeaveChannel(Function):
    """
    Leaves a channel on a specified server
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "leave"
        # Names which can be used to address the function
        self.names = {"leave channel", "leave", "part"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Leave a channel. Server can be specified with \"server=<server_name>\". " \
                         "Format: \"leave <channel>\"."

    def run(self, line, user_obj, destination_obj=None):
        # Check for server name in input line
        server_name = Commons.find_parameter("server", line)
        if server_name is None:
            server_obj = user_obj.get_server()
        else:
            server_obj = user_obj.get_server().get_hallo().get_server_by_name(server_name)
            line = line.replace("server=" + server_name, "").strip()
        if server_obj is None:
            return "Error, invalid server specified."
        # Find channel object
        if line.strip() != "":
            channel_name = line.split()[0].lower()
            channel_obj = server_obj.get_channel_by_name(channel_name)
        else:
            if destination_obj.is_channel():
                channel_name = destination_obj.get_name()
                channel_obj = destination_obj
            else:
                return "Error, I cannot leave a private chat."
        # Leave channel, provided hallo is in channel.
        if not channel_obj.is_in_channel():
            return "Error, I'm not in that channel."
        server_obj.leave_channel(channel_obj)
        return "Left " + channel_name + "."


class Disconnect(Function):
    """
    Disconnects from a Server
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "disconnect"
        # Names which can be used to address the Function
        self.names = {"disconnect", "quit"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Disconnects from a server."

    def run(self, line, user_obj, destination_obj=None):
        server_obj = user_obj.get_server()
        hallo_obj = server_obj.get_hallo()
        if line.strip() != "":
            server_obj = hallo_obj.get_server_by_name(line)
        if server_obj is None:
            return "Invalid server."
        server_obj.set_auto_connect(False)
        server_obj.disconnect()
        return "Disconnected from server: " + server_obj.get_name() + "."


class Connect(Function):
    """
    Connects to a Server
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "connect"
        # Names which can be used to address the Function
        self.names = {"connect", "new server"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Connects to an existing or a new server. " \
                         "Format: \"connect <protocol> <server>\" or \"connect <already known server name>\""

    def run(self, line, user_obj, destination_obj=None):
        """Runs the function"""
        current_server = user_obj.get_server()
        hallo_obj = current_server.get_hallo()
        # Try and see if it's a server we already know
        existing_server = hallo_obj.get_server_by_name(line)
        if existing_server is not None:
            return self.connect_to_known_server(existing_server)
        # Try to find what protocol is specified, or use whatever protocol the user is using.
        line_split = line.split()
        valid_protocols = [Server.TYPE_IRC]
        server_protocol = None
        if any([prot in [arg.lower() for arg in line_split] for prot in valid_protocols]):
            for protocol in valid_protocols:
                if protocol in [arg.lower() for arg in line_split]:
                    server_protocol = protocol
                    protocol_regex = re.compile("\s" + protocol + "\s", re.IGNORECASE)
                    line = protocol_regex.sub(" ", line)
                    break
        else:
            server_protocol = current_server.get_type()
        # Go through protocols branching to whatever function to handle that protocol
        if server_protocol == Server.TYPE_IRC:
            return self.connect_to_new_server_irc(line, user_obj, destination_obj)
        # Add in elseif statements here, to make user Connect Function support other protocols
        else:
            return "Unrecognised server protocol"

    def connect_to_known_server(self, server_obj):
        """Connects to a known server."""
        server_obj.set_auto_connect(True)
        if server_obj.is_connected():
            return "Already connected to that server"
        Thread(target=server_obj.run).start()
        return "Connected to server: " + server_obj.get_name() + "."

    def connect_to_new_server_irc(self, line, user_obj, destination_obj):
        """Processes arguments in order to connect to a new IRC server"""
        # Get some handy objects
        current_server = user_obj.get_server()
        hallo_obj = current_server.get_hallo()
        # Set all variables to none as default
        server_address, server_port = None, None
        server_name = None
        # Find the URL, if specified
        url_regex = re.compile("(^|\s)(irc://)?(([a-z.]+\.[a-z]+)(:([0-9]+))?)(\s|$)", re.IGNORECASE)
        url_search = url_regex.search(line)
        if url_search is not None:
            line = line.replace(url_search.group(0), " ")
            server_address = url_search.group(4).lower()
            try:
                server_port = int(url_search.group(6))
            except ValueError:
                return "Error, invalid port number"
        # Find the server_address, if specified with equals notation
        server_address = Commons.find_parameter("server_address", line) or server_address
        # Find the server_port, if specified with equals notation
        server_port_param = Commons.find_parameter("server_port", line)
        if server_port_param is not None:
            try:
                server_port = int(server_port_param)
            except (ValueError, TypeError):
                return "Error, invalid port number."
        # Check server_address and server_port are set
        if server_address is None:
            return "Error, No server address specified."
        if server_port is None:
            server_port = current_server.get_server_port()
        # Get server name
        server_name = Commons.find_parameter("name", line) or server_name
        server_name = Commons.find_parameter("server_name", line) or server_name
        # if server name is null, get it from server_address
        if server_name is None:
            server_name = Commons.get_domain_name(server_address)
        # Get other parameters, if set.
        auto_connect = Commons.string_to_bool(Commons.find_parameter("auto_connect", line)) or True
        server_nick = Commons.find_parameter("server_nick", line) or Commons.find_parameter("nick", line)
        server_prefix = Commons.find_parameter("server_prefix", line) or Commons.find_parameter("prefix", line)
        full_name = Commons.find_parameter("full_name", line)
        nickserv_nick = "nickserv"
        nickserv_identity_command = "status"
        nickserv_identity_resp = "^status [^ ]+ 3$"
        nickserv_password = None
        if current_server.get_type() == Server.TYPE_IRC:
            nickserv_nick = current_server.get_nickserv_nick()
            nickserv_identity_command = current_server.get_nickserv_ident_command()
            nickserv_identity_resp = current_server.get_nickserv_ident_response()
            nickserv_password = current_server.get_nickserv_pass()
        nickserv_nick = Commons.find_parameter("nickserv_nick", line) or nickserv_nick
        nickserv_identity_command = Commons.find_parameter("nickserv_identity_command",
                                                           line) or nickserv_identity_command
        nickserv_identity_resp = Commons.find_parameter("nickserv_identity_resp", line) or nickserv_identity_resp
        nickserv_password = Commons.find_parameter("nickserv_password", line) or nickserv_password
        # Create this serverIRC object
        new_server_obj = ServerIRC(hallo_obj, server_name, server_address, server_port)
        new_server_obj.set_auto_connect(auto_connect)
        new_server_obj.set_nick(server_nick)
        new_server_obj.set_prefix(server_prefix)
        new_server_obj.set_full_name(full_name)
        new_server_obj.set_nickserv_nick(nickserv_nick)
        new_server_obj.set_nickserv_ident_command(nickserv_identity_command)
        new_server_obj.set_nickserv_ident_response(nickserv_identity_resp)
        new_server_obj.set_nickserv_pass(nickserv_password)
        # Add the new object to Hallo's list
        hallo_obj.add_server(new_server_obj)
        # Connect to the new server object.
        Thread(target=new_server_obj.run).start()
        return "Connected to new IRC server: " + new_server_obj.get_name() + "."


class Say(Function):
    """
    Function to enable speaking through hallo
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "say"
        # Names which can be used to address the Function
        self.names = {"say", "message", "msg"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Say a message into a channel or server/channel pair (in the format \"{server,channel}\"). " \
                         "Format: say <channel> <message>"

    def run(self, line, user_obj, destination_obj=None):
        """
        Say a message into a channel or server/channel pair (in the format "{server,channel}").
        Format: say <channel> <message>
        """
        # Setting up variables
        hallo_obj = user_obj.get_server().get_hallo()
        # See if server and channel are specified as parameters
        server_name = Commons.find_parameter("server", line)
        if server_name is not None:
            line = line.replace("server=" + server_name, "").strip()
        channel_name = Commons.find_parameter("channel", line)
        if channel_name is not None:
            line = line.replace("channel=" + channel_name, "").strip()
        # If channel_name is not found as a parameter, see if server/channel is given as a first argument pair.
        if channel_name is None:
            destination_pair = line.split()[0]
            line = line[len(destination_pair):].strip()
            destination_separators = ["->", ">", ",", ".", "/", ":"]
            for destination_separator in destination_separators:
                if destination_pair.count(destination_separator) != 0:
                    server_name = destination_pair.split(destination_separator)[0]
                    channel_name = destination_pair.split(destination_separator)[1]
                    break
            if channel_name is None:
                channel_name = destination_pair
        # Get server_obj list from server_name
        server_objs = []
        if server_name is None:
            server_objs = [user_obj.get_server()]
        else:
            # Create a regex query from their input
            server_regex = re.escape(server_name).replace("\*", ".*")
            server_list = hallo_obj.get_server_list()
            for server_obj in server_list:
                if not server_obj.is_connected():
                    continue
                if re.match(server_regex, server_obj.get_name(), re.IGNORECASE):
                    server_objs.append(server_obj)
        # If server is not recognised or found, respond with an error
        if len(server_objs) == 0:
            return "Unrecognised server."
        # Get channel_obj list from server_obj and channel_name
        channel_objs = []
        for server_obj in server_objs:
            channel_regex = re.escape(channel_name).replace("\*", ".*")
            channel_list = server_obj.get_channel_list()
            for channel_obj in channel_list:
                if not channel_obj.is_in_channel():
                    continue
                if re.match(channel_regex, channel_obj.get_name(), re.IGNORECASE):
                    channel_objs.append(channel_obj)
        # If no channels were found that match, respond with an error
        if len(channel_objs) == 0:
            return "Unrecognised channel."
        # Send message to all matching channels
        for channel_obj in channel_objs:
            channel_obj.server.send(line, channel_obj, Server.MSG_MSG)
        return "Message sent."


class EditServer(Function):
    """
    Edits a Server
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "edit server"
        # Names which can be used to address the Function
        self.names = {"edit server", "server edit"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Edits a server's configuration."

    def run(self, line, user_obj, destination_obj=None):
        """Runs the function"""
        current_server = user_obj.get_server()
        hallo_obj = current_server.get_hallo()
        # Split line, to find server name
        line_split = line.split()
        server_name = line_split[0]
        # See is a server by this name is known
        server_obj = hallo_obj.get_server_by_name(server_name)
        if server_obj is None:
            return "This is not a recognised server name. Please specify server name, " \
                   "then whichever variables and values you wish to set. In variable=value pairs."
        # Get protocol and go through protocols branching to whatever function to handle modifying servers of it.
        server_protocol = server_obj.get_type()
        if server_protocol == Server.TYPE_IRC:
            return self.edit_server_irc(line, server_obj, user_obj, destination_obj)
        # Add in ELIF statements here, to make user Connect Function support other protocols
        else:
            return "Unrecognised server protocol"

    def edit_server_irc(self, line, server_obj, user_obj, destination_obj):
        """Processes arguments in order to edit an IRC server"""
        # Set all variables to none as default
        server_address, server_port = None, None
        # Find the URL, if specified
        url_regex = re.compile("(^|\s)(irc://)?(([a-z.]+\.[a-z]+)(:([0-9]+))?)(\s|$)", re.IGNORECASE)
        url_search = url_regex.search(line)
        if url_search is not None:
            line = line.replace(url_search.group(0), " ")
            server_address = url_search.group(4).lower()
            server_port = int(url_search.group(6))
        # Find the server_address, if specified with equals notation
        server_address = Commons.find_parameter("server_address", line) or server_address
        # Find the server_port, if specified with equals notation
        server_port_param = Commons.find_parameter("server_port", line)
        if server_port_param is not None:
            try:
                server_port = int(server_port_param)
            except ValueError:
                return "Invalid port number."
        # If server_address or server_port are set, edit those and reconnect.
        if server_address is not None:
            server_obj.server_address = server_address
        if server_port is not None:
            server_obj.server_port = server_port
        # Get other parameters, if set. defaulting to whatever server defaults.
        auto_connect = Commons.string_to_bool(Commons.find_parameter("auto_connect",
                                                                     line)) or server_obj.get_auto_connect()
        server_nick = Commons.find_parameter("server_nick",
                                             line) or Commons.find_parameter("nick", line) or server_obj.get_nick()
        server_prefix = Commons.find_parameter("server_prefix",
                                               line) or Commons.find_parameter("prefix",
                                                                               line) or server_obj.get_prefix()
        full_name = Commons.find_parameter("full_name", line) or server_obj.get_full_name()
        nickserv_nick = Commons.find_parameter("nickserv_nick", line) or server_obj.get_nickserv_nick()
        nickserv_identity_command = Commons.find_parameter("nickserv_identity_command",
                                                           line) or server_obj.get_nickserv_ident_command()
        nickserv_identity_response = Commons.find_parameter("nickserv_identity_response",
                                                            line) or server_obj.get_nickserv_ident_response()
        nickserv_password = Commons.find_parameter("nickserv_password", line) or server_obj.get_nickserv_pass()
        # Set all the new variables
        server_obj.set_auto_connect(auto_connect)
        server_obj.set_nick(server_nick)
        server_obj.set_prefix(server_prefix)
        server_obj.set_full_name(full_name)
        server_obj.set_nickserv_nick(nickserv_nick)
        server_obj.set_nickserv_ident_command(nickserv_identity_command)
        server_obj.set_nickserv_ident_response(nickserv_identity_response)
        server_obj.get_nickserv_pass(nickserv_password)
        # If server address or server port was changed, reconnect.
        if server_port is not None or server_address is not None:
            server_obj.reconnect()
        return "Modified the IRC server: " + server_obj.get_name() + "."


class ListUsers(Function):
    """
    Lists users in a specified channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "list users"
        # Names which can be used to address the Function
        self.names = {"list users", "nick list", "nicklist", "list channel"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a user list for a given channel."

    def run(self, line, user_obj, destination_obj=None):
        line_clean = line.strip().lower()
        # Useful object
        hallo_obj = user_obj.get_server().get_hallo()
        # See if a server was specified.
        server_name = Commons.find_parameter("server", line)
        # Get server object. If invalid, use current
        if server_name is None:
            server_obj = user_obj.get_server()
        else:
            server_obj = hallo_obj.get_server_by_name(server_name)
            if server_obj is None:
                return "I don't recognise that server name."
            # Remove server name from line and trim
            line_clean = line_clean.replace("server=" + server_name, "").strip()
        # See if channel was specified with equals syntax
        channel_name = Commons.find_parameter("channel", line_clean) or Commons.find_parameter("chan", line_clean)
        # If not specified with equals syntax, check if just said.
        if channel_name is None:
            channel_name = line_clean
        if channel_name == "":
            if destination_obj is None or not destination_obj.is_channel():
                return "I don't recognise that channel name."
            channel_name = destination_obj.get_name()
        # If they've specified all channels, display the server list.
        if channel_name in ["*", "all"]:
            output_string = "Users on " + server_obj.get_name() + ": "
            user_list = server_obj.get_user_list()
            output_string += ", ".join([user.get_name() for user in user_list if user.is_online()])
            output_string += "."
            return output_string
        # Get channel object
        channel_obj = server_obj.get_channel_by_name(channel_name)
        # Get user list
        user_list = channel_obj.get_user_list()
        # Output
        output_string = "Users in " + channel_name + ": "
        output_string += ", ".join([user.get_name() for user in user_list])
        output_string += "."
        return output_string


class ListChannels(Function):
    """
    Lists channels in a specified server, or for all of hallo.
    """

    HALLO_NAMES = ["hallo", "core", "all", "*", "default"]
    SERVER_NAMES = ["server", "serv", "s"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "list channels"
        # Names which can be used to address the Function
        self.names = {"list channels", "channel list", "chanlist", "channels"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Hallo will tell you which channels he is in. Format: \"list channels\" " \
                         "for channels on current server, \"list channels all\" for all channels on all servers."

    def run(self, line, user_obj, destination_obj=None):
        """
        Hallo will tell you which channels he is in, ops only.
        Format: "channels" for channels on current server, "channels all" for all channels on all servers.
        """
        line_clean = line.strip().lower()
        hallo_obj = user_obj.get_server().get_hallo()
        # If they ask for all channels, give them all channels.
        if line_clean in self.HALLO_NAMES:
            output_string = "On all servers, I am on these channels: "
            server_list = hallo_obj.get_server_list()
            channel_title_list = []
            for server_obj in server_list:
                server_name = server_obj.get_name()
                in_channel_name_list = self.get_in_channel_names_list(server_obj)
                channel_title_list += [server_name + "-" + channel_name for channel_name in in_channel_name_list]
            output_string += ', '.join(channel_title_list)
            output_string += "."
            return output_string
        # If nothing specified, or "server", then output current server channel list
        if line_clean == "" or line_clean in self.SERVER_NAMES:
            server_obj = user_obj.get_server()
            in_channel_name_list = self.get_in_channel_names_list(server_obj)
            output_string = "On this server, I'm in these channels: "
            output_string += ', '.join(in_channel_name_list) + "."
            return output_string
        # If a server is specified, get that server's channel list
        if Commons.find_any_parameter(self.SERVER_NAMES, line_clean):
            server_name = line_clean.split("=")[1]
            server_obj = hallo_obj.get_server_by_name(server_name)
            if server_obj is None:
                return "I don't recognise that server name."
            in_channel_name_list = self.get_in_channel_names_list(server_obj)
            output_string = "On " + server_obj.get_name() + " server, I'm in these channels: "
            output_string += ', '.join(in_channel_name_list) + "."
            return output_string
        # Check if whatever input they gave is a server
        server_obj = hallo_obj.get_server_by_name(line_clean)
        if server_obj is None:
            # Otherwise, return an error
            output_string = "I don't understand your input, please specify a server, or hallo, " \
                           "or no input to get the current server's list"
            return output_string
        in_channel_name_list = self.get_in_channel_names_list(server_obj)
        output_string = "On " + server_obj.get_name() + " server, I'm in these channels: "
        output_string += ', '.join(in_channel_name_list) + "."
        return output_string

    def get_in_channel_names_list(self, server_obj):
        channel_list = server_obj.get_channel_list()
        in_channel_list = [channel for channel in channel_list if channel.is_in_channel()]
        in_channel_names_list = [channel.get_name() for channel in in_channel_list]
        return in_channel_names_list
