from abc import ABCMeta

from hallo.destination import Channel, User
from hallo.permission_mask import PermissionMask


class ServerException(Exception):
    pass


class Server(metaclass=ABCMeta):
    """
    Generic server object. An interface for ServerIRC or ServerSkype or whatever objects.
    """

    # Constants
    TYPE_IRC = "irc"
    TYPE_MOCK = "mock"
    TYPE_TELEGRAM = "telegram"
    STATE_CLOSED = "disconnected"
    STATE_OPEN = "connected"
    STATE_CONNECTING = "connecting"
    STATE_DISCONNECTING = "disconnecting"

    type = None

    def __init__(self, hallo):
        """
        Constructor for server object
        :param hallo: Hallo Instance of hallo that contains this server object
        :type hallo: hallo.Hallo
        """
        self.hallo = hallo  # The hallo object that created this server
        # Persistent/saved class variables
        self.name = None  # Server name
        self.auto_connect = (
            True  # Whether to automatically connect to this server when hallo starts
        )
        self.channel_list = (
            []
        )  # List of channels on this server (which may or may not be currently active)
        """ :type : list[Destination.Channel]"""
        self.user_list = []  # Users on this server (not all of which are online)
        """ :type : list[Destination.User]"""
        self.nick = None  # Nickname to use on this server
        self.prefix = None  # Prefix to use with functions on this server
        self.full_name = None  # Full name to use on this server
        self.permission_mask = PermissionMask()  # PermissionMask for the server
        """ :type : PermissionMask"""
        # Dynamic/unsaved class variables
        self.state = Server.STATE_CLOSED  # Current state of the server, replacing open

    def __eq__(self, other):
        return (
            isinstance(other, Server)
            and self.hallo == other.hallo
            and self.type == other.type
            and self.name.lower() == other.name.lower()
        )

    def __hash__(self):
        return hash((self.hallo, self.type, self.name.lower()))

    def start(self):
        """
        Starts the new server, launching new thread as appropriate.
        """
        raise NotImplementedError

    def disconnect(self, force=False):
        """
        Disconnects from the server, shutting down remaining threads
        """
        raise NotImplementedError

    def reconnect(self):
        """
        Disconnects and reconnects from the server
        """
        self.disconnect()
        self.start()

    def send(self, event):
        """
        Sends a message to the server, or a specific channel in the server
        :param event: Event to send, should be outbound.
        :type event: events.ServerEvent
        :rtype : events.ServerEvent | None
        """
        raise NotImplementedError

    def reply(self, old_event, new_event):
        """
        Sends a message as a reply to another message, such as a response to a function call
        :param old_event: The event which was received, to reply to
        :type old_event: events.ChannelUserTextEvent
        :param new_event: The event to be sent
        :type new_event: events.ChannelUserTextEvent
        """
        # This method will just do some checks, implementations will have to actually send events
        if not old_event.is_inbound or new_event.is_inbound:
            raise ServerException("Cannot reply to outbound event, or send inbound one")
        if old_event.channel != new_event.channel:
            raise ServerException(
                "Cannot send reply to a different channel than original message came from"
            )
        if new_event.user is not None and old_event.user != new_event.user:
            raise ServerException(
                "Cannot send reply to a different private chat than original message came from"
            )
        if old_event.server != new_event.server:
            raise ServerException(
                "Cannot send reply to a different server than the original message came from"
            )
        return

    def to_json(self):
        """
        Returns a dict formatted so it may be serialised into json configuration data
        :return: dict
        """
        raise NotImplementedError

    def get_nick(self):
        """Nick getter"""
        if self.nick is None:
            return self.hallo.default_nick
        return self.nick

    def set_nick(self, nick):
        """
        Nick setter
        :param nick: New nick for hallo to use on this server
        :type nick: str
        """
        self.nick = nick

    def get_prefix(self):
        """Prefix getter"""
        if self.prefix is None:
            return self.hallo.default_prefix
        return self.prefix

    def set_prefix(self, prefix):
        """
        Prefix setter
        :param prefix: Prefix for hallo to use for function calls on this server
        :type prefix: str | bool | None
        """
        self.prefix = prefix

    def get_full_name(self):
        """Full name getter"""
        if self.full_name is None:
            return self.hallo.default_full_name
        return self.full_name

    def set_full_name(self, full_name):
        """
        Full name setter
        :param full_name: Full name for Hallo to use on this server
        :type full_name: str
        """
        self.full_name = full_name

    def get_auto_connect(self):
        """AutoConnect getter"""
        return self.auto_connect

    def set_auto_connect(self, auto_connect):
        """
        AutoConnect setter
        :param auto_connect: Whether or not to autoconnect to the server
        :type auto_connect: bool
        """
        self.auto_connect = auto_connect

    def is_connected(self):
        """Returns boolean representing whether the server is connected or not."""
        return self.state == Server.STATE_OPEN

    def get_channel_by_name(self, channel_name):
        """
        Returns a Channel object with the specified channel name.
        :param channel_name: Name of the channel which is being searched for
        :type channel_name: str
        :rtype: Optional[Destination.Channel]
        """
        channel_name = channel_name.lower()
        for channel in self.channel_list:
            if channel.name == channel_name:
                return channel
        return None

    def get_channel_by_address(self, address, channel_name=None):
        """
        Returns a Channel object with the specified channel name.
        :param address: Address of the channel
        :type address: str
        :param channel_name: Name of the channel which is being searched for
        :type channel_name: str
        :rtype: destination.Channel
        """
        for channel in self.channel_list:
            if channel.address == address:
                return channel
        if channel_name is None:
            channel_name = self.get_name_by_address(address)
        new_channel = Channel(self, address, channel_name)
        self.add_channel(new_channel)
        return new_channel

    def get_name_by_address(self, address):
        """
        Returns the name of a destination, based on the address
        :param address: str
        :return: str
        """
        raise NotImplementedError()

    def add_channel(self, channel_obj):
        """
        Adds a channel to the channel list
        :param channel_obj: Adds a channel to the list, without joining it
        :type channel_obj: destination.Channel
        """
        self.channel_list.append(channel_obj)

    def join_channel(self, channel_obj):
        """
        Joins a specified channel
        :param channel_obj: Channel to join
        :type channel_obj: destination.Channel
        """
        raise NotImplementedError

    def leave_channel(self, channel_obj):
        """
        Leaves a specified channel
        :param channel_obj: Channel for hallo to leave
        :type channel_obj: destination.Channel
        """
        # If channel isn't in channel list, do nothing
        if channel_obj not in self.channel_list:
            return
        # Set channel to not AutoJoin, for the future
        channel_obj.auto_join = False
        # Set not in channel
        channel_obj.set_in_channel(False)

    def get_user_by_name(self, user_name):
        """
        Returns a User object with the specified user name.
        :param user_name: Name of user which is being searched for
        :type user_name: str
        :rtype: destination.User | None
        """
        user_name = user_name.lower()
        for user in self.user_list:
            if user.name == user_name:
                return user
        # No user by that name exists, return None
        return None

    def get_user_by_address(self, address, user_name=None):
        """
        Returns a User object with the specified user name.
        :param address: address of the user which is being searched for or added
        :type address: str
        :param user_name: Name of user which is being searched for
        :type user_name: str
        :return: Destination.User | None
        """
        for user in self.user_list:
            if user.address == address:
                return user
        if user_name is None:
            user_name = self.get_name_by_address(address)
        # No user by that name exists, so create one
        new_user = User(self, address, user_name)
        self.add_user(new_user)
        return new_user

    def get_user_list(self):
        """Returns the full list of users on this server."""
        return self.user_list

    def add_user(self, user_obj):
        """
        Adds a user to the user list
        :param user_obj: User to add to user list
        :type user_obj: destination.User
        """
        self.user_list.append(user_obj)

    def rights_check(self, right_name):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the right to check default server value for
        :type right_name: str
        """
        if self.permission_mask is not None:
            right_value = self.permission_mask.get_right(right_name)
            # If PermissionMask contains that right, return it.
            if right_value in [True, False]:
                return right_value
        # Fallback to the parent Hallo's decision.
        return self.hallo.rights_check(right_name)

    def check_user_identity(self, user_obj):
        """
        Check if a user is identified and verified
        :param user_obj: User to check identity of
        :type user_obj: destination.User
        """
        raise NotImplementedError
