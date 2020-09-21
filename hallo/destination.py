import time
from typing import Optional

from hallo.permission_mask import PermissionMask
from abc import ABCMeta


class Destination(metaclass=ABCMeta):
    """
    Abstract class for Channel and User. It just means messages can be sent to these entities.
    """

    def __init__(self, server, address, name):
        self.server = server  # The server object this destination belongs to
        """:type : Server.Server"""
        self.address = address
        """:type : str"""
        self.name = name  # Destination name, where to send messages
        """:type : str"""
        self.logging = True  # Whether logging is enabled for this destination
        """:type : bool"""
        self.last_active = None  # Timestamp of when they were last active
        """:type : float | None"""
        self.use_caps_lock = (
            False  # Whether to use caps lock when communicating to this destination
        )
        """:type : bool"""
        self.permission_mask = (
            PermissionMask()
        )  # PermissionMask for the destination object
        """:type : PermissionMask.PermissionMask"""
        self.memberships_list = set()  # Set of ChannelMemberships for User or Channel
        """:type : set[ChannelMembership]"""

    def is_channel(self):
        """
        Boolean, whether the destination is a channel.
        :rtype : bool
        """
        if isinstance(self, Channel):
            return True
        else:
            return False

    def is_user(self):
        """
        Boolean, whether the destination is a user.
        :rtype : bool
        """
        if isinstance(self, Channel):
            return False
        else:
            return True

    def update_activity(self):
        """Updates LastActive timestamp"""
        self.last_active = time.time()

    def is_persistent(self):
        """
        Defines whether a Destination object is persistent.
        That is to say, whether it needs saving, or can be generated anew.
        :rtype : bool
        """
        raise NotImplementedError

    def rights_check(self, right_name):
        raise NotImplementedError


class Channel(Destination):
    def __init__(self, server, address, name):
        """
        Constructor for channel object
        :type name: str
        :type server: server.Server
        """
        super().__init__(server, address, name)
        self.password = None  # Channel password, or none.
        """:type : str | None"""
        self.in_channel = False  # Whether or not hallo is in the channel
        """:type : bool"""
        self.passive_enabled = True  # Whether to use passive functions in the channel
        """:type : bool"""
        self.auto_join = (
            False  # Whether hallo should automatically join this channel when loading
        )
        """:type : bool"""
        self.prefix = None  # Prefix for calling functions. None means inherit from Server. False means use nick.
        """:type : bool | None | str"""

    def __eq__(self, other):
        return (
            isinstance(other, Channel)
            and self.server == other.server
            and self.address == other.address
        )

    def __hash__(self):
        return hash(self.address)

    def get_prefix(self):
        """
        Returns the channel prefix.
        :rtype : bool | str
        """
        if self.prefix is None:
            return self.server.get_prefix()
        return self.prefix

    def get_user_list(self):
        """
        Returns the full user list of the channel
        :rtype : set[User]
        """
        return set([membership.user for membership in self.memberships_list])

    def add_user(self, user):
        """
        Adds a new user to a given channel
        :param user: User object to add to channel's user list
        :type user: User
        """
        chan_membership = ChannelMembership(self, user)
        self.memberships_list.add(chan_membership)
        user.memberships_list.add(chan_membership)

    def set_user_list(self, user_list):
        """
        Sets the entire user list of a channel
        :param user_list: List of users which are currently in the channel.
        :type user_list: set[User]
        """
        # Remove any users not in the given user list
        remove_memberships = []
        for membership in self.memberships_list:
            if membership.user not in user_list:
                membership.user.memberships_list.remove(membership)
                remove_memberships.append(membership)
        for remove_membership in remove_memberships:
            self.memberships_list.remove(remove_membership)
        # Add any users not in membership list
        for user in user_list:
            if user not in [membership.user for membership in self.memberships_list]:
                self.add_user(user)

    def remove_user(self, user):
        """
        Removes a user from a given channel
        :param user: User to remove from channel's user list
        :type user: User
        """
        chan_membership = ChannelMembership(self, user)
        try:
            self.memberships_list.remove(chan_membership)
        except KeyError:
            pass
        try:
            user.memberships_list.remove(chan_membership)
        except KeyError:
            pass

    def is_user_in_channel(self, user):
        """
        Returns a boolean as to whether the user is in this channel
        :param user: User being checked
        :type user: User
        :rtype : bool
        """
        return user in [membership.user for membership in self.memberships_list]

    def get_membership_by_user(self, user):
        """
        Returns the channel membership matching this user, or None
        :param user: The user to get membership for
        :type user: User
        :rtype : ChannelMembership | None
        """
        for membership in self.memberships_list:
            if membership.user == user:
                return membership
        return None

    def set_in_channel(self, in_channel):
        """
        Sets whether hallo is in this channel
        :param in_channel: Boolean, whether hallo is in this channel.
        :type in_channel: bool
        """
        self.in_channel = in_channel
        if in_channel is False:
            for membership in self.memberships_list:
                membership.user.memberships_list.discard(membership)
            self.memberships_list = set()

    def rights_check(self, right_name: str) -> bool:
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the user right to check
        """
        if self.permission_mask is not None:
            right_value = self.permission_mask.get_right(right_name)
            # If PermissionMask contains that right, return it.
            if right_value in [True, False]:
                return right_value
        # Fallback to the parent Server's decision.
        return self.server.rights_check(right_name)

    def is_persistent(self):
        """Defines whether Channel is persistent. That is to say, whether it needs saving, or can be generated anew."""
        # If you need to rejoin this channel, then you need to save it
        if self.auto_join is True:
            return True
        # If channel has a password, you need to save it
        if self.password is not None:
            return True
        # If channel has logging disabled, save it
        if self.logging is False:
            return True
        # If channel has caps lock, save it
        if self.use_caps_lock is True:
            return True
        # If channel has specific permissions set, save it
        if not self.permission_mask.is_empty():
            return True
        # If channel has passive functions disabled, save it
        if self.passive_enabled is False:
            return True
        # Otherwise it can be generated anew to be identical.
        return False

    def to_json(self):
        """
        Returns a dictionary which can be serialised into a json config object
        :return: dict
        """
        json_obj = dict()
        json_obj["name"] = self.name
        json_obj["address"] = self.address
        json_obj["logging"] = self.logging
        json_obj["caps_lock"] = self.use_caps_lock
        json_obj["passive_enabled"] = self.passive_enabled
        json_obj["auto_join"] = self.auto_join
        if self.password is not None:
            json_obj["password"] = self.password
        if not self.permission_mask.is_empty():
            json_obj["permission_mask"] = self.permission_mask.to_json()
        return json_obj

    @staticmethod
    def from_json(json_obj, server):
        name = json_obj["name"]
        address = json_obj["address"]
        new_channel = Channel(server, address, name)
        new_channel.logging = json_obj["logging"]
        new_channel.use_caps_lock = json_obj["caps_lock"]
        new_channel.passive_enabled = json_obj["passive_enabled"]
        new_channel.auto_join = json_obj["auto_join"]
        if "password" in json_obj:
            new_channel.password = json_obj["password"]
        if "permission_mask" in json_obj:
            new_channel.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        return new_channel


class User(Destination):
    def __init__(self, server, address, name):
        """
        Constructor for user object
        :param name: Name of the user
        :type name: str
        :param server: Server the user is on
        :type server: server.Server
        """
        super().__init__(server, address, name)
        """:type : str"""
        self.identified = False  # Whether the user is identified (with nickserv)
        """:type : bool"""
        self.online = False  # Whether or not the user is online
        """:type : bool"""
        self.user_group_list = set()  # List of UserGroups this User is a member of
        """:type : set[UserGroup.UserGroup]"""
        self.extra_data_dict = (
            dict()
        )  # Dictionary of extra data, in the format of str->Any
        """:type : dict[str, Any]"""

    def __eq__(self, other):
        return (
            isinstance(other, User)
            and self.server == other.server
            and self.address == other.address
        )

    def __hash__(self):
        return hash(self.address)

    def is_identified(self):
        """
        Checks whether this user is identified
        :rtype : bool
        """
        if not self.identified:
            self.check_identity()
        return self.identified

    def check_identity(self):
        """Checks with the server whether this user is identified."""
        identity_result = self.server.check_user_identity(self)
        self.identified = identity_result

    def add_user_group(self, new_user_group):
        """
        Adds a User to a UserGroup
        :param new_user_group: User group to add the user to
        :type new_user_group: user_group.UserGroup
        """
        self.user_group_list.add(new_user_group)

    def get_user_group_by_name(self, user_group_name):
        """
        Returns the UserGroup with the matching name
        :param user_group_name: Returns the user group by the specified name that this user is in
        :type user_group_name: str
        :rtype : user_group.UserGroup | None
        """
        for user_group in self.user_group_list:
            if user_group.name == user_group_name:
                return user_group
        return None

    def remove_user_group(self, user_group):
        """
        Removes the UserGroup by the given name from a user
        :param user_group: Removes the user group matching this name that the user is in
        :type user_group: user_group.UserGroup
        """
        self.user_group_list.remove(user_group)

    def get_channel_list(self):
        """
        Returns a list of channels
        :return: list of channels the user is in
        :rtype: set[Channel]
        """
        return set([membership.channel for membership in self.memberships_list])

    def set_online(self, online):
        """
        Sets whether the user is online
        :param online: Boolean, whether the user is online
        :type online: bool
        """
        self.online = online
        if online is False:
            self.identified = False
            for membership in self.memberships_list:
                membership.channel.memberships_list.discard(membership)
            self.memberships_list = set()
            """:type : set[ChannelMembership]"""

    def rights_check(self, right_name: str, channel_obj: Optional[Channel] = None) -> bool:
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the user right to check
        :param channel_obj: Channel in which the right is being checked
        """
        if self.permission_mask is not None:
            right_value = self.permission_mask.get_right(right_name)
            # If PermissionMask contains that right, return it.
            if right_value in [True, False]:
                return right_value
        # Check UserGroup rights, if any apply
        if len(self.user_group_list) != 0:
            return any(
                [
                    user_group.rights_check(right_name, self, channel_obj)
                    for user_group in self.user_group_list
                ]
            )
        # Fall back to channel, if defined
        if channel_obj is not None:
            return channel_obj.rights_check(right_name)
        # Fall back to the parent Server's decision.
        return self.server.rights_check(right_name)

    def is_persistent(self):
        """Defines whether User is persistent. That is to say, whether it needs saving, or can be generated anew."""
        # If user is in any groups, save it
        if len(self.user_group_list) != 0:
            return True
        # If user has logging disabled, save it
        if self.logging is False:
            return True
        # If user has caps lock, save it
        if self.use_caps_lock is True:
            return True
        # If user has specific permissions set, save it
        if not self.permission_mask.is_empty():
            return True
        # If they have any extra data, save it
        if self.extra_data_dict:
            return True
        # Otherwise it can be generated anew to be identical.
        return False

    def to_json(self):
        """
        Creates a dict of the user object, to serialise and store as json configuration
        :return: dict
        """
        json_obj = dict()
        json_obj["name"] = self.name
        json_obj["address"] = self.address
        json_obj["logging"] = self.logging
        json_obj["caps_lock"] = self.use_caps_lock
        json_obj["user_groups"] = []
        for user_group in self.user_group_list:
            json_obj["user_groups"].append(user_group.name)
        if not self.permission_mask.is_empty():
            json_obj["permission_mask"] = self.permission_mask.to_json()
        if self.extra_data_dict:
            json_obj["extra_data"] = self.extra_data_dict
        return json_obj

    @staticmethod
    def from_json(json_obj, server):
        name = json_obj["name"]
        address = json_obj["address"]
        new_user = User(server, address, name)
        new_user.logging = json_obj["logging"]
        new_user.use_caps_lock = json_obj["caps_lock"]
        for user_group_name in json_obj["user_groups"]:
            user_group = server.hallo.get_user_group_by_name(user_group_name)
            if user_group is not None:
                new_user.add_user_group(user_group)
        if "permission_mask" in json_obj:
            new_user.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        if "extra_data" in json_obj:
            new_user.extra_data_dict = json_obj["extra_data"]
        return new_user


class ChannelMembership:
    def __init__(self, channel, user):
        """
        Constructor for ChannelMembership
        :param channel: Which channel is this a membership of
        :type channel: Channel
        :param user: Which use is the member
        :type user: User
        """
        self.channel = channel
        self.user = user
        self.is_op = False
        self.is_voice = False
        self.join_time = time.time()

    def __eq__(self, other):
        return isinstance(other, ChannelMembership) and (self.channel, self.user) == (
            other.channel,
            other.user,
        )

    def __hash__(self):
        return (self.channel, self.user).__hash__()
