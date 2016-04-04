from xml.dom import minidom

from PermissionMask import PermissionMask


class UserGroup:
    """
    UserGroup object, mostly exists for a speedy way to apply a PermissionsMask to a large amount of users at once
    """
    mName = None  # Name of the UserGroup
    mPermissionMask = None  # PermissionMask for the UserGroup
    mHallo = None  # Hallo instance that owns this UserGroup
    mUserList = None  # Dynamic userlist of this group

    def __init__(self, name, hallo):
        """
        Constructor
        """
        self.mUserList = set()
        self.mHallo = hallo
        self.mName = name
        self.mPermissionMask = PermissionMask()

    def rightsCheck(self, rightName, userObject, channelObject=None):
        """Checks the value of the right with the specified name. Returns boolean
        :param rightName: Name of the right to check
        :param userObject: User which is having rights checked
        :param channelObject: Channel in which rights are being checked, None for private messages
        """
        rightValue = self.mPermissionMask.get_right(rightName)
        # PermissionMask contains that right, return it.
        if rightValue in [True, False]:
            return rightValue
        # Fall back to channel, if defined
        if channelObject is not None:
            return channelObject.rights_check(rightName)
        # Fall back to the parent Server's decision.
        return userObject.getServer().rights_check(rightName)

    def getName(self):
        return self.mName

    def getPermissionMask(self):
        return self.mPermissionMask

    def setPermissionMask(self, newPermissionMask):
        self.mPermissionMask = newPermissionMask

    def getHallo(self):
        return self.mHallo

    def addUser(self, newUser):
        self.mUserList.add(newUser)

    def removeUser(self, removeUser):
        self.mUserList.remove(removeUser)

    def toXml(self):
        """Returns the UserGroup object XML"""
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("user_group")
        doc.appendChild(root)
        # create name element
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        # create permission_mask element
        if not self.mPermissionMask.is_empty():
            permissionMaskElement = minidom.parseString(self.mPermissionMask.to_xml()).firstChild
            root.appendChild(permissionMaskElement)
        # output XML string
        return doc.toxml()

    @staticmethod
    def fromXml(xmlString, hallo):
        """
        Loads a new UserGroup object from XML
        :param xmlString: String containing XML to parse for usergroup
        :param hallo: Hallo object to add user group to
        """
        doc = minidom.parseString(xmlString)
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newUserGroup = UserGroup(newName, hallo)
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            newUserGroup.mPermissionMask = PermissionMask.from_xml(
                doc.getElementsByTagName("permission_mask")[0].toxml())
        return newUserGroup
