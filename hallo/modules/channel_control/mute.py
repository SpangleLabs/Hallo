from hallo.events import EventMode
from hallo.function import Function
import hallo.modules.channel_control.channel_control
from hallo.destination import Channel
from hallo.server import Server


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
        self.help_docs = (
            "Mutes a given channel or current channel. Format: mute <channel>"
        )

    async def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't mute channels
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # Check if no arguments were provided
        if event.command_args.strip() == "":
            if event.channel is None:
                return event.create_response(
                    "Error, you can't set mute on a private message."
                )
            return event.create_response(await self.mute_channel(event.channel))
        # Get channel from user input
        target_channel = server_obj.get_channel_by_name(event.command_args.strip())
        if target_channel is None:
            return event.create_response(f"Error, {event.command_args.strip()} is not known on {server_obj.name}.")
        return event.create_response(await self.mute_channel(target_channel))

    async def mute_channel(self, channel: Channel) -> str:
        """
        Sets mute on a given channel.
        :param channel: Channel to mute
        :return: Response to send to requester
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if hallo has op in channel
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return f"Error, I don't have power to mute {channel.name}."
        # Send invite
        mode_evt = EventMode(channel.server, channel, None, "+m", inbound=False)
        await channel.server.send(mode_evt)
        return f"Set mute in {channel.name}."


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

    async def run(self, event):
        # Get server object
        server_obj = event.server
        # If server isn't IRC type, we can't unmute channels
        if server_obj.type != Server.TYPE_IRC:
            return event.create_response(
                "Error, this function is only available for IRC servers."
            )
        # Check if no arguments were provided
        if event.command_args.strip() == "":
            if event.channel is None:
                return event.create_response(
                    "Error, you can't unset mute on a private message."
                )
            return event.create_response(self.unmute_channel(event.channel))
        # Get channel from user input
        target_channel = server_obj.get_channel_by_name(event.command_args.strip())
        if target_channel is None:
            return event.create_response(f"Error, {event.command_args.strip()} is not known on {server_obj.name}.")
        return event.create_response(self.unmute_channel(target_channel))

    async def unmute_channel(self, channel: Channel) -> str:
        """
        Sets mute on a given channel.
        :param channel: Channel to mute
        :return: Response to send to requester
        """
        # Check if in channel
        if not channel.in_channel:
            return "Error, I'm not in that channel."
        # Check if hallo has op in channel
        if not hallo.modules.channel_control.channel_control.hallo_has_op(channel):
            return f"Error, I don't have power to unmute {channel.name}."
        # Send invite
        mode_evt = EventMode(channel.server, channel, None, "-m", inbound=False)
        await channel.server.send(mode_evt)
        return f"Unset mute in {channel.name}."
