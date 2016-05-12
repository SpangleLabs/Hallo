from Function import Function
from inc.Commons import Commons
from Server import Server, ServerIRC


class Operator(Function):
    """
    Gives a user on an irc server "operator" status.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "op"
        # Names which can be used to address the function
        self.names = {"op", "operator", "give op", "gib op", "get op", "give operator", "gib operator", "get operator"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Op member in given channel, or current channel if no channel given. Or command user if no " \
                         "member given. Format: op <name> <channel>"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.server
        # If server isn't IRC type, we can't give op.
        if server_obj.type != Server.TYPE_IRC:
            return "Error, this function is only available for IRC servers."
        # If 0 arguments, op user who called command.
        line_split = line.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if destination_obj is None or destination_obj.is_user():
                return "Error, I can't op you in a privmsg, please provide a channel."
            # Give op to the user
            return self.give_op(destination_obj, user_obj)
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is None or destination_obj.is_user():
                channel = server_obj.get_channel_by_name(line)
                return self.give_op(channel, user_obj)
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(line)
            if test_channel.in_channel:
                return self.give_op(test_channel, user_obj)
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(line)
            return self.give_op(destination_obj, target_user)
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            return self.give_op(target_channel, target_user)
        # 2 args, try with second argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[1])
        target_user = server_obj.get_user_by_name(line_split[0])
        return self.give_op(target_channel, target_user)

    def give_op(self, channel, user):
        """
        Gives op to a user in a given channel, after checks.
        :param channel: Channel to give user op in
        :type channel: Destination.Channel
        :param user: User to give op to
        :type user: Destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, "+user.name+" is not in "+channel.name+"."
        # Check if hallo has op in channel
        if not self.hallo_has_op(channel):
            return "Error, I don't have power to give op in "+channel.name+"."
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_op:
            return "Error, this user already has op."
        channel.server.send("MODE "+channel.name+" +o "+user.name, None, Server.MSG_RAW)
        return "Op status given."

    def hallo_has_op(self, channel):
        """
        Checks whether hallo has op in a given channel.
        :param channel: channel to check op status for
        :type channel: Destination.Channel
        :return: whether hallo has op
        :rtype: bool
        """
        server = channel.server
        hallo_user = server.get_user_by_name(server.get_nick())
        hallo_membership = channel.get_membership_by_user(hallo_user)
        return hallo_membership.is_op


class DeOperator(Function):
    """
    Removes a user on an irc server's "operator" status.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "deop"
        # Names which can be used to address the function
        self.names = {"deop", "deoperator", "unoperator", "take op", "del op", "delete op", "remove op",
                      "take operator", "del operator", "delete op", "remove operator"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Deop member in given channel, or current channel if no channel given. Or command user if " \
                         "no member given. Format: deop <name> <channel>"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.server
        # If server isn't IRC type, we can't take op.
        if server_obj.type != Server.TYPE_IRC:
            return "Error, this function is only available for IRC servers."
        # If 0 arguments, de-op user who called command.
        line_split = line.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if destination_obj is None or destination_obj.is_user():
                return "Error, I can't de-op you in a privmsg, please provide a channel."
            # Remove op
            return self.take_op(destination_obj, user_obj)
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is None or destination_obj.is_user():
                channel = server_obj.get_channel_by_name(line)
                return self.take_op(channel, user_obj)
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(line)
            if test_channel.in_channel:
                return self.take_op(test_channel, user_obj)
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(line)
            return self.take_op(destination_obj, target_user)
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            return self.take_op(target_channel, target_user)
        # 2 args, try with second argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[1])
        target_user = server_obj.get_user_by_name(line_split[0])
        return self.take_op(target_channel, target_user)

    def take_op(self, channel, user):
        """
        Takes op from a user in a given channel, after checks.
        :param channel: Channel to take user op in
        :type channel: Destination.Channel
        :param user: User to take op from
        :type user: Destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, "+user.name+" is not in "+channel.name+"."
        # Check if hallo has op in channel
        if not self.hallo_has_op(channel):
            return "Error, I don't have power to take op in "+channel.name+"."
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_op:
            return "Error, this user doesn't have op."
        channel.server.send("MODE "+channel.name+" -o "+user.name, None, Server.MSG_RAW)
        return "Op status taken."

    def hallo_has_op(self, channel):
        """
        Checks whether hallo has op in a given channel.
        :param channel: channel to check op status for
        :type channel: Destination.Channel
        :return: whether hallo has op
        :rtype: bool
        """
        server = channel.server
        hallo_user = server.get_user_by_name(server.get_nick())
        hallo_membership = channel.get_membership_by_user(hallo_user)
        return hallo_membership.is_op


class Voice(Function):
    """
    Gives a user on an irc server "voice" status.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "voice"
        # Names which can be used to address the function
        self.names = {"voice", "give voice", "gib voice", "get voice"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Voice member in given channel, or current channel if no channel given, or command user if " \
                         "no member given. Format: voice <name> <channel>"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.server
        # If server isn't IRC type, we can't give op.
        if server_obj.type != Server.TYPE_IRC:
            return "Error, this function is only available for IRC servers."
        # If 0 arguments, voice user who called command.
        line_split = line.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if destination_obj is None or destination_obj.is_user():
                return "Error, I can't voice you in a privmsg, please provide a channel."
            # Give user voice
            return self.give_voice(destination_obj, user_obj)
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is None or destination_obj.is_user():
                channel = server_obj.get_channel_by_name(line)
                return self.give_voice(channel, user_obj)
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(line)
            if test_channel.in_channel:
                return self.give_voice(test_channel, user_obj)
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(line)
            return self.give_voice(destination_obj, target_user)
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            return self.give_voice(target_channel, target_user)
        # 2 args, try with second argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[1])
        target_user = server_obj.get_user_by_name(line_split[0])
        return self.give_voice(target_channel, target_user)

    def give_voice(self, channel, user):
        """
        Gives voice to a user in a given channel, after checks.
        :param channel: Channel to give user op in
        :type channel: Destination.Channel
        :param user: User to give op to
        :type user: Destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, "+user.name+" is not in "+channel.name+"."
        # Check if hallo has op in channel
        if not self.hallo_has_op(channel):
            return "Error, I don't have power to give op in "+channel.name+"."
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_op:
            return "Error, this user already has op."
        channel.server.send("MODE "+channel.name+" +o "+user.name, None, Server.MSG_RAW)
        return "Op status given."

    def hallo_has_op(self, channel):
        """
        Checks whether hallo has op in a given channel.
        :param channel: channel to check op status for
        :type channel: Destination.Channel
        :return: whether hallo has op
        :rtype: bool
        """
        server = channel.server
        hallo_user = server.get_user_by_name(server.get_nick())
        hallo_membership = channel.get_membership_by_user(hallo_user)
        return hallo_membership.is_op


class DeVoice(Function):
    """
    Removes a user on an irc server's "voice" status.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "devoice"
        # Names which can be used to address the function
        self.names = {"devoice", "unvoice", "take voice", "del voice", "delete voice", "remove voice"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "UnVoice member in given channel, or current channel if no channel given, or command user " \
                         "if no member given. Format: devoice <name> <channel>"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if server_obj.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # If 0 arguments, op user who called command.
        line_split = line.split()
        if len(line_split) == 0:
            server_obj.send("MODE " + destination_obj.get_name() + " -o " + user_obj.get_name(), None, Server.MSG_RAW)
            return "Voice status given."
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is not None and destination_obj == user_obj:
                channel = server_obj.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                server_obj.send("MODE " + channel.get_name() + " -v " + user_obj.get_name(), None, Server.MSG_RAW)
                return "Voice status taken."
            # If it starts with '#', check it's a channel hallo is in.
            if line.startswith("#"):
                channel = server_obj.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                server_obj.send("MODE " + channel.get_name() + " -v " + user_obj.get_name(), None, Server.MSG_RAW)
                return "Voice status taken."
            # Check if it's a user in current channel
            target_user = server_obj.get_user_by_name(line)
            if target_user is None or not destination_obj.is_user_in_channel(target_user):
                return "That user is not in this channel."
            # TODO: check if hallo has op in this channel.
            server_obj.send("MODE " + destination_obj.get_name() + " -v " + target_user.get_name(), None, Server.MSG_RAW)
            return "Voice status taken."
        # If 2 arguments, determine which is channel and which is user.
        if line_split[0].startswith("#"):
            target_channel = server_obj.get_channel_by_name(line_split[0])
            target_user = server_obj.get_user_by_name(line_split[1])
        elif line_split[1].startswith("#"):
            target_channel = server_obj.get_channel_by_name(line_split[1])
            target_user = server_obj.get_user_by_name(line_split[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if target_channel is None or not target_channel.is_in_channel():
            return "I'm not in that channel."
        if target_user is None or not target_user.is_online():
            return "That user is not online."
        if not target_channel.is_user_in_channel(target_user):
            return "That user is not in that channel."
        # TODO: check if hallo has op in this channel.
        server_obj.send("MODE " + target_channel.get_name() + " -v " + target_user.get_name(), None, Server.MSG_RAW)
        return "Voice status taken."


class Invite(Function):
    """
    IRC only, invites users to a given channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "invite"
        # Names which can be used to address the function
        self.names = {"invite"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Invite someone to a channel"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if server_obj.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        line_split = line.split()
        if len(line_split) == 0:
            return "Please specify a person to invite and/or a channel to invite to."
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            if line.startswith("#"):
                target_channel = server_obj.get_channel_by_name(line)
                if target_channel is None or not target_channel.is_in_channel():
                    return "I'm not in that channel."
                server_obj.send("INVITE " + user_obj.get_name() + " " + target_channel.get_name(), None, Server.MSG_RAW)
                return "Invited " + user_obj.get_name() + " to " + target_channel.get_name() + "."
            if destination_obj is None or destination_obj == user_obj:
                return "You can't invite a user to privmsg."
            target_user = server_obj.get_user_by_name(line)
            if target_user is None or not target_user.is_online():
                return "That user is not online."
            server_obj.send("INVITE " + target_user.get_name() + " " + destination_obj.get_name())
            return "Invited " + target_user.get_name() + " to " + destination_obj.get_name() + "."
        # If 2 arguments, determine which is channel and which is user.
        if line_split[0].startswith("#"):
            target_channel = server_obj.get_channel_by_name(line_split[0])
            target_user = server_obj.get_user_by_name(line_split[1])
        elif line_split[1].startswith("#"):
            target_channel = server_obj.get_channel_by_name(line_split[1])
            target_user = server_obj.get_user_by_name(line_split[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if target_channel is None or not target_channel.is_in_channel():
            return "I'm not in that channel."
        if target_user is None or not target_user.is_online():
            return "That user is not online."
        if target_channel.is_user_in_channel(target_user):
            return "That user is already in that channel."
        # TODO: check if hallo has op in this channel.
        server_obj.send("INVITE " + target_user.get_name() + " " + target_channel.get_name(), None, Server.MSG_RAW)
        return "Invited " + target_user.get_name() + " to " + target_channel.get_name() + "."


class Mute(Function):
    """
    Mutes the current or a selected channel. IRC only.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "mute"
        # Names which can be used to address the function
        self.names = {"mute"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Mutes a given channel or current channel. Format: mute <channel>"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.get_server()
        # TODO: check if hallo has op.
        # Check if no arguments were provided
        if line.strip() == "":
            target_channel = destination_obj
            if target_channel is None or target_channel == user_obj:
                return "You can't set mute on a privmsg."
            server_obj.send("MODE " + target_channel.get_name() + " +m", None, Server.MSG_RAW)
            return "Set mute."
        # Get channel from user input
        target_channel = server_obj.get_channel_by_name(line.strip())
        if target_channel is None or not target_channel.is_in_channel():
            return "I'm not in that channel."
        server_obj.send("MODE " + target_channel.get_name() + " +m", None, Server.MSG_RAW)
        return "Set mute in " + target_channel.get_name() + "."


class UnMute(Function):
    """
    Mutes the current or a selected channel. IRC only.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "unmute"
        # Names which can be used to address the function
        self.names = {"unmute", "un mute"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Unmutes a given channel or current channel if none is given. Format: unmute <channel>"

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.get_server()
        # TODO: check if hallo has op.
        # Check if no arguments were provided
        if line.strip() == "":
            target_channel = destination_obj
            if target_channel is None or target_channel == user_obj:
                return "You can't set mute on a privmsg."
            server_obj.send("MODE " + target_channel.get_name() + " -m", None, Server.MSG_RAW)
            return "Unset mute."
        # Get channel from user input
        target_channel = server_obj.get_channel_by_name(line.strip())
        if target_channel is None or not target_channel.is_in_channel():
            return "I'm not in that channel."
        server_obj.send("MODE " + target_channel.get_name() + " -m", None, Server.MSG_RAW)
        return "Unset mute in " + target_channel.get_name() + "."


class Kick(Function):
    """
    Kicks a specified user from a specified channel. IRC Only.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "kick"
        # Names which can be used to address the function
        self.names = {"kick"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Kick given user in given channel, or current channel if no channel given."

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if server_obj.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # Check input is not blank
        if line.strip() == "":
            return "Please specify who to kick."
        # Check if 1 argument is given.
        line_split = line.split()
        if len(line_split) == 1:
            target_user = server_obj.get_user_by_name(line.strip())
            if destination_obj is None or destination_obj == user_obj:
                return "I can't kick someone from a privmsg. Please specify a channel."
            if target_user is None or not target_user.is_online():
                return "That user is not online."
            if not destination_obj.is_user_in_channel(target_user):
                return "That user isn't in this channel."
            server_obj.send("KICK " + destination_obj.get_name() + " " + target_user.get_name(), None,
                            ServerIRC.MSG_RAW)
            return "Kicked " + target_user.get_name() + " from " + destination_obj.get_name() + "."
        # Check if first argument is a channel
        if line_split[0].startswith("#"):
            target_channel = server_obj.get_channel_by_name(line_split[0])
            target_user = server_obj.get_user_by_name(line_split[1])
            message = ""
            if len(line_split) > 2:
                message = " ".join(line_split[2:])
            if target_channel is None or not target_channel.is_in_channel():
                return "I'm not in that channel."
            if target_user is None or not target_user.is_online():
                return "That user is not online."
            if not target_channel.is_user_in_channel(target_user):
                return "That user is not in that channel."
            server_obj.send("KICK " + target_channel.get_name() + " " + target_user.get_name() + " " + message, None,
                            ServerIRC.MSG_RAW)
            return "Kicked " + target_user.get_name() + " from " + target_channel.get_name() + "."
        # Check if second argument is a channel.
        if line_split[1].startswith("#"):
            target_channel = server_obj.get_channel_by_name(line_split[1])
            target_user = server_obj.get_user_by_name(line_split[0])
            message = ""
            if len(line_split) > 2:
                message = " ".join(line_split[2:])
            if target_channel is None or not target_channel.is_in_channel():
                return "I'm not in that channel."
            if target_user is None or not target_user.is_online():
                return "That user is not online."
            if not target_channel.is_user_in_channel(target_user):
                return "That user is not in that channel."
            server_obj.send("KICK " + target_channel.get_name() + " " + target_user.get_name() + " " + message, None,
                            ServerIRC.MSG_RAW)
            return "Kicked " + target_user.get_name() + " from " + target_channel.get_name() + "."
        # Otherwise, it is a user and a message.
        target_channel = destination_obj
        target_user = server_obj.get_user_by_name(line_split[0])
        message = ""
        if len(line_split) > 2:
            message = " ".join(line_split[2:])
        if destination_obj is None or destination_obj == user_obj:
            return "I can't kick someone from a privmsg. Please specify a channel."
        if target_channel is None or not target_channel.is_in_channel():
            return "I'm not in that channel."
        if target_user is None or not target_user.is_online():
            return "That user is not online."
        if not target_channel.is_user_in_channel(target_user):
            return "That user is not in that channel."
        server_obj.send("KICK " + target_channel.get_name() + " " + target_user.get_name() + " " + message, None,
                        ServerIRC.MSG_RAW)
        return "Kicked " + target_user.get_name() + " from " + target_channel.get_name() + "."


class ChannelCaps(Function):
    """
    Set caps lock for a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "caps lock"
        # Names which can be used to address the function
        self.names = {"caps lock", "channel caps", "channel caps lock", "chan caps", "chan caps lock",
                      "channelcapslock"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets caps lock for channel on or off."

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.get_server()
        # If no arguments given, toggle caps lock in current destination
        line_clean = line.strip()
        if line_clean == '':
            destination_obj.set_upper_case(not destination_obj.is_upper_case())
            return "Caps lock toggled."
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                destination_obj.set_upper_case(input_bool)
                return "Caps lock set " + {False: 'off', True: 'on'}[input_bool] + "."
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.is_in_channel():
                target_channel.set_upper_case(not target_channel.is_upper_case())
                return "Caps lock toggled in " + target_channel.get_name() + "."
            # Otherwise input unknown
            return "Error, I don't understand your input, please specify a channel and whether to turn caps lock " \
                   "on or off."
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return "Error, I don't understand your input, please specify a channel and whether to turn " \
                   "caps lock on or off."
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if target_channel is None or not target_channel.is_in_channel():
            return "Error, I'm not in that channel."
        target_channel.set_upper_case(input_bool)
        return "Caps lock set " + {False: 'off', True: 'on'}[input_bool] + " in " + target_channel.get_name() + "."


class ChannelLogging(Function):
    """
    Set logging for a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "logging"
        # Names which can be used to address the function
        self.names = {"logging", "channel logging", "channel log", "chan logging", "chan log"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets or toggles logging for channel."

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.server
        # If no arguments given, toggle logging in current destination
        line_clean = line.strip()
        if line_clean == '':
            destination_obj.logging = not destination_obj.logging
            return "Logging toggled."
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                destination_obj.logging = input_bool
                return "Logging set " + {False: 'off', True: 'on'}[input_bool] + "."
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.logging = not target_channel.logging
                return "Logging toggled in " + target_channel.name + "."
            # Otherwise input unknown
            return "Error, I don't understand your input, please specify a channel and whether to turn logging " \
                   "on or off."
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return "Error, I don't understand your input, please specify a channel and whether to turn logging " \
                   "on or off."
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if not target_channel.in_channel:
            return "Error, I'm not in that channel."
        target_channel.logging = input_bool
        return "Logging set " + {False: 'off', True: 'on'}[input_bool] + " in " + target_channel.name + "."


class ChannelPassiveFunctions(Function):
    """
    Set whether passive functions are enabled in a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "passive"
        # Names which can be used to address the function
        self.names = {"passive"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets or toggles logging for channel."

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = {"passive"}
        for chan in ["chan ", "channel ", ""]:
            for passive in ["passive", "passive func", "passive funcs", "passive function", "passive functions"]:
                self.names.add(chan + passive)
        return self.names

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.server
        # If no arguments given, toggle passive functions in current destination
        line_clean = line.strip()
        if line_clean == '':
            destination_obj.passive_enabled = not destination_obj.passive_enabled
            return "Passive functions toggled."
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                destination_obj.passive_enabled = input_bool
                return "Passive functions set " + {False: 'disabled', True: 'enabled'}[input_bool] + "."
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.passive_enabled = not target_channel.passive_enabled
                return "Passive functions toggled in " + target_channel.get_name() + "."
            # Otherwise input unknown
            return "Error, I don't understand your input, please specify a channel and whether to turn passive " \
                   "functions on or off."
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return "Error, I don't understand your input, please specify a channel and whether to turn passive " \
                   "functions on or off."
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if not target_channel.in_channel:
            return "Error, I'm not in that channel."
        target_channel.passive_enabled = input_bool
        return "Passive functions set " + {False: 'disabled', True: 'enabled'}[
            input_bool] + " in " + target_channel.name + "."


class ChannelPassword(Function):
    """
    Set password for a channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "channel password"
        # Names which can be used to address the function
        self.names = {"channel password", "chan password", "channel pass", "chan pass"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Sets or disables channel password."

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        server_obj = user_obj.server
        # If no arguments given, turn the password for current channel off.
        line_clean = line.strip()
        if line_clean == '':
            destination_obj.password = None
            return "Channel password disabled."
        # If line has 1 argument, set password for current channel
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if null was specified
            input_null = Commons.is_string_null(line_split[0])
            if input_null:
                destination_obj.password = None
                return "Channel password disabled."
            else:
                destination_obj.password = line_split[0]
                return "Channel password set."
        # Otherwise line has 2 or more arguments.
        # Assume first is channel, and second is password.
        input_null = Commons.is_string_null(line_split[1])
        target_channel_name = line_split[0]
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if input_null:
            target_channel.password = None
            return "Channel password disabled for " + target_channel.name + "."
        else:
            target_channel.password = line_split[1]
            return "Channel password set for " + target_channel.name + "."
