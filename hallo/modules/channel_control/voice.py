from hallo.events import EventMode
from hallo.function import Function
import hallo.modules.channel_control.channel_control
from hallo.server import Server


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
        self.help_docs = (
            "Voice member in given channel, or current channel if no channel given, or command user if "
            "no member given. Format: voice <name> <channel>"
        )

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't give voice.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # If 0 arguments, voice user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response(
                    "Error, I can't voice you in a private message, please provide a channel."
                )
            # Give user voice
            return event.create_response(self.give_voice(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response(
                        "Error, {} is not known on {}.".format(
                            event.command_args, server_obj.name
                        )
                    )
                return event.create_response(self.give_voice(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.give_voice(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        event.command_args, server_obj.name
                    )
                )
            return event.create_response(self.give_voice(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        line_split[1], server_obj.name
                    )
                )
            return event.create_response(self.give_voice(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response(
                "Error, {} is not known on {}.".format(line_split[0], server_obj.name)
            )
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response(
                "Error, {} is not known on {}.".format(line_split[1], server_obj.name)
            )
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
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return "Error, I don't have power to give voice in {}.".format(channel.name)
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_voice or user_membership.is_op:
            return "Error, this user already has voice."
        mode_evt = EventMode(
            channel.server, channel, None, "+v {}".format(user.address), inbound=False
        )
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
        self.names = {
            "devoice",
            "unvoice",
            "take voice",
            "del voice",
            "delete voice",
            "remove voice",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "UnVoice member in given channel, or current channel if no channel given, or command user "
            "if no member given. Format: devoice <name> <channel>"
        )

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't take voice.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # If 0 arguments, take voice from user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response(
                    "Error, I can't un-voice you in a private message, please provide a channel."
                )
            # Give user voice
            return event.create_response(self.take_voice(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response(
                        "Error, {} is not known on {}.".format(
                            event.command_args, server_obj.name
                        )
                    )
                return event.create_response(self.take_voice(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.take_voice(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        event.command_args, server_obj.name
                    )
                )
            return event.create_response(self.take_voice(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        line_split[1], server_obj.name
                    )
                )
            return event.create_response(self.take_voice(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response(
                "Error, {} is not known on {}.".format(line_split[0], server_obj.name)
            )
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response(
                "Error, {} is not known on {}.".format(line_split[1], server_obj.name)
            )
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
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return "Error, I don't have power to take voice in {}.".format(channel.name)
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if not user_membership.is_voice:
            return "Error, this user doesn't have voice."
        mode_evt = EventMode(
            channel.server, channel, None, "-v {}".format(user.address)
        )
        channel.server.send(mode_evt)
        return "Voice status taken."
