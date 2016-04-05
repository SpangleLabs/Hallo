from Function import Function
from inc.commons import Commons
from Server import Server


class Operator(Function):
    """
    Gives a user on an irc server "operator" status.
    """
    # Name for use in help listing
    help_name = "op"
    # Names which can be used to address the function
    names = {"op", "operator", "give op", "gib op", "get op", "give operator", "gib operator", "get operator"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Op member in given channel, or current channel if no channel given. Or command user if no member " \
                "given. Format: op <name> <channel>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if serverObject.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # If 0 arguments, op user who called command.
        lineSplit = line.split()
        if len(lineSplit) == 0:
            serverObject.send("MODE " + destination_obj.get_name() + " +o " + user_obj.get_name(), None, "raw")
            return "Op status given."
        # If 1 argument, see if it's a channel or a user.
        if len(lineSplit) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is not None and destination_obj == user_obj:
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " +o " + user_obj.get_name(), None, "raw")
                return "Op status given."
            # If it starts with '#', check it's a channel hallo is in.
            if line.startswith("#"):
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " +o " + user_obj.get_name(), None, "raw")
                return "Op status given."
            # Check if it's a user in current channel
            targetUser = serverObject.get_user_by_name(line)
            if targetUser is None or not destination_obj.is_user_in_channel(targetUser):
                return "That user is not in this channel."
            # TODO: check if hallo has op in this channel.
            serverObject.send("MODE " + destination_obj.get_name() + " +o " + targetUser.get_name(), None, "raw")
            return "Op status given."
        # If 2 arguments, determine which is channel and which is user.
        if lineSplit[0].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            targetUser = serverObject.get_user_by_name(lineSplit[1])
        elif lineSplit[1].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[1])
            targetUser = serverObject.get_user_by_name(lineSplit[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        if targetUser is None or not targetUser.is_online():
            return "That user is not online."
        if not targetChannel.is_user_in_channel(targetUser):
            return "That user is not in that channel."
        # TODO: check if hallo has op in this channel.
        serverObject.send("MODE " + targetChannel.get_name() + " +o " + targetUser.get_name(), None, "raw")
        return "Op status given."


class DeOperator(Function):
    """
    Removes a user on an irc server's "operator" status.
    """
    # Name for use in help listing
    help_name = "deop"
    # Names which can be used to address the function
    names = {"deop", "deoperator", "unoperator", "take op", "del op", "delete op", "remove op", "take operator",
              "del operator", "delete op", "remove operator"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Deop member in given channel, or current channel if no channel given. Or command user if no member " \
                "given. Format: deop <name> <channel>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if serverObject.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # If 0 arguments, op user who called command.
        lineSplit = line.split()
        if len(lineSplit) == 0:
            serverObject.send("MODE " + destination_obj.get_name() + " -o " + user_obj.get_name(), None, "raw")
            return "Op status taken."
        # If 1 argument, see if it's a channel or a user.
        if len(lineSplit) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is not None and destination_obj == user_obj:
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " -o " + user_obj.get_name(), None, "raw")
                return "Op status taken."
            # If it starts with '#', check it's a channel hallo is in.
            if line.startswith("#"):
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " -o " + user_obj.get_name(), None, "raw")
                return "Op status taken."
            # Check if it's a user in current channel
            targetUser = serverObject.get_user_by_name(line)
            if targetUser is None or not destination_obj.is_user_in_channel(targetUser):
                return "That user is not in this channel."
            # TODO: check if hallo has op in this channel.
            serverObject.send("MODE " + destination_obj.get_name() + " -o " + targetUser.get_name(), None, "raw")
            return "Op status taken."
        # If 2 arguments, determine which is channel and which is user.
        if lineSplit[0].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            targetUser = serverObject.get_user_by_name(lineSplit[1])
        elif lineSplit[1].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[1])
            targetUser = serverObject.get_user_by_name(lineSplit[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        if targetUser is None or not targetUser.is_online():
            return "That user is not online."
        if not targetChannel.is_user_in_channel(targetUser):
            return "That user is not in that channel."
        # TODO: check if hallo has op in this channel.
        serverObject.send("MODE " + targetChannel.get_name() + " -o " + targetUser.get_name(), None, "raw")
        return "Op status taken."


class Voice(Function):
    """
    Gives a user on an irc server "voice" status.
    """
    # Name for use in help listing
    help_name = "voice"
    # Names which can be used to address the function
    names = {"voice", "give voice", "gib voice", "get voice"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Voice member in given channel, or current channel if no channel given, or command user if no member " \
                "given. Format: voice <name> <channel>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if serverObject.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # If 0 arguments, op user who called command.
        lineSplit = line.split()
        if len(lineSplit) == 0:
            serverObject.send("MODE " + destination_obj.get_name() + " +v " + user_obj.get_name(), None, "raw")
            return "Voice status given."
        # If 1 argument, see if it's a channel or a user.
        if len(lineSplit) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is not None and destination_obj == user_obj:
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " +v " + user_obj.get_name(), None, "raw")
                return "Voice status given."
            # If it starts with '#', check it's a channel hallo is in.
            if line.startswith("#"):
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " +v " + user_obj.get_name(), None, "raw")
                return "Voice status given."
            # Check if it's a user in current channel
            targetUser = serverObject.get_user_by_name(line)
            if targetUser is None or not destination_obj.is_user_in_channel(targetUser):
                return "That user is not in this channel."
            # TODO: check if hallo has op in this channel.
            serverObject.send("MODE " + destination_obj.get_name() + " +v " + targetUser.get_name(), None, "raw")
            return "Voice status given."
        # If 2 arguments, determine which is channel and which is user.
        if lineSplit[0].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            targetUser = serverObject.get_user_by_name(lineSplit[1])
        elif lineSplit[1].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[1])
            targetUser = serverObject.get_user_by_name(lineSplit[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        if targetUser is None or not targetUser.is_online():
            return "That user is not online."
        if not targetChannel.is_user_in_channel(targetUser):
            return "That user is not in that channel."
        # TODO: check if hallo has op in this channel.
        serverObject.send("MODE " + targetChannel.get_name() + " +o " + targetUser.get_name(), None, "raw")
        return "Voice status given."


class DeVoice(Function):
    """
    Removes a user on an irc server's "voice" status.
    """
    # Name for use in help listing
    help_name = "devoice"
    # Names which can be used to address the function
    names = {"devoice", "unvoice", "take voice", "del voice", "delete voice", "remove voice"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "UnVoice member in given channel, or current channel if no channel given, or command user if no " \
                "member given. Format: devoice <name> <channel>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if serverObject.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # If 0 arguments, op user who called command.
        lineSplit = line.split()
        if len(lineSplit) == 0:
            serverObject.send("MODE " + destination_obj.get_name() + " -o " + user_obj.get_name(), None, "raw")
            return "Voice status given."
        # If 1 argument, see if it's a channel or a user.
        if len(lineSplit) == 1:
            # If message was sent in privmsg, it's referring to a channel
            if destination_obj is not None and destination_obj == user_obj:
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " -v " + user_obj.get_name(), None, "raw")
                return "Voice status taken."
            # If it starts with '#', check it's a channel hallo is in.
            if line.startswith("#"):
                channel = serverObject.get_channel_by_name(line)
                if channel is None or not channel.is_in_channel():
                    return "I'm not in that channel."
                # TODO: check if hallo has op in that channel.
                serverObject.send("MODE " + channel.get_name() + " -v " + user_obj.get_name(), None, "raw")
                return "Voice status taken."
            # Check if it's a user in current channel
            targetUser = serverObject.get_user_by_name(line)
            if targetUser is None or not destination_obj.is_user_in_channel(targetUser):
                return "That user is not in this channel."
            # TODO: check if hallo has op in this channel.
            serverObject.send("MODE " + destination_obj.get_name() + " -v " + targetUser.get_name(), None, "raw")
            return "Voice status taken."
        # If 2 arguments, determine which is channel and which is user.
        if lineSplit[0].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            targetUser = serverObject.get_user_by_name(lineSplit[1])
        elif lineSplit[1].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[1])
            targetUser = serverObject.get_user_by_name(lineSplit[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        if targetUser is None or not targetUser.is_online():
            return "That user is not online."
        if not targetChannel.is_user_in_channel(targetUser):
            return "That user is not in that channel."
        # TODO: check if hallo has op in this channel.
        serverObject.send("MODE " + targetChannel.get_name() + " -v " + targetUser.get_name(), None, "raw")
        return "Voice status taken."


class Invite(Function):
    """
    IRC only, invites users to a given channel.
    """
    # Name for use in help listing
    help_name = "invite"
    # Names which can be used to address the function
    names = {"invite"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Invite someone to a channel"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if serverObject.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        lineSplit = line.split()
        if len(lineSplit) == 0:
            return "Please specify a person to invite and/or a channel to invite to."
        # If 1 argument, see if it's a channel or a user.
        if len(lineSplit) == 1:
            if line.startswith("#"):
                targetChannel = serverObject.get_channel_by_name(line)
                if targetChannel is None or not targetChannel.is_in_channel():
                    return "I'm not in that channel."
                serverObject.send("INVITE " + user_obj.get_name() + " " + targetChannel.get_name(), None, "raw")
                return "Invited " + user_obj.get_name() + " to " + targetChannel.get_name() + "."
            if destination_obj is None or destination_obj == user_obj:
                return "You can't invite a user to privmsg."
            targetUser = serverObject.get_user_by_name(line)
            if targetUser is None or not targetUser.is_online():
                return "That user is not online."
            serverObject.send("INVITE " + targetUser.get_name() + " " + destination_obj.get_name())
            return "Invited " + targetUser.get_name() + " to " + destination_obj.get_name() + "."
        # If 2 arguments, determine which is channel and which is user.
        if lineSplit[0].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            targetUser = serverObject.get_user_by_name(lineSplit[1])
        elif lineSplit[1].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[1])
            targetUser = serverObject.get_user_by_name(lineSplit[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        # Do checks on target channel and user
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        if targetUser is None or not targetUser.is_online():
            return "That user is not online."
        if targetChannel.is_user_in_channel(targetUser):
            return "That user is already in that channel."
        # TODO: check if hallo has op in this channel.
        serverObject.send("INVITE " + targetUser.get_name() + " " + targetChannel.get_name(), None, "raw")
        return "Invited " + targetUser.get_name() + " to " + targetChannel.get_name() + "."


class Mute(Function):
    """
    Mutes the current or a selected channel. IRC only.
    """
    # Name for use in help listing
    help_name = "mute"
    # Names which can be used to address the function
    names = {"mute"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Mutes a given channel or current channel. Format: mute <channel>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # TODO: check if hallo has op.
        # Check if no arguments were provided
        if line.strip() == "":
            targetChannel = destination_obj
            if targetChannel is None or targetChannel == user_obj:
                return "You can't set mute on a privmsg."
            serverObject.send("MODE " + targetChannel.get_name() + " +m", None, "raw")
            return "Set mute."
        # Get channel from user input
        targetChannel = serverObject.get_channel_by_name(line.strip())
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        serverObject.send("MODE " + targetChannel.get_name() + " +m", None, "raw")
        return "Set mute in " + targetChannel.get_name() + "."


class UnMute(Function):
    """
    Mutes the current or a selected channel. IRC only.
    """
    # Name for use in help listing
    help_name = "unmute"
    # Names which can be used to address the function
    names = {"unmute", "un mute"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Unmutes a given channel or current channel if none is given. Format: unmute <channel>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # TODO: check if hallo has op.
        # Check if no arguments were provided
        if line.strip() == "":
            targetChannel = destination_obj
            if targetChannel is None or targetChannel == user_obj:
                return "You can't set mute on a privmsg."
            serverObject.send("MODE " + targetChannel.get_name() + " -m", None, "raw")
            return "Unset mute."
        # Get channel from user input
        targetChannel = serverObject.get_channel_by_name(line.strip())
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        serverObject.send("MODE " + targetChannel.get_name() + " -m", None, "raw")
        return "Unset mute in " + targetChannel.get_name() + "."


class Kick(Function):
    """
    Kicks a specified user from a specified channel. IRC Only.
    """
    # Name for use in help listing
    help_name = "kick"
    # Names which can be used to address the function
    names = {"kick"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Kick given user in given channel, or current channel if no channel given."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If server isn't IRC type, we can't give op.
        if serverObject.get_type() != Server.TYPE_IRC:
            return "This function is only available for IRC servers."
        # TODO: check if hallo has op?
        # Check input is not blank
        if line.strip() == "":
            return "Please specify who to kick."
        # Check if 1 argument is given.
        lineSplit = line.split()
        if len(lineSplit) == 1:
            targetUser = serverObject.get_user_by_name(line.strip())
            if destination_obj is None or destination_obj == user_obj:
                return "I can't kick someone from a privmsg. Please specify a channel."
            if targetUser is None or not targetUser.is_online() or not destination_obj.is_user_in_channel(targetUser):
                return "That user isn't in this channel."
            serverObject.send("KICK " + destination_obj.get_name() + " " + targetUser.get_name(), None, "raw")
            return "Kicked " + targetUser.get_name() + " from " + destination_obj.get_name() + "."
        # Check if first argument is a channel
        if lineSplit[0].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            targetUser = serverObject.get_user_by_name(lineSplit[1])
            message = ""
            if len(lineSplit) > 2:
                message = " ".join(lineSplit[2:])
            if targetChannel is None or not targetChannel.is_in_channel():
                return "I'm not in that channel."
            if targetUser is None or not targetUser.is_online():
                return "That user is not online."
            if not targetChannel.is_user_in_channel(targetUser):
                return "That user is not in that channel."
            serverObject.send("KICK " + targetChannel.get_name() + " " + targetUser.get_name() + " " + message, None,
                              "raw")
            return "Kicked " + targetUser.get_name() + " from " + targetChannel.get_name() + "."
        # Check if second argument is a channel.
        if lineSplit[1].startswith("#"):
            targetChannel = serverObject.get_channel_by_name(lineSplit[1])
            targetUser = serverObject.get_user_by_name(lineSplit[0])
            message = ""
            if len(lineSplit) > 2:
                message = " ".join(lineSplit[2:])
            if targetChannel is None or not targetChannel.is_in_channel():
                return "I'm not in that channel."
            if targetUser is None or not targetUser.is_online():
                return "That user is not online."
            if not targetChannel.is_user_in_channel(targetUser):
                return "That user is not in that channel."
            serverObject.send("KICK " + targetChannel.get_name() + " " + targetUser.get_name() + " " + message, None,
                              "raw")
            return "Kicked " + targetUser.get_name() + " from " + targetChannel.get_name() + "."
        # Otherwise, it is a user and a message.
        targetChannel = destination_obj
        targetUser = serverObject.get_user_by_name(lineSplit[0])
        message = ""
        if len(lineSplit) > 2:
            message = " ".join(lineSplit[2:])
        if destination_obj is None or destination_obj == user_obj:
            return "I can't kick someone from a privmsg. Please specify a channel."
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        if targetUser is None or not targetUser.is_online():
            return "That user is not online."
        if not targetChannel.is_user_in_channel(targetUser):
            return "That user is not in that channel."
        serverObject.send("KICK " + targetChannel.get_name() + " " + targetUser.get_name() + " " + message, None, "raw")
        return "Kicked " + targetUser.get_name() + " from " + targetChannel.get_name() + "."


class ChannelCaps(Function):
    """
    Set caps lock for a channel.
    """
    # Name for use in help listing
    help_name = "caps lock"
    # Names which can be used to address the function
    names = {"caps lock", "channel caps", "channel caps lock", "chan caps", "chan caps lock", "channelcapslock"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Sets caps lock for channel on or off."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If no arguments given, toggle caps lock in current destination
        lineClean = line.strip()
        if lineClean == '':
            destination_obj.set_upper_case(not destination_obj.is_upper_case())
            return "Caps lock toggled."
        # If line has 1 argument,
        lineSplit = lineClean.split()
        if len(lineSplit) == 1:
            # Check if a boolean was specified
            inputBool = Commons.string_to_bool(lineSplit[0])
            if inputBool is not None:
                destination_obj.set_upper_case(inputBool)
                return "Caps lock set " + {False: 'off', True: 'on'}[inputBool] + "."
            # Check if a channel was specified
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            if targetChannel.is_in_channel():
                targetChannel.set_upper_case(not targetChannel.is_upper_case())
                return "Caps lock togged in " + targetChannel.get_name() + "."
            # Otherwise input unknown
            return "I don't understand your input, please specify a channel and whether to turn caps lock on or off."
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        inputBool = Commons.string_to_bool(lineSplit[0])
        targetChannelName = lineSplit[1]
        if inputBool is None:
            inputBool = Commons.string_to_bool(lineSplit[1])
            targetChannelName = lineSplit[0]
        if inputBool is None:
            return "I don't understand your input, please specify a channel and whether to turn caps lock on or off."
        targetChannel = serverObject.get_channel_by_name(targetChannelName)
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        destination_obj.set_upper_case(inputBool)
        return "Caps lock set " + {False: 'off', True: 'on'}[inputBool] + " in " + targetChannel.get_name() + "."


class ChannelLogging(Function):
    """
    Set logging for a channel.
    """
    # Name for use in help listing
    help_name = "logging"
    # Names which can be used to address the function
    names = {"logging", "channel logging", "channel log", "chan logging", "chan log"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Sets or toggles logging for channel."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If no arguments given, toggle logging in current destination
        lineClean = line.strip()
        if lineClean == '':
            destination_obj.set_logging(not destination_obj.get_logging())
            return "Logging toggled."
        # If line has 1 argument,
        lineSplit = lineClean.strip()
        if len(lineSplit) == 1:
            # Check if a boolean was specified
            inputBool = Commons.string_to_bool(lineSplit[0])
            if inputBool is not None:
                destination_obj.set_logging(inputBool)
                return "Logging set " + {False: 'off', True: 'on'}[inputBool] + "."
            # Check if a channel was specified
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            if targetChannel.is_in_channel():
                targetChannel.set_logging(not targetChannel.get_logging())
                return "Logging togged in " + targetChannel.get_name() + "."
            # Otherwise input unknown
            return "I don't understand your input, please specify a channel and whether to turn logging on or off."
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        inputBool = Commons.string_to_bool(lineSplit[0])
        targetChannelName = lineSplit[1]
        if inputBool is None:
            inputBool = Commons.string_to_bool(lineSplit[1])
            targetChannelName = lineSplit[0]
        if inputBool is None:
            return "I don't understand your input, please specify a channel and whether to turn logging on or off."
        targetChannel = serverObject.get_channel_by_name(targetChannelName)
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        destination_obj.set_logging(inputBool)
        return "Logging set " + {False: 'off', True: 'on'}[inputBool] + " in " + targetChannel.get_name() + "."


class ChannelPassiveFunctions(Function):
    """
    Set whether passive functions are enabled in a channel.
    """
    # Name for use in help listing
    help_name = "passive"
    # Names which can be used to address the function
    names = {"passive"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Sets or toggles logging for channel."

    def __init__(self):
        """
        Constructor
        """
        pass

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = {"passive"}
        for chan in ["chan ", "channel "]:
            for passive in ["passive", "passive func", "passive function", "passive functions"]:
                self.names.add(chan + passive)
        return self.names

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If no arguments given, toggle passive functions in current destination
        lineClean = line.strip()
        if lineClean == '':
            destination_obj.set_passive_enabled(not destination_obj.is_passive_enabled())
            return "Passive functions toggled."
        # If line has 1 argument,
        lineSplit = lineClean.strip()
        if len(lineSplit) == 1:
            # Check if a boolean was specified
            inputBool = Commons.string_to_bool(lineSplit[0])
            if inputBool is not None:
                destination_obj.set_passive_enabled(inputBool)
                return "Passive functions set " + {False: 'disabled', True: 'enabled'}[inputBool] + "."
            # Check if a channel was specified
            targetChannel = serverObject.get_channel_by_name(lineSplit[0])
            if targetChannel.is_in_channel():
                targetChannel.set_passive_enabled(not targetChannel.is_passive_enabled())
                return "Passive functions togged in " + targetChannel.get_name() + "."
            # Otherwise input unknown
            return "I don't understand your input, please specify a channel and whether to turn passive functions on " \
                   "or off."
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        inputBool = Commons.string_to_bool(lineSplit[0])
        targetChannelName = lineSplit[1]
        if inputBool is None:
            inputBool = Commons.string_to_bool(lineSplit[1])
            targetChannelName = lineSplit[0]
        if inputBool is None:
            return "I don't understand your input, please specify a channel and whether to turn passive functions on " \
                   "or off."
        targetChannel = serverObject.get_channel_by_name(targetChannelName)
        if targetChannel is None or not targetChannel.is_in_channel():
            return "I'm not in that channel."
        destination_obj.set_passive_enabled(inputBool)
        return "Passive functions set " + {False: 'disabled', True: 'enabled'}[
            inputBool] + " in " + targetChannel.get_name() + "."


class ChannelPassword(Function):
    """
    Set password for a channel.
    """
    # Name for use in help listing
    help_name = "channel password"
    # Names which can be used to address the function
    names = {"channel password", "chan password", "channel pass", "chan pass"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Sets or disables channel password."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Get server object
        serverObject = user_obj.get_server()
        # If no arguments given, turn the password for current channel off.
        lineClean = line.strip()
        if lineClean == '':
            destination_obj.set_password(None)
            return "Channel password disabled."
        # If line has 1 argument, set password for current channel
        lineSplit = lineClean.strip()
        if len(lineSplit) == 1:
            # Check if null was specified
            inputNull = Commons.is_string_null(lineSplit[0])
            if inputNull:
                destination_obj.set_password(None)
                return "Channel password disabled."
            else:
                destination_obj.set_password(lineSplit[0])
                return "Channel password set."
        # Otherwise line has 2 or more arguments.
        # Assume first is channel, and second is password.
        inputNull = Commons.is_string_null(lineSplit[1])
        targetChannelName = lineSplit[0]
        targetChannel = serverObject.get_channel_by_name(targetChannelName)
        if inputNull:
            destination_obj.set_password(None)
            return "Channel password disabled for " + targetChannel.get_name() + "."
        else:
            destination_obj.set_password(lineSplit[1])
            return "Channel password set for " + targetChannel.get_name() + "."
