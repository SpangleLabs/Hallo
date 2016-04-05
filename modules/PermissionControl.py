from Function import Function
from inc.commons import Commons


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
        location_input = line_split[:-3]
        # Search for the permission_mask they want.
        try:
            permission_mask = self.find_permission_mask(location_input, user_obj, destination_obj)
        # If it comes back with an error message, return that error
        except Exception as e:
            return str(e)
        # If it comes back unspecified, generic error message
        if permission_mask is None:
            return "I can't find that permission mask. Specify which you wish to modify as user={username}, " \
                   "or similarly for usergroup, channel, server or hallo."
        # Turn bool_input into a boolean
        bool_bool = Commons.string_to_bool(bool_input)
        # Check if boolean input is valid
        if bool_bool is None:
            return "I don't understand your boolean value. Please use true or false."
        # Set the right
        permission_mask.setRight(right_input, bool_bool)
        pass

    def find_permission_mask(self, location_input, user_obj, destination_obj):
        # If locationInput is a list with more than 2 elements, I don't know how to proceed.
        if len(location_input) > 2:
            raise Exception("I'm not sure how to interpret that PermissionMask location")
        # If they've specified a server & channel or server & user, parse here
        if len(location_input) == 2:
            # Find server object.
            if any([location_input[0].startswith(serverStr + "=") for serverStr in self.SERVER_NAMES]):
                server_name = location_input[0].split("=")[1]
                location_other = location_input[1]
            elif any([location_input[1].startswith(serverStr + "=") for serverStr in self.SERVER_NAMES]):
                server_name = location_input[1].split("=")[1]
                location_other = location_input[0]
            else:
                raise Exception("No server name found.")
            server_obj = user_obj.get_server().get_hallo().get_server_by_name(server_name)
            if server_obj is None:
                raise Exception("No server exists by that name.")
            # Check if they have specified a channel
            if any([location_other.startswith(channelStr + "=") for channelStr in self.CHANNEL_NAMES]):
                # Get channel by that name
                channel_name = location_other.split("=")[1]
                channel_obj = user_obj.get_server().get_channel_by_name(channel_name)
                permission_mask = channel_obj.get_permission_mask()
                return permission_mask
            # Check if they've specified a user
            if any([location_other.startswith(userStr + "=") for userStr in self.USER_NAMES]):
                # Get the user by that name
                user_name = location_other.split("=")[1]
                user_obj.get_server().get_user_by_name(user_name)
                permission_mask = user_obj.get_permission_mask()
                return permission_mask
            raise Exception("Input not understood. You specified a server but not channel or user?")
        # # All following have length locationInput ==1.
        # Check if they want to set generic hallo permissions
        if location_input[0] in self.HALLO_NAMES:
            permission_mask = user_obj.get_server().get_hallo().get_permission_mask()
            return permission_mask
        # Check if they have asked for current server
        if location_input[0] in self.SERVER_NAMES:
            permission_mask = user_obj.get_server().get_permission_mask()
            return permission_mask
        # Check if they have specified a server
        if any([location_input[0].startswith(serverStr + "=") for serverStr in self.SERVER_NAMES]):
            server_name = location_input[0].split("=")[1]
            server_obj = user_obj.get_server().get_hallo().get_server_by_name(server_name)
            if server_obj is None:
                raise Exception("No server exists by that name.")
            permission_mask = server_obj.get_permission_mask()
            return permission_mask
        # Check if they've asked for current channel
        if location_input[0] in self.CHANNEL_NAMES:
            # Check if this is a channel, and not privmsg.
            if destination_obj is None or destination_obj == user_obj:
                raise Exception("You can't set generic channel permissions in a privmsg.")
            permission_mask = destination_obj.get_permission_mask()
            return permission_mask
        # Check if they have specified a channel
        if any([location_input[0].startswith(channelStr + "=") for channelStr in self.CHANNEL_NAMES]):
            # Get channel by that name
            channel_name = location_input[0].split("=")[1]
            channel_obj = user_obj.get_server().get_channel_by_name(channel_name)
            permission_mask = channel_obj.get_permission_mask()
            return permission_mask
        # Check if they've specified a user group?
        if any([location_input[0].startswith(userGroupStr + "=") for userGroupStr in self.USER_GROUP_NAMES]):
            # See if you can find a UserGroup with that name
            user_group_name = location_input[0].split("=")[1]
            hallo_obj = user_obj.get_server().get_hallo()
            user_group_obj = hallo_obj.get_user_group_by_name(user_group_name)
            if user_group_obj is None:
                raise Exception("No user group exists by that name.")
            # get permission mask and output
            permission_mask = user_group_obj.get_permission_mask()
            return permission_mask
        # Check if they've specified a user
        if any([location_input[0].startswith(userStr + "=") for userStr in self.USER_NAMES]):
            # Get the user by that name
            user_name = location_input[0].split("=")[1]
            user_obj.get_server().get_user_by_name(user_name)
            permission_mask = user_obj.get_permission_mask()
            return permission_mask
        # Check if their current channel has any user by the name of whatever else they might have said?
        if destination_obj is None or destination_obj == user_obj:
            user_list = destination_obj.get_user_list()
            user_list_matching = [userObject for userObject in user_list if userObject.get_name() == location_input[0]]
            if len(user_list_matching) == 0:
                raise Exception("I do not understand your input. I cannot find that Permission Mask.")
            user_obj = user_list_matching[0]
            permission_mask = user_obj.get_permission_mask()
            return permission_mask
        # My normal approaches failed. Generic error message
        return None
