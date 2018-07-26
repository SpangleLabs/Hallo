from xml.dom import minidom

from PermissionMask import PermissionMask


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
        :type hallo: Hallo.Hallo
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
        :type user_obj: Destination.User
        :param channel_obj: Channel in which rights are being checked, None for private messages
        :type channel_obj: Destination.Channel | None
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
        :type new_user: Destination.User
        """
        self.user_list.add(new_user)

    def remove_user(self, remove_user):
        self.user_list.remove(remove_user)

    def to_xml(self):
        """Returns the UserGroup object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("user_group")
        doc.appendChild(root)
        # create name element
        name_elem = doc.createElement("name")
        name_elem.appendChild(doc.createTextNode(self.name))
        root.appendChild(name_elem)
        # create permission_mask element
        if not self.permission_mask.is_empty():
            permission_mask_elem = minidom.parseString(self.permission_mask.to_xml()).firstChild
            root.appendChild(permission_mask_elem)
        # output XML string
        return doc.toxml()

    @staticmethod
    def from_xml(xml_string, hallo):
        """
        Loads a new UserGroup object from XML
        :param xml_string: String containing XML to parse for usergroup
        :type xml_string: str
        :param hallo: Hallo object to add user group to
        :type hallo: Hallo.Hallo
        """
        doc = minidom.parseString(xml_string)
        new_name = doc.getElementsByTagName("name")[0].firstChild.data
        new_user_group = UserGroup(new_name, hallo)
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            new_user_group.permission_mask = PermissionMask.from_xml(
                doc.getElementsByTagName("permission_mask")[0].toxml())
        return new_user_group
