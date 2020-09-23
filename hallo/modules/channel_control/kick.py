from hallo.events import EventKick
from hallo.function import Function
import hallo.modules.channel_control.channel_control
from hallo.server import Server


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
        self.help_docs = (
            "Kick given user in given channel, or current channel if no channel given."
        )

    def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't invite people
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # If 0 arguments, ask for clarification
        line_split = event.command_args.split()
        if len(line_split) == 0:
            return event.create_response(
                "Error, please specify a user to kick and/or a channel to kick from."
            )
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
                return event.create_response(self.send_kick(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.send_kick(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        event.command_args, server_obj.name
                    )
                )
            return event.create_response(self.send_kick(event.channel, target_user))
        if len(line_split) == 2:
            # If message was in private message, it's either channel and user, user and channel or channel and message
            if event.channel is None:
                target_channel = server_obj.get_channel_by_name(line_split[0])
                if target_channel is not None:
                    if target_channel.in_channel:
                        target_user = server_obj.get_user_by_name(line_split[1])
                        if (
                            target_user is not None
                            and target_channel.is_user_in_channel(target_user)
                        ):
                            return event.create_response(
                                self.send_kick(target_channel, target_user)
                            )
                        return event.create_response(
                            self.send_kick(target_channel, event.user, line_split[1])
                        )
                    return event.create_response("Error, I am not in that channel.")
                target_user = server_obj.get_user_by_name(line_split[0])
                if target_user is None:
                    return event.create_response(
                        "Error, {} is not known on {}.".format(
                            line_split[0], server_obj.name
                        )
                    )
                target_channel = server_obj.get_channel_by_name(line_split[1])
                if target_channel is None:
                    return event.create_response(
                        "Error, {} is not known on {}.".format(
                            line_split[1], server_obj.name
                        )
                    )
                return event.create_response(
                    self.send_kick(target_channel, target_user)
                )
            # If 2 arguments, try with first argument as channel
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel is not None and target_channel.in_channel:
                target_user = server_obj.get_user_by_name(line_split[1])
                if target_user is not None and target_channel.is_user_in_channel(
                    target_user
                ):
                    return event.create_response(
                        self.send_kick(target_channel, target_user)
                    )
                return event.create_response(
                    self.send_kick(target_channel, event.user, line_split[1])
                )
            # 2 args, try with second argument as channel
            target_user = server_obj.get_user_by_name(line_split[0])
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        line_split[0], server_obj.name
                    )
                )
            target_channel = server_obj.get_channel_by_name(line_split[1])
            if target_channel is not None and target_channel.in_channel:
                return event.create_response(
                    self.send_kick(target_channel, target_user)
                )
            return event.create_response(
                self.send_kick(event.channel, target_user, line_split[1])
            )
        # If message was in private message, it's either channel, user and message or user, channel and message or
        # channel and message
        if event.channel is None:
            target_channel = server_obj.get_channel_by_name(line_split[0])
            if target_channel is not None:
                if target_channel.in_channel:
                    target_user = server_obj.get_user_by_name(line_split[1])
                    if target_user is not None and target_channel.is_user_in_channel(
                        target_user
                    ):
                        return event.create_response(
                            self.send_kick(
                                target_channel, target_user, " ".join(line_split[2:])
                            )
                        )
                    return event.create_response(
                        self.send_kick(
                            target_channel, event.user, " ".join(line_split[1:])
                        )
                    )
                return event.create_response("Error, I am not in that channel.")
            target_user = server_obj.get_user_by_name(line_split[0])
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        line_split[0], server_obj.name
                    )
                )
            target_channel = server_obj.get_channel_by_name(line_split[1])
            if target_channel is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        line_split[1], server_obj.name
                    )
                )
            return event.create_response(
                self.send_kick(target_channel, target_user, " ".join(line_split[2:]))
            )
        # If more than 2 arguments, determine which of the first 2 is channel/user, the rest is a message.
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is not None and target_channel.is_user_in_channel(
                target_user
            ):
                return event.create_response(
                    self.send_kick(
                        target_channel, target_user, " ".join(line_split[2:])
                    )
                )
            return event.create_response(
                self.send_kick(target_channel, event.user, " ".join(line_split[1:]))
            )
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response(
                "Error, {} is not known on {}.".format(line_split[0], server_obj.name)
            )
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is not None and target_channel.in_channel:
            return event.create_response(
                self.send_kick(target_channel, target_user, " ".join(line_split[2:]))
            )
        return event.create_response(
            self.send_kick(event.channel, target_user, " ".join(line_split[1:]))
        )

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
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return "Error, I don't have power to kick users from {}.".format(
                channel.name
            )
        # Send invite
        kick_evt = EventKick(
            channel.server, channel, None, user, message, inbound=False
        )
        channel.server.send(kick_evt)
        return "Kicked {} from {}.".format(user.name, channel.name)
