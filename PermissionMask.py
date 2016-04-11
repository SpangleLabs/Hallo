from xml.dom import minidom
from inc.Commons import Commons


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

    def to_xml(self):
        """Returns the FunctionMask object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("permission_mask")
        doc.appendChild(root)
        # Add rights list element
        right_list_elem = doc.createElement("right_list")
        # create rights elements
        for map_right in self.rights_map:
            if self.rights_map[map_right] is None:
                continue
            right_elem = doc.createElement("right")
            # Add right name
            name_elem = doc.createElement("name")
            name_elem.appendChild(doc.createTextNode(map_right))
            right_elem.appendChild(name_elem)
            # Add right value
            value_elem = doc.createElement("value")
            value_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.rights_map[map_right]]))
            right_elem.appendChild(value_elem)
            # Add right element to list
            right_list_elem.appendChild(right_elem)
        root.appendChild(right_list_elem)
        # output XML string
        return doc.toxml()

    @staticmethod
    def from_xml(xml_string):
        """
        Loads a new Destination object from XML
        :param xml_string: XML string to parse to create new PermissionMask
        """
        doc = minidom.parseString(xml_string)
        new_mask = PermissionMask()
        # Load rights
        rights_list_elem = doc.getElementsByTagName("right_list")[0]
        for right_elem in rights_list_elem.getElementsByTagName("right"):
            right_name = right_elem.getElementsByTagName("name")[0].firstChild.data
            right_value = Commons.string_from_file(right_elem.getElementsByTagName("value")[0].firstChild.data)
            new_mask.set_right(right_name, right_value)
        return new_mask
