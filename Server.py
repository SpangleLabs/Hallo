from abc import ABCMeta

from Destination import Channel, User
from PermissionMask import PermissionMask


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
    MSG_MSG = "message"
    MSG_NOTICE = "notice"
    MSG_RAW = "raw"
    STATE_CLOSED = "disconnected"
    STATE_OPEN = "connected"
    STATE_CONNECTING = "connecting"
    STATE_DISCONNECTING = "disconnecting"

    type = None

    def __init__(self, hallo):
        """
        Constructor for server object
        :param hallo: Hallo Instance of hallo that contains this server object
        :type hallo: Hallo.Hallo
        """
        self.hallo = hallo  # The hallo object that created this server
        # Persistent/saved class variables
        self.name = None  # Server name
        self.auto_connect = True  # Whether to automatically connect to this server when hallo starts
        self.channel_list = []  # List of channels on this server (which may or may not be currently active)
        self.user_list = []  # Users on this server (not all of which are online)
        self.nick = None  # Nickname to use on this server
        self.prefix = None  # Prefix to use with functions on this server
        self.full_name = None  # Full name to use on this server
        self.permission_mask = PermissionMask()  # PermissionMask for the server
        # Dynamic/unsaved class variables
        self.state = Server.STATE_CLOSED  # Current state of the server, replacing open

    def __eq__(self, other):
        return isinstance(other, Server) and self.hallo == other.hallo and self.type == other.type and \
               self.name.lower() == other.name.lower()

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

    def send(self, data, destination_obj=None, msg_type=MSG_MSG):
        """
        Sends a message to the server, or a specific channel in the server
        :param data: Line of data to send to server
        :type data: str
        :param destination_obj: Destination to send data to
        :type destination_obj: Destination.Destination | None
        :param msg_type: Type of message which is being sent
        :type msg_type: str
        """
        raise NotImplementedError

    @staticmethod
    def from_xml(xml_string, hallo):
        """
        Constructor to build a new server object from xml
        :param xml_string: XML string representation of the server
        :type xml_string: str
        :param hallo: Hallo object which is connected to this server
        :type hallo: Hallo.Hallo
        """
        raise NotImplementedError

    def to_xml(self):
        """
        Returns an XML representation of the server object
        """
        raise NotImplementedError

    def get_hallo(self):
        """Returns the Hallo instance that created this Server"""
        return self.hallo

    def get_name(self):
        """Name getter"""
        return self.name

    def get_nick(self):
        """Nick getter"""
        if self.nick is None:
            return self.hallo.get_default_nick()
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
            return self.hallo.get_default_prefix()
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
            return self.hallo.get_default_full_name()
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

    def get_type(self):
        """Type getter"""
        return self.type

    def get_permission_mask(self):
        return self.permission_mask

    def is_connected(self):
        """Returns boolean representing whether the server is connected or not."""
        return self.state == Server.STATE_OPEN

    def get_channel_by_name(self, channel_name, address=None):
        # TODO: fix all usages of this
        """
        Returns a Channel object with the specified channel name.
        :param channel_name: Name of the channel which is being searched for
        :type channel_name: str
        :param address: Address of the channel
        :type address: str
        :return: Destination.Channel
        """
        channel_name = channel_name.lower()
        for channel in self.channel_list:
            if channel.get_name() == channel_name:
                return channel
        new_channel = None
        if address is not None:
            new_channel = Channel(self, address, channel_name)
            self.add_channel(new_channel)
        else:
            self.hallo.printer.print_raw("WARNING: Server.get_channel_by_name() used without address")
        return new_channel

    def get_channel_by_address(self, address, channel_name):
        """
        Returns a Channel object with the specified channel name.
        :param address: Address of the channel
        :type address: str
        :param channel_name: Name of the channel which is being searched for
        :type channel_name: str
        :return: Destination.Channel
        """
        for channel in self.channel_list:
            if channel.address == address:
                return channel
        new_channel = Channel(self, address, channel_name)
        self.add_channel(new_channel)
        return new_channel

    def get_channel_list(self):
        return self.channel_list

    def add_channel(self, channel_obj):
        """
        Adds a channel to the channel list
        :param channel_obj: Adds a channel to the list, without joining it
        :type channel_obj: Destination.Channel
        """
        self.channel_list.append(channel_obj)

    def join_channel(self, channel_obj):
        """
        Joins a specified channel
        :param channel_obj: Channel to join
        :type channel_obj: Destination.Channel
        """
        raise NotImplementedError

    def leave_channel(self, channel_obj):
        """
        Leaves a specified channel
        :param channel_obj: Channel for hallo to leave
        :type channel_obj: Destination.Channel
        """
        # If channel isn't in channel list, do nothing
        if channel_obj not in self.channel_list:
            return
        # Set channel to not AutoJoin, for the future
        channel_obj.set_auto_join(False)
        # Set not in channel
        channel_obj.set_in_channel(False)

    def get_user_by_name(self, user_name, address=None):
        # TODO: fix all usages of this
        """
        Returns a User object with the specified user name.
        :param user_name: Name of user which is being searched for
        :type user_name: str
        :param address: address of the user which is being searched for or added
        :type address: str | None
        :return: Destination.User | None
        """
        user_name = user_name.lower()
        for user in self.user_list:
            if user.get_name() == user_name:
                return user
        # No user by that name exists, so create one, provided address is supplied
        new_user = None
        if address is not None:
            new_user = User(self, address, user_name)
            self.add_user(new_user)
        else:
            self.hallo.printer.print_raw("WARNING: Server.get_user_by_name() used without address")
        return new_user

    def get_user_by_address(self, address, user_name):
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
        :type user_obj: Destination.User
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
        :type user_obj: Destination.User
        """
        raise NotImplementedError
