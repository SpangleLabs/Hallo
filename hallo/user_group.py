from hallo.permission_mask import PermissionMask


class UserGroup:
    """
    UserGroup object, mostly exists for a speedy way to apply a PermissionsMask to a large amount of users at once
    """

    def __init__(self, name, hallo):
        """
        Constructor
        :param name: Name of the user group
        :type name: str
        :param hallo: Hallo object which owns the user group
        :type hallo: hallo.Hallo
        """
        self.user_list = set()  # Dynamic userlist of this group
        """:type : set[Destination.User]"""
        self.hallo = hallo  # Hallo instance that owns this UserGroup
        """:type : Hallo.Hallo"""
        self.name = name  # Name of the UserGroup
        """:type : str"""
        self.permission_mask = PermissionMask()  # PermissionMask for the UserGroup
        """:type : PermissionMask"""

    def __eq__(self, other):
        return (self.hallo, self.name) == (self.hallo, other.name)

    def __hash__(self):
        return (self.hallo, self.name).__hash__()

    def rights_check(self, right_name, user_obj, channel_obj=None):
        """Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the right to check
        :type right_name: str
        :param user_obj: User which is having rights checked
        :type user_obj: destination.User
        :param channel_obj: Channel in which rights are being checked, None for private messages
        :type channel_obj: destination.Channel | None
        :rtype: bool
        """
        right_value = self.permission_mask.get_right(right_name)
        # PermissionMask contains that right, return it.
        if right_value in [True, False]:
            return right_value
        # Fall back to channel, if defined
        if channel_obj is not None:
            return channel_obj.rights_check(right_name)
        # Fall back to the parent Server's decision.
        return user_obj.server.rights_check(right_name)

    def get_name(self):
        return self.name

    def get_permission_mask(self):
        return self.permission_mask

    def set_permission_mask(self, new_permission_mask):
        """
        Sets the permission mask of the user group
        :param new_permission_mask: Permission mask to set for user group
        :type new_permission_mask: PermissionMask.PermissionMask
        """
        self.permission_mask = new_permission_mask

    def get_hallo(self):
        return self.hallo

    def add_user(self, new_user):
        """
        Adds a new user to this group
        :param new_user: User to add to group
        :type new_user: destination.User
        """
        self.user_list.add(new_user)

    def remove_user(self, remove_user):
        self.user_list.remove(remove_user)

    def to_json(self):
        """
        Returns the user group configuration as a dict for serialisation into json
        :return: dict
        """
        json_obj = dict()
        json_obj["name"] = self.name
        if not self.permission_mask.is_empty():
            json_obj["permission_mask"] = self.permission_mask.to_json()
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        """
        Creates a UserGroup object from json object dictionary
        :param json_obj: json object dictionary
        :type json_obj: dict
        :param hallo: root hallo object
        :type hallo: hallo.Hallo
        :return: new user group
        :rtype: UserGroup
        """
        new_group = UserGroup(json_obj["name"], hallo)
        if "permission_mask" in json_obj:
            new_group.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        return new_group
