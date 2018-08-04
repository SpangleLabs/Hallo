

class PermissionMask(object):
    """
    Permission mask object, stores which rights are enabled or disabled by level
    """
    rights_map = None

    def __init__(self):
        self.rights_map = {}

    def get_right(self, right):
        """
        Gets the value of the specified right in the rights map
        :param right: Name of the right to be searching for
        """
        if right in self.rights_map:
            return self.rights_map[right]
        return None

    def set_right(self, right, value):
        """Sets the value of the specified right in the rights map
        :param right: Name of the right to set
        :param value: Value to set the right to
        """
        if value is None and right in self.rights_map:
            del self.rights_map[right]
        try:
            value = value.lower()
        except AttributeError:
            pass
        if value == 'true' or value == '1' or value == 1:
            value = True
        if value == 'false' or value == '0' or value == 0:
            value = False
        if value in [True, False]:
            self.rights_map[right] = value

    def is_empty(self):
        """Returns a boolean representing whether the PermissionMask is "empty" or has no rights set."""
        return len(self.rights_map) == 0

    def to_json(self):
        """
        Returns the PermissionMask configuration as an object for serialisation into json
        :return: dict
        """
        json_obj = {}
        for map_right in self.rights_map:
            if self.rights_map[map_right] is None:
                continue
            json_obj[map_right] = self.rights_map[map_right]
        return json_obj

    @staticmethod
    def from_json(json_obj):
        new_mask = PermissionMask()
        for map_right in json_obj:
            new_mask.set_right(map_right, json_obj[map_right])
        return new_mask
