from typing import Optional, TYPE_CHECKING

from hallo.permission_mask import PermissionMask

if TYPE_CHECKING:
    from hallo.hallo import Hallo
    from hallo.destination import Channel, User


class UserGroup:
    """
    UserGroup object, mostly exists for a speedy way to apply a PermissionsMask to a large amount of users at once
    """

    def __init__(self, name: str, hallo: 'Hallo') -> None:
        """
        Constructor
        :param name: Name of the user group
        :param hallo: Hallo object which owns the user group
        """
        self.user_list = set()  # Dynamic userlist of this group
        """:type : set[Destination.User]"""
        self.hallo = hallo  # Hallo instance that owns this UserGroup
        """:type : Hallo.Hallo"""
        self.name = name  # Name of the UserGroup
        """:type : str"""
        self.permission_mask = PermissionMask()  # PermissionMask for the UserGroup
        """:type : PermissionMask"""

    def __eq__(self, other: 'UserGroup') -> bool:
        return (self.hallo, self.name) == (self.hallo, other.name)

    def __hash__(self) -> int:
        return (self.hallo, self.name).__hash__()

    def rights_check(
            self,
            right_name: str,
            user_obj: 'User',
            channel_obj: Optional['Channel'] = None
    ) -> bool:
        """Checks the value of the right with the specified name. Returns boolean
        :param right_name: Name of the right to check
        :param user_obj: User which is having rights checked
        :param channel_obj: Channel in which rights are being checked, None for private messages
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

    def get_name(self) -> str:
        return self.name

    def get_permission_mask(self) -> PermissionMask:
        return self.permission_mask

    def set_permission_mask(self, new_permission_mask: PermissionMask) -> None:
        """
        Sets the permission mask of the user group
        :param new_permission_mask: Permission mask to set for user group
        :type new_permission_mask: PermissionMask.PermissionMask
        """
        self.permission_mask = new_permission_mask

    def get_hallo(self) -> 'Hallo':
        return self.hallo

    def add_user(self, new_user: 'User') -> None:
        """
        Adds a new user to this group
        :param new_user: User to add to group
        :type new_user: destination.User
        """
        self.user_list.add(new_user)

    def remove_user(self, remove_user: 'User') -> None:
        self.user_list.remove(remove_user)

    def to_json(self) -> dict:
        """
        Returns the user group configuration as a dict for serialisation into json
        """
        json_obj: dict = {
            "name": self.name
        }
        if not self.permission_mask.is_empty():
            json_obj["permission_mask"] = self.permission_mask.to_json()
        return json_obj

    @staticmethod
    def from_json(json_obj: dict, hallo: 'Hallo') -> 'UserGroup':
        """
        Creates a UserGroup object from json object dictionary
        :param json_obj: json object dictionary
        :param hallo: root hallo object
        :return: new user group
        """
        new_group = UserGroup(json_obj["name"], hallo)
        if "permission_mask" in json_obj:
            new_group.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        return new_group
