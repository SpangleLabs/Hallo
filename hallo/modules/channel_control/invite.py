from hallo.events import EventInvite
from hallo.function import Function
import hallo.modules.channel_control.channel_control
from hallo.server import Server


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
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # If 0 arguments, ask for clarification
        line_split = event.command_args.split()
        if len(line_split) == 0:
            return event.create_response(
                "Error, please specify a user to invite and/or a channel to invite to."
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
                return event.create_response(self.send_invite(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(self.send_invite(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response(
                    "Error, {} is not known on {}.".format(
                        event.command_args, server_obj.name
                    )
                )
            return event.create_response(self.send_invite(event.channel, target_user))
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
            return event.create_response(self.send_invite(target_channel, target_user))
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
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return "Error, I don't have power to invite users in {}.".format(
                channel.name
            )
        # Send invite
        invite_evt = EventInvite(channel.server, channel, None, user, inbound=False)
        channel.server.send(invite_evt)
        return "Invite sent."