from hallo.destination import Channel, User
from hallo.events import EventMode
from hallo.function import Function
import hallo.modules.channel_control.channel_control
from hallo.server import Server


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
        self.names = {
            "op",
            "operator",
            "give op",
            "gib op",
            "get op",
            "give operator",
            "gib operator",
            "get operator",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Op member in given channel, or current channel if no channel given. Or command user if no "
            "member given. Format: op <name> <channel>"
        )

    async def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't give op.
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # If 0 arguments, op user who called command.
        line_split = event.command_args.split()
        if len(line_split) == 0:
            # Check that this is a channel
            if event.channel is None:
                return event.create_response(
                    "Error, I can't op you in a private message, please provide a channel."
                )
            # Give op to the user
            return event.create_response(await self.give_op(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response(f"Error, {event.command_args} is not known on {server_obj.name}.")
                return event.create_response(await self.give_op(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(await self.give_op(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response(f"Error, {event.command_args} is not known on {server_obj.name}.")
            return event.create_response(await self.give_op(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response(f"Error, {line_split[1]} is not known on {server_obj.name}.")
            return event.create_response(await self.give_op(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response(f"Error, {line_split[0]} is not known on {server_obj.name}.")
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response(
                f"Error, {line_split[1]} is not known on {server_obj.name}."
            )
        return event.create_response(await self.give_op(target_channel, target_user))

    async def give_op(self, channel: Channel, user: User) -> str:
        """
        Gives op to a user in a given channel, after checks.
        :param channel: Channel to give user op in
        :param user: User to give op to
        :return: Response to send to requester
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return f"Error, {user.name} is not in {channel.name}."
        # Check if hallo has op in channel
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return f"Error, I don't have power to give op in {channel.name}."
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if user_membership.is_op:
            return "Error, this user already has op."
        mode_evt = EventMode(
            channel.server, channel, None, f"+o {user.address}", inbound=False
        )
        await channel.server.send(mode_evt)
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
        self.names = {
            "deop",
            "deoperator",
            "unoperator",
            "take op",
            "del op",
            "delete op",
            "remove op",
            "take operator",
            "del operator",
            "delete op",
            "remove operator",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Deop member in given channel, or current channel if no channel given. Or command user if "
            "no member given. Format: deop <name> <channel>"
        )

    async def run(self, event):
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
                return event.create_response(
                    "Error, I can't de-op you in a private message, please provide a channel."
                )
            # Remove op
            return event.create_response(await self.take_op(event.channel, event.user))
        # If 1 argument, see if it's a channel or a user.
        if len(line_split) == 1:
            # If message was sent in private message, it's referring to a channel
            if event.channel is None:
                channel = server_obj.get_channel_by_name(event.command_args)
                if channel is None:
                    return event.create_response(f"Error, {event.command_args} is not known on {server_obj.name}.")
                return event.create_response(await self.take_op(channel, event.user))
            # See if it's a channel that hallo is in
            test_channel = server_obj.get_channel_by_name(event.command_args)
            if test_channel is not None and test_channel.in_channel:
                return event.create_response(await self.take_op(test_channel, event.user))
            # Argument must be a user?
            target_user = server_obj.get_user_by_name(event.command_args)
            if target_user is None:
                return event.create_response(f"Error, {event.command_args} is not known on {server_obj.name}.")
            return event.create_response(await self.take_op(event.channel, target_user))
        # If 2 arguments, try with first argument as channel
        target_channel = server_obj.get_channel_by_name(line_split[0])
        if target_channel is not None and target_channel.in_channel:
            target_user = server_obj.get_user_by_name(line_split[1])
            if target_user is None:
                return event.create_response(f"Error, {line_split[1]} is not known on {server_obj.name}.")
            return event.create_response(await self.take_op(target_channel, target_user))
        # 2 args, try with second argument as channel
        target_user = server_obj.get_user_by_name(line_split[0])
        if target_user is None:
            return event.create_response(f"Error, {line_split[0]} is not known on {server_obj.name}.")
        target_channel = server_obj.get_channel_by_name(line_split[1])
        if target_channel is None:
            return event.create_response(f"Error, {line_split[1]} is not known on {server_obj.name}.")
        return event.create_response(await self.take_op(target_channel, target_user))

    async def take_op(self, channel: Channel, user: User) -> str:
        """
        Takes op from a user in a given channel, after checks.
        :param channel: Channel to take user op in
        :param user: User to take op from
        :return: Response to send to requester
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if user is in channel
        if user not in channel.get_user_list():
            return f"Error, {user.name} is not in {channel.name}."
        # Check if hallo has op in channel
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return f"Error, I don't have power to take op in {channel.name}."
        # Check that user does not have op in channel
        user_membership = channel.get_membership_by_user(user)
        if not user_membership.is_op:
            return "Error, this user doesn't have op."
        mode_evt = EventMode(
            channel.server, channel, None, f"-o {user.address}", inbound=False
        )
        await channel.server.send(mode_evt)
        return "Op status taken."
