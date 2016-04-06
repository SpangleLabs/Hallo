import time

from xml.dom import minidom
from PermissionMask import PermissionMask
from inc.commons import Commons
from abc import ABCMeta


class Destination(metaclass=ABCMeta):
    """
    Abstract class for Channel and User. It just means messages can be sent to these entities.
    """

    TYPE_CHANNEL = "channel"
    TYPE_USER = "user"

    def __init__(self):
        self.type = None  # The type of destination, "channel" or "user"
        self.server = None  # The server object this destination belongs to
        self.name = None  # Destination name, where to send messages
        self.logging = True  # Whether logging is enabled for this destination
        self.last_active = True  # Timestamp of when they were last active
        self.use_caps_lock = False  # Whether to use caps lock when communicating to this destination
        self.permission_mask = None  # PermissionMask for the destination object

    def get_name(self):
        """Name getter"""
        return self.name.lower()

    def set_name(self, name):
        """
        Name setter
        :param name: Name of the destination
        """
        self.name = name.lower()

    def get_type(self):
        """
        Returns whether the destination is a user or channel.
        """
        return self.type

    def is_channel(self):
        """Boolean, whether the destination is a channel."""
        if self.type == Destination.TYPE_CHANNEL:
            return True
        else:
            return False

    def is_user(self):
        """Boolean, whether the destination is a user."""
        if self.type == Destination.TYPE_CHANNEL:
            return False
        else:
            return True

    def get_logging(self):
        """Boolean, whether the destination is supposed to have logging."""
        return self.logging

    def set_logging(self, logging):
        """
        Sets whether the destination is logging.
        :param logging: Boolean, whether or not to log destination content
        """
        self.logging = logging

    def get_server(self):
        """Returns the server object that this destination belongs to"""
        return self.server

    def update_activity(self):
        """Updates LastActive timestamp"""
        self.last_active = time.time()

    def get_last_active(self):
        """Returns when the destination was last active"""
        return self.last_active

    def is_upper_case(self):
        """Returns a boolean representing whether to use caps lock"""
        return self.use_caps_lock

    def set_upper_case(self, upper_case):
        """
        Sets whether the destination uses caps lock
        :param upper_case: Boolean, whether or not this destination is caps-lock only
        """
        self.use_caps_lock = upper_case

    def is_persistent(self):
        """
        Defines whether a Destination object is persistent.
        That is to say, whether it needs saving, or can be generated anew.
        """
        raise NotImplementedError

    def get_permission_mask(self):
        return self.permission_mask

    def to_xml(self):
        """Returns the Destination object XML"""
        raise NotImplementedError

    @staticmethod
    def from_xml(xml_string, server):
        """
        Loads a new Destination object from XML
        :param xml_string: XML string to parse to create destination
        :param server: Server on which the destination is located
        """
        raise NotImplementedError


class Channel(Destination):

    def __init__(self, name, server):
        """
        Constructor for channel object
        """
        super().__init__()
        self.type = Destination.TYPE_CHANNEL  # This is a channel object
        self.password = None  # Channel password, or none.
        self.user_list = set()  # Set of users in the channel
        self.in_channel = False  # Whether or not hallo is in the channel
        self.passive_enabled = True  # Whether to use passive functions in the channel
        self.auto_join = False  # Whether hallo should automatically join this channel when loading
        self.prefix = None  # Prefix for calling functions. None means inherit from Server. False means use nick.
        self.name = name.lower()
        self.server = server

    def get_password(self):
        """Channel password getter"""
        return self.password

    def set_password(self, password):
        """
        Channel password setter
        :param password: Password of the channel
        :type password: str | None
        """
        self.password = password

    def get_prefix(self):
        """Returns the channel prefix."""
        if self.prefix is None:
            return self.server.get_prefix()
        return self.prefix

    def set_prefix(self, new_prefix):
        """
        Sets the channel function prefix.
        :param new_prefix: New prefix to use to identify calls to hallo in this destination
        :type new_prefix: bool | str | None
        """
        self.prefix = new_prefix

    def get_user_list(self):
        """Returns the full user list of the channel"""
        return self.user_list

    def add_user(self, user):
        """
        Adds a new user to a given channel
        :param user: User object to add to channel's user list
        :type user: User
        """
        self.user_list.add(user)
        user.add_channel(self)

    def set_user_list(self, user_list):
        """
        Sets the entire user list of a channel
        :param user_list: List of users which are currently in the channel.
        :type user_list: set
        """
        self.user_list = user_list
        for user in user_list:
            user.add_channel(self)

    def remove_user(self, user):
        """
        Removes a user from a given channel
        :param user: User to remove from channel's user list
        :type user: User
        """
        try:
            self.user_list.remove(user)
            user.remove_channel(self)
        except KeyError:
            pass

    def is_user_in_channel(self, user):
        """
        Returns a boolean as to whether the user is in this channel
        :param user: User being checked
        :type user: User
        """
        return user in self.user_list

    def is_passive_enabled(self):
        """Whether or not passive functions are enabled in this channel"""
        return self.passive_enabled

    def set_passive_enabled(self, passive_enabled):
        """
        Sets whether passive functions are enabled in this channel
        :param passive_enabled: Boolean, whether functions triggered indirectly are enabled for this channel.
        :type passive_enabled: bool
        """
        self.passive_enabled = passive_enabled

    def is_auto_join(self):
        """Whether or not hallo should automatically join this channel"""
        return self.auto_join

    def set_auto_join(self, auto_join):
        """
        Sets whether hallo automatically joins this channel
        :param auto_join: Boolean, whether or not to join this channel when the server connects.
        :type auto_join: bool
        """
        self.auto_join = auto_join

    def is_in_channel(self):
        """Whether or not hallo is in this channel"""
        return self.in_channel

    def set_in_channel(self, in_channel):
        """
        Sets whether hallo is in this channel
        :param in_channel: Boolean, whether hallo is in this channel.
        :type in_channel: bool
        """
        self.in_channel = in_channel
        if in_channel is False:
            self.user_list = set()

    def rights_check(self, right_name):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the user right to check
        :type right_name: str
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

    def to_xml(self):
        """Returns the Channel object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("channel")
        doc.appendChild(root)
        # create name element
        name_elem = doc.createElement("channel_name")
        name_elem.appendChild(doc.createTextNode(self.name))
        root.appendChild(name_elem)
        # create logging element
        logging_elem = doc.createElement("logging")
        logging_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.logging]))
        root.appendChild(logging_elem)
        # create caps_lock element, to say whether to use caps lock
        caps_lock_elem = doc.createElement("caps_lock")
        caps_lock_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.use_caps_lock]))
        root.appendChild(caps_lock_elem)
        # create password element
        if self.password is not None:
            password_elem = doc.createElement("password")
            password_elem.appendChild(doc.createTextNode(self.password))
            root.appendChild(password_elem)
        # create passive_enabled element, saying whether passive functions are enabled
        passive_enabled_elem = doc.createElement("passive_enabled")
        passive_enabled_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.passive_enabled]))
        root.appendChild(passive_enabled_elem)
        # create auto_join element, whether or not to automatically join a channel
        auto_join_elem = doc.createElement("auto_join")
        auto_join_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.auto_join]))
        root.appendChild(auto_join_elem)
        # create permission_mask element
        if not self.permission_mask.is_empty():
            permission_mask_elem = minidom.parseString(self.permission_mask.to_xml()).firstChild
            root.appendChild(permission_mask_elem)
        # output XML string
        return doc.toxml()

    @staticmethod
    def from_xml(xml_string, server):
        """
        Loads a new Channel object from XML
        :param xml_string: XML string representation of the channel
        :type xml_string: str
        :param server: Server the channel is on
        :type server: Server.Server
        """
        doc = minidom.parseString(xml_string)
        new_name = doc.getElementsByTagName("channel_name")[0].firstChild.data
        channel = Channel(new_name, server)
        channel.logging = Commons.string_from_file(doc.getElementsByTagName("logging")[0].firstChild.data)
        channel.use_caps_lock = Commons.string_from_file(doc.getElementsByTagName("caps_lock")[0].firstChild.data)
        if len(doc.getElementsByTagName("password")) != 0:
            channel.password = doc.getElementsByTagName("password")[0].firstChild.data
        channel.passive_enabled = Commons.string_from_file(
            doc.getElementsByTagName("passive_enabled")[0].firstChild.data)
        channel.auto_join = Commons.string_from_file(doc.getElementsByTagName("auto_join")[0].firstChild.data)
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            channel.permission_mask = PermissionMask.from_xml(doc.getElementsByTagName("permission_mask")[0].toxml())
        return channel


class User(Destination):

    def __init__(self, name, server):
        """
        Constructor for user object
        :param name: Name of the user
        :type name: str
        :param server: Server the user is on
        :type server: Server.Server
        """
        super().__init__()
        self.type = Destination.TYPE_USER  # This is a user object
        self.identified = False  # Whether the user is identified (with nickserv)
        self.channel_list = set()  # Set of channels this user is in
        self.online = False  # Whether or not the user is online
        self.user_group_list = {}  # List of UserGroups this User is a member of
        self.name = name.lower()
        self.server = server

    def is_identified(self):
        """Checks whether this user is identified"""
        if not self.identified:
            self.check_identity()
        return self.identified

    def set_identified(self, identified):
        """
        Sets whether this user is identified
        :param identified: Boolean, whether this user is identified
        :type identified: bool
        """
        self.identified = identified

    def check_identity(self):
        """Checks with the server whether this user is identified."""
        identity_result = self.server.check_user_identity(self)
        self.identified = identity_result

    def get_channel_list(self):
        """Returns the list of channels this user is in"""
        return self.channel_list

    def add_channel(self, channel):
        """
        Adds a new channel to a given user
        :param channel: Channel to add to user's channel list
        :type channel: Channel
        """
        self.channel_list.add(channel)

    def remove_channel(self, channel):
        """
        Removes a channel from a given user
        :param channel: Channel to remove from user's channel list
        :type channel: Channel
        """
        self.channel_list.remove(channel)

    def set_channel_list(self, channel_list):
        """
        Sets the entire channel list of a user
        :param channel_list: List of channels the user is in
        :type channel_list: set
        """
        self.channel_list = channel_list

    def add_user_group(self, new_user_group):
        """
        Adds a User to a UserGroup
        :param new_user_group: User group to add the user to
        :type new_user_group: UserGroup.UserGroup
        """
        new_user_group_name = new_user_group.get_name()
        self.user_group_list[new_user_group_name] = new_user_group

    def get_user_group_by_name(self, user_group_name):
        """
        Returns the UserGroup with the matching name
        :param user_group_name: Returns the user group by the specified name that this user is in
        :type user_group_name: str
        """
        if user_group_name in self.user_group_list:
            return self.user_group_list[user_group_name]
        return None

    def get_user_group_list(self):
        """Returns the full list of UserGroups this User is a member of"""
        return self.user_group_list

    def remove_user_group_by_name(self, user_group_name):
        """
        Removes the UserGroup by the given name from a user
        :param user_group_name: Removes the user group matching this name that the user is in
        :type user_group_name: str
        """
        del self.user_group_list[user_group_name]

    def is_online(self):
        """Whether the user appears to be online"""
        return self.online

    def set_online(self, online):
        """
        Sets whether the user is online
        :param online: Boolean, whether the user is online
        :type online: bool
        """
        self.online = online
        if online is False:
            self.identified = False
            self.channel_list = set()

    def rights_check(self, right_name, channel_obj=None):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the user right to check
        :type right_name: str
        :param channel_obj: Channel in which the right is being checked
        :type channel_obj: Channel
        """
        if self.permission_mask is not None:
            right_value = self.permission_mask.get_right(right_name)
            # If PermissionMask contains that right, return it.
            if right_value in [True, False]:
                return right_value
        # Check UserGroup rights, if any apply
        if len(self.user_group_list) != 0:
            return any(
                [userGroup.rights_check(right_name, self, channel_obj) for userGroup in self.user_group_list.values()])
        # Fall back to channel, if defined
        if channel_obj is not None and channel_obj.is_channel():
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
        # Otherwise it can be generated anew to be identical.
        return False

    def to_xml(self):
        """Returns the User object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("user")
        doc.appendChild(root)
        # create name element
        name_elem = doc.createElement("user_name")
        name_elem.appendChild(doc.createTextNode(self.name))
        root.appendChild(name_elem)
        # create logging element
        logging_elem = doc.createElement("logging")
        logging_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.logging]))
        root.appendChild(logging_elem)
        # create caps_lock element, to say whether to use caps lock
        caps_lock_elem = doc.createElement("caps_lock")
        caps_lock_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.use_caps_lock]))
        root.appendChild(caps_lock_elem)
        # create user_group list
        user_group_list_elem = doc.createElement("user_group_membership")
        for user_group_name in self.user_group_list:
            user_group_elem = doc.createElement("user_group_name")
            user_group_elem.appendChild(doc.createTextNode(user_group_name))
            user_group_list_elem.appendChild(user_group_elem)
        root.appendChild(user_group_list_elem)
        # create permission_mask element
        if not self.permission_mask.is_empty():
            permission_mask_elem = minidom.parseString(self.permission_mask.to_xml()).firstChild
            root.appendChild(permission_mask_elem)
        # output XML string
        return doc.toxml()

    @staticmethod
    def from_xml(xml_string, server):
        """
        Loads a new User object from XML
        :param xml_string: XML string representation of the user to create
        :type xml_string: str
        :param server: Server which the user is on
        :type server: Server.Server
        """
        doc = minidom.parseString(xml_string)
        new_name = doc.getElementsByTagName("user_name")[0].firstChild.data
        new_user = User(new_name, server)
        new_user.logging = Commons.string_from_file(doc.getElementsByTagName("logging")[0].firstChild.data)
        new_user.use_caps_lock = Commons.string_from_file(doc.getElementsByTagName("caps_lock")[0].firstChild.data)
        # Load UserGroups from XML
        user_group_list_elem = doc.getElementsByTagName("user_group_membership")[0]
        for user_group_elem in user_group_list_elem.getElementsByTagName("user_group_name"):
            user_group_name = user_group_elem.firstChild.data
            user_group = server.get_hallo().get_user_group_by_name(user_group_name)
            if user_group is not None:
                new_user.add_user_group(user_group)
        # Add PermissionMask, if one exists
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            new_user.permission_mask = PermissionMask.from_xml(doc.getElementsByTagName("permission_mask")[0].toxml())
        return new_user
