from Function import Function
from inc.Commons import Commons


class PermissionControlException(Exception):
    pass


class Permissions(Function):
    """
    Change permissions for a specified PermissionMask
    """

    HALLO_NAMES = ["hallo", "core", "all", "*", "default"]
    SERVER_NAMES = ["server", "serv", "s"]
    CHANNEL_NAMES = ["channel", "chan", "room", "c"]
    USER_GROUP_NAMES = ["usergroup", "user_group", "user-group", "group"]
    USER_NAMES = ["user", "person", "u"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "permissions"
        # Names which can be used to address the function
        self.names = {"permissions", "permissionmask", "permission mask"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Changes the permissions of a specified permission map." \
                         " Format: permissions <location> <permission> <on/off>"

    def run(self, line, user_obj, destination_obj=None):
        line_split = line.split()
        if len(line_split) < 3:
            return "You need to specify a location, a right and the value"
        bool_input = line_split[-1]
        right_input = line_split[-2]
        location_input = line_split[:-2]
        # Search for the permission_mask they want.
        try:
            permission_mask = self.find_permission_mask(location_input, user_obj,
                                                        destination_obj if destination_obj.is_channel() else None)
        # If it comes back with an error message, return that error
        except PermissionControlException as e:
            return str(e)
        # If it comes back unspecified, generic error message
        if permission_mask is None:
            return "Error, I can't find that permission mask. Specify which you wish to modify as user={username}, " \
                   "or similarly for usergroup, channel, server or hallo."
        # Turn bool_input into a boolean
        bool_bool = Commons.string_to_bool(bool_input)
        # Check if boolean input is valid
        if bool_bool is None:
            return "Error, I don't understand your boolean value. Please use true or false."
        # Set the right
        permission_mask.set_right(right_input, bool_bool)
        return "Set "+right_input+" to "+{True: "true", False: "false"}[bool_bool]+"."

    def find_permission_mask(self, location_input, user_obj, destination_obj):
        """
        Finds a permission mask by a given user input
        :param location_input: User input specifying permission mask
        :type location_input: list[str]
        :param user_obj: User who asked for permission mask
        :type user_obj: Destination.User
        :param destination_obj: Channel which the user asked for permission mask from, or None if privmsg
        :type destination_obj: Destination.Channel | None
        :return: Permission mask matching user input, or None if not found.
        :rtype: PermissionMask.PermissionMask | None
        """
        # If locationInput is a list with more than 2 elements, I don't know how to proceed.
        if len(location_input) > 2:
            raise PermissionControlException("Error, I'm not sure how to interpret that PermissionMask location, "
                                             "you've provided too many filters")
        # If they've specified a server & channel or server & user, parse here
        if len(location_input) == 2:
            # Find server object.
            if self.is_parameter(self.SERVER_NAMES, location_input[0]):
                server_name = location_input[0].split("=")[1]
                location_other = location_input[1]
            elif self.is_parameter(self.SERVER_NAMES, location_input[1]):
                server_name = location_input[1].split("=")[1]
                location_other = location_input[0]
            else:
                raise PermissionControlException("Error, no server name found. If specifying 2 settings, use "
                                                 "\"server=<server> channel=<channel>\" or "
                                                 "\"server=<server> user=<user>\"")
            server_obj = user_obj.server.hallo.get_server_by_name(server_name)
            if server_obj is None:
                raise PermissionControlException("Error, no server exists by that name.")
            # Check if they have specified a channel
            if self.is_parameter(self.CHANNEL_NAMES, location_other):
                # Get channel by that name
                channel_name = location_other.split("=")[1]
                channel_obj = server_obj.get_channel_by_name(channel_name)
                return channel_obj.permission_mask
            # Check if they've specified a user
            if self.is_parameter(self.USER_NAMES, location_other):
                # Get the user by that name
                user_name = location_other.split("=")[1]
                user = server_obj.get_user_by_name(user_name)
                return user.permission_mask
            raise PermissionControlException("Error, input not understood. You specified a server but not channel "
                                             "or user?")
        # # All following have length location_input ==1.
        # Check if they want to set generic hallo permissions
        if location_input[0] in self.HALLO_NAMES:
            return user_obj.server.hallo.permission_mask
        # Check if they have asked for current server
        if location_input[0] in self.SERVER_NAMES:
            return user_obj.server.permission_mask
        # Check if they have specified a server
        if self.is_parameter(self.SERVER_NAMES, location_input[0]):
            server_name = location_input[0].split("=")[1]
            server_obj = user_obj.server.hallo.get_server_by_name(server_name)
            if server_obj is None:
                raise PermissionControlException("Error, no server exists by that name.")
            return server_obj.permission_mask
        # Check if they've asked for current channel
        if location_input[0] in self.CHANNEL_NAMES:
            # Check if this is a channel, and not privmsg.
            if destination_obj is None:
                raise PermissionControlException("Error, you can't set generic channel permissions in a privmsg.")
            return destination_obj.permission_mask
        # Check if they have specified a channel
        if self.is_parameter(self.CHANNEL_NAMES, location_input[0]):
            # Get channel by that name
            channel_name = location_input[0].split("=")[1]
            channel_obj = user_obj.server.get_channel_by_name(channel_name)
            return channel_obj.permission_mask
        # Check if they've specified a user group?
        if self.is_parameter(self.USER_GROUP_NAMES, location_input[0]):
            # See if you can find a UserGroup with that name
            user_group_name = location_input[0].split("=")[1]
            hallo_obj = user_obj.server.hallo
            user_group_obj = hallo_obj.get_user_group_by_name(user_group_name)
            if user_group_obj is None:
                raise PermissionControlException("Error, no user group exists by that name.")
            # get permission mask and output
            return user_group_obj.permission_mask
        # Check if they've specified a user
        if self.is_parameter(self.USER_NAMES, location_input[0]):
            # Get the user by that name
            user_name = location_input[0].split("=")[1]
            user = user_obj.server.get_user_by_name(user_name)
            return user.permission_mask
        # Check if their current channel has any user by the name of whatever else they might have said?
        if destination_obj is not None:
            test_user = user_obj.server.get_user_by_name(location_input[0])
            if not destination_obj.is_user_in_channel(test_user):
                raise PermissionControlException("Error, I can't find that permission mask. Specify which you wish to "
                                                 "modify as user={username}, or similarly for usergroup, channel, "
                                                 "server or hallo.")
            return test_user.permission_mask
        # My normal approaches failed. Generic error message
        raise PermissionControlException("Error, I can't find that permission mask. Specify which you wish to modify "
                                         "as user={username}, or similarly for usergroup, channel, server or hallo.")

    def is_parameter(self, parameter_names, user_input):
        """
        Checks whether a user input string is specifying a parameter in given list
        :param parameter_names: List of possible parameter names
        :type parameter_names: list[str]
        :param user_input: User provided input potentially specifying parameter
        :type user_input: str
        :return: Whether or not it's one of the parameters specified
        :rtype: bool
        """
        return any([user_input.startswith(parameter_name + "=") for parameter_name in parameter_names])
