from events import EventMode, EventInvite, EventKick
from function import Function
from inc.commons import Commons
from server import Server


def hallo_has_op(channel):
    """
    Checks whether hallo has op in a given channel.
    :param channel: channel to check op status for
    :type channel: destination.Channel
    :return: whether hallo has op
    :rtype: bool
    """
    server = channel.server
    hallo_user = server.get_user_by_address(server.get_nick().lower(), server.get_nick())
    hallo_membership = channel.get_membership_by_user(hallo_user)
    return hallo_membership.is_op


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't give op.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # If 0 arguments, op user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response("Error, I can't op you in a private message, please provide a channel.")
            # Give op to the user
            return event.create_response(self.give_op(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                        server_obj.name))
                return event.create_response(self.give_op(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.give_op(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                    server_obj.name))
            return event.create_response(self.give_op(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
            return event.create_response(self.give_op(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
        return event.create_response(self.give_op(target_channel, target_user))

    def give_op(self, channel, user):
        """
        Gives op to a user in a given channel, after checks.
        :param channel: Channel to give user op in
        :type channel: destination.Channel
        :param user: User to give op to
        :type user: destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, {} is not in {}.".format(user.name, channel.name)
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to give op in {}.".format(channel.name)
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_op:
            return "Error, this user already has op."
        mode_evt = EventMode(channel.server, channel, None, "+o {}".format(user.address), inbound=False)
        channel.server.send(mode_evt)
        return "Op status given."


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't take op.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # If 0 arguments, de-op user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response("Error, I can't de-op you in a private message, please provide a channel.")
            # Remove op
            return event.create_response(self.take_op(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                        server_obj.name))
                return event.create_response(self.take_op(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.take_op(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                    server_obj.name))
            return event.create_response(self.take_op(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
            return event.create_response(self.take_op(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
        return event.create_response(self.take_op(target_channel, target_user))

    def take_op(self, channel, user):
        """
        Takes op from a user in a given channel, after checks.
        :param channel: Channel to take user op in
        :type channel: destination.Channel
        :param user: User to take op from
        :type user: destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, {} is not in {}.".format(user.name, channel.name)
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to take op in {}.".format(channel.name)
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if not user_membership.is_op:
            return "Error, this user doesn't have op."
        mode_evt = EventMode(channel.server, channel, None, "-o {}".format(user.address), inbound=False)
        channel.server.send(mode_evt)
        return "Op status taken."


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't give voice.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # If 0 arguments, voice user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response("Error, I can't voice you in a private message, please provide a channel.")
            # Give user voice
            return event.create_response(self.give_voice(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                        server_obj.name))
                return event.create_response(self.give_voice(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.give_voice(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                    server_obj.name))
            return event.create_response(self.give_voice(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[1],
                                                                                    server_obj.name))
            return event.create_response(self.give_voice(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
        return event.create_response(self.give_voice(target_channel, target_user))

    def give_voice(self, channel, user):
        """
        Gives voice to a user in a given channel, after checks.
        :param channel: Channel to give user voice in
        :type channel: destination.Channel
        :param user: User to give voice to
        :type user: destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, {} is not in {}.".format(user.name, channel.name)
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to give voice in {}.".format(channel.name)
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_voice or user_membership.is_op:
            return "Error, this user already has voice."
        mode_evt = EventMode(channel.server, channel, None, "+v {}".format(user.address), inbound=False)
        channel.server.send(mode_evt)
        return "Voice status given."


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't take voice.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # If 0 arguments, take voice from user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response("Error, I can't un-voice you in a private message, " +
                                             "please provide a channel.")
            # Give user voice
            return event.create_response(self.take_voice(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                        server_obj.name))
                return event.create_response(self.take_voice(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.take_voice(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                    server_obj.name))
            return event.create_response(self.take_voice(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
            return event.create_response(self.take_voice(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
        return event.create_response(self.take_voice(target_channel, target_user))

    def take_voice(self, channel, user):
        """
        Takes voice from a user in a given channel, after checks.
        :param channel: Channel to take voice from user in
        :type channel: destination.Channel
        :param user: User to take voice from
        :type user: destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, {} is not in {}.".format(user.name, channel.name)
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to take voice in {}.".format(channel.name)
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if not user_membership.is_voice:
            return "Error, this user doesn't have voice."
        mode_evt = EventMode(channel.server, channel, None, "-v {}".format(user.address))
        channel.server.send(mode_evt)
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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't invite people
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # If 0 arguments, ask for clarification
        line_split = event.command_args.split()
        if len(line_split) == 0:
            return event.create_response("Error, please specify a user to invite and/or a channel to invite to.")
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                        server_obj.name))
                return event.create_response(self.send_invite(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.send_invite(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                    server_obj.name))
            return event.create_response(self.send_invite(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
            return event.create_response(self.send_invite(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
        return event.create_response(self.send_invite(target_channel, target_user))

    def send_invite(self, channel, user):
        """
        Sends an invite to a specified user to join a given channel.
        :param channel: Channel to invite target to
        :type channel: destination.Channel
        :param user: User to invite to channel
        :type user: destination.User
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user in channel.get_user_list():
            return "Error, {} is already in {}".format(user.name, channel.name)
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to invite users in {}.".format(channel.name)
        # Send invite
        invite_evt = EventInvite(channel.server, channel, None, user, inbound=False)
        channel.server.send(invite_evt)
        return "Invite sent."


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't mute channels
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # Check if no arguments were provided
        if event.command_args.strip() == "":
            if event.channel is None:
                return event.create_response("Error, you can't set mute on a private message.")
            return event.create_response(self.mute_channel(event.channel))
        # Get channel from user input
        target_channel = server_obj.get_channel_by_name(event.command_args.strip())
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(event.command_args.strip(),
                                                                                server_obj.name))
        return event.create_response(self.mute_channel(target_channel))

    def mute_channel(self, channel):
        """
        Sets mute on a given channel.
        :param channel: Channel to mute
        :type channel: destination.Channel
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to mute {}.".format(channel.name)
        # Send invite
        mode_evt = EventMode(channel.server, channel, None, "+m", inbound=False)
        channel.server.send(mode_evt)
        return "Set mute in {}.".format(channel.name)


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't unmute channels
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # Check if no arguments were provided
        if event.command_args.strip() == "":
            if event.channel is None:
                return event.create_response("Error, you can't unset mute on a private message.")
            return event.create_response(self.unmute_channel(event.channel))
        # Get channel from user input
        target_channel = server_obj.get_channel_by_name(event.command_args.strip())
        if target_channel is None:
            return event.create_response("Error, {} is not known on {}.".format(event.command_args.strip(),
                                                                                server_obj.name))
        return event.create_response(self.unmute_channel(target_channel))

    def unmute_channel(self, channel):
        """
        Sets mute on a given channel.
        :param channel: Channel to mute
        :type channel: destination.Channel
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to unmute {}.".format(channel.name)
        # Send invite
        mode_evt = EventMode(channel.server, channel, None, "-m", inbound=False)
        channel.server.send(mode_evt)
        return "Unset mute in {}.".format(channel.name)


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't invite people
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response("Error, this function is only available for IRC servers.")
        # If 0 arguments, ask for clarification
        line_split = event.command_args.split()
        if len(line_split) == 0:
            return event.create_response("Error, please specify a user to kick and/or a channel to kick from.")
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                        server_obj.name))
                return event.create_response(self.send_kick(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.send_kick(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(event.command_args,
                                                                                    server_obj.name))
            return event.create_response(self.send_kick(event.channel, target_user))
        if len(line_split) == 2:
            # If message was in private message, it's either channel and user, user and channel or channel and message
            if event.channel is None:
                target_channel = server_obj.get_channel_by_name(line_split[0])
                if target_channel is not None:
                    if target_channel.in_channel:
                        target_user = server_obj.get_user_by_name(line_split[1])
                        if target_user is not None and target_channel.is_user_in_channel(target_user):
                            return event.create_response(self.send_kick(target_channel, target_user))
                        return event.create_response(self.send_kick(target_channel, event.user, line_split[1]))
                    return event.create_response("Error, I am not in that channel.")
                target_user = server_obj.get_user_by_name(line_split[0])
                if target_user is None:
                    return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
                target_channel = server_obj.get_channel_by_name(line_split[1])
                if target_channel is None:
                    return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
                return event.create_response(self.send_kick(target_channel, target_user))
            # If 2 arguments, try with first argument as channel
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel is not None and target_channel.in_channel:
                target_user = server_obj.get_user_by_name(line_split[1])
                if target_user is not None and target_channel.is_user_in_channel(target_user):
                    return event.create_response(self.send_kick(target_channel, target_user))
                return event.create_response(self.send_kick(target_channel, event.user, line_split[1]))
            # 2 args, try with second argument as channel
            target_user = server_obj.get_user_by_name(line_split[0])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
            target_channel = server_obj.get_channel_by_name(line_split[1])
            if target_channel is not None and target_channel.in_channel:
                return event.create_response(self.send_kick(target_channel, target_user))
            return event.create_response(self.send_kick(event.channel, target_user, line_split[1]))
        # If message was in private message, it's either channel, user and message or user, channel and message or
        # channel and message
        if event.channel is None:
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel is not None:
                if target_channel.in_channel:
                    target_user = server_obj.get_user_by_name(line_split[1])
                    if target_user is not None and target_channel.is_user_in_channel(target_user):
                        return event.create_response(self.send_kick(target_channel, target_user,
                                                                    " ".join(line_split[2:])))
                    return event.create_response(self.send_kick(target_channel, event.user, " ".join(line_split[1:])))
                return event.create_response("Error, I am not in that channel.")
            target_user = server_obj.get_user_by_name(line_split[0])
            if target_user is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
            target_channel = server_obj.get_channel_by_name(line_split[1])
            if target_channel is None:
                return event.create_response("Error, {} is not known on {}.".format(line_split[1], server_obj.name))
            return event.create_response(self.send_kick(target_channel, target_user, " ".join(line_split[2:])))
        # If more than 2 arguments, determine which of the first 2 is channel/user, the rest is a message.
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is not None and target_channel.is_user_in_channel(target_user):
                return event.create_response(self.send_kick(target_channel, target_user, " ".join(line_split[2:])))
            return event.create_response(self.send_kick(target_channel, event.user, " ".join(line_split[1:])))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response("Error, {} is not known on {}.".format(line_split[0], server_obj.name))
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is not None and target_channel.in_channel:
            return event.create_response(self.send_kick(target_channel, target_user, " ".join(line_split[2:])))
        return event.create_response(self.send_kick(event.channel, target_user, " ".join(line_split[1:])))

    def send_kick(self, channel, user, message=""):
        """
        Sends an invite to a specified user to join a given channel.
        :param channel: Channel to invite target to
        :type channel: destination.Channel
        :param user: User to invite to channel
        :type user: destination.User
        :param message: Kick message to send
        :type message: str
        :return: Response to send to requester
        :rtype: str
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return "Error, {} is not in {}.".format(user.name, channel.name)
        # Check if hallo has op in channel
        if not hallo_has_op(channel):
            return "Error, I don't have power to kick users from {}.".format(channel.name)
        # Send invite
        kick_evt = EventKick(channel.server, channel, None, user, message, inbound=False)
        channel.server.send(kick_evt)
        return "Kicked {} from {}.".format(user.name, channel.name)


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, toggle caps lock in current destination
        line_clean = event.command_args.strip()
        if line_clean == '':
            event.channel.use_caps_lock = not event.channel.use_caps_lock
            return event.create_response("Caps lock toggled.")
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                event.channel.use_caps_lock = input_bool
                return event.create_response("Caps lock set {}.".format({False: 'off', True: 'on'}[input_bool]))
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.use_caps_lock = not target_channel.use_caps_lock
                return event.create_response("Caps lock toggled in {}.".format(target_channel.name))
            # Otherwise input unknown
            return event.create_response("Error, I don't understand your input, " +
                                         "please specify a channel and whether to turn caps lock on or off.")
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return event.create_response("Error, I don't understand your input, please specify a channel and " +
                                         "whether to turn caps lock on or off.")
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if target_channel is None or not target_channel.in_channel:
            return event.create_response("Error, I'm not in that channel.")
        target_channel.use_caps_lock = input_bool
        return event.create_response("Caps lock set {} in {}.".format({False: 'off', True: 'on'}[input_bool],
                                                                      target_channel.name))


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, toggle logging in current destination
        line_clean = event.command_args.strip()
        if line_clean == '':
            event.channel.logging = not event.channel.logging
            return event.create_response("Logging toggled.")
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                event.channel.logging = input_bool
                return event.create_response("Logging set {}.".format({False: 'off', True: 'on'}[input_bool]))
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.logging = not target_channel.logging
                return event.create_response("Logging toggled in {}.".format(target_channel.name))
            # Otherwise input unknown
            return event.create_response("Error, I don't understand your input, please specify a channel and " +
                                         "whether to turn logging on or off.")
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return event.create_response("Error, I don't understand your input, please specify a channel and " +
                                         "whether to turn logging on or off.")
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if not target_channel.in_channel:
            return event.create_response("Error, I'm not in that channel.")
        target_channel.logging = input_bool
        return event.create_response("Logging set {} in {}.".format({False: 'off', True: 'on'}[input_bool],
                                                                    target_channel.name))


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, toggle passive functions in current destination
        line_clean = event.command_args.strip()
        if line_clean == '':
            event.channel.passive_enabled = not event.channel.passive_enabled
            return event.create_response("Passive functions toggled.")
        # If line has 1 argument,
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if a boolean was specified
            input_bool = Commons.string_to_bool(line_split[0])
            if input_bool is not None:
                event.channel.passive_enabled = input_bool
                return event.create_response("Passive functions set {}.".format({False: 'disabled',
                                                                                 True: 'enabled'}[input_bool]))
            # Check if a channel was specified
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel.in_channel:
                target_channel.passive_enabled = not target_channel.passive_enabled
                return event.create_response("Passive functions toggled in {}.".format(target_channel.name))
            # Otherwise input unknown
            return event.create_response("Error, I don't understand your input, please specify a channel and " +
                                         "whether to turn passive functions on or off.")
        # Otherwise line has 2 or more arguments.
        # Check if first argument is boolean
        input_bool = Commons.string_to_bool(line_split[0])
        target_channel_name = line_split[1]
        if input_bool is None:
            input_bool = Commons.string_to_bool(line_split[1])
            target_channel_name = line_split[0]
        if input_bool is None:
            return event.create_response("Error, I don't understand your input, please specify a channel and " +
                                         "whether to turn passive functions on or off.")
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if not target_channel.in_channel:
            return event.create_response("Error, I'm not in that channel.")
        target_channel.passive_enabled = input_bool
        return event.create_response("Passive functions set {} in {}.".format("enabled" if input_bool else "disabled",
                                                                              target_channel.name))


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

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If no arguments given, turn the password for current channel off.
        line_clean = event.command_args.strip()
        if line_clean == '':
            event.channel.password = None
            return event.create_response("Channel password disabled.")
        # If line has 1 argument, set password for current channel
        line_split = line_clean.split()
        if len(line_split) == 1:
            # Check if null was specified
            input_null = Commons.is_string_null(line_split[0])
            if input_null:
                event.channel.password = None
                return event.create_response("Channel password disabled.")
            else:
                event.channel.password = line_split[0]
                return event.create_response("Channel password set.")
        # Otherwise line has 2 or more arguments.
        # Assume first is channel, and second is password.
        input_null = Commons.is_string_null(line_split[1])
        target_channel_name = line_split[0]
        target_channel = server_obj.get_channel_by_name(target_channel_name)
        if input_null:
            target_channel.password = None
            return event.create_response("Channel password disabled for {}.".format(target_channel.name))
        else:
            target_channel.password = line_split[1]
            return event.create_response("Channel password set for {}.".format(target_channel.name))
