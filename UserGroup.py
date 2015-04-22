
from xml.dom import minidom

from PermissionMask import PermissionMask

class UserGroup:
    '''
    UserGroup object, mostly exists for a speedy way to appply a PermissionsMask to a large amount of users at once
    '''
    mName = None
    mPermissionMask = None
    mHallo = None
    mUserList = set()

    def __init__(self,hallo,name):
        '''
        Constructor
        '''
        self.mHallo = hallo
        self.mName = name
        self.mPermissionMask = PermissionMask()
    
    def rightsCheck(self,rightName,userObject,channelObject=None):
        'Checks the value of the right with the specified name. Returns boolean'
        rightValue = self.mPermissionMask.getRight(rightName)
        #If PermissionMask contains that right, return it.
        if(rightValue in [True,False]):
            return rightValue
        #Fall back to channel, if defined
        if(channelObject is not None):
            return channelObject.rightsCheck(rightName)
        #Fall back to the parent Server's decision.
        return userObject.getServer().rightsCheck(rightName)
    
    def getName(self):
        return self.mName
    
    def setName(self,newName):
        self.mName = newName
    
    def getPermissionMask(self):
        return self.mPermissionMask
    
    def getHallo(self):
        return self.mHallo
    
    def addUser(self,newUser):
        self.mUserList.add(newUser)
    
    def removeUser(self,removeUser):
        self.mUserList.remove(removeUser)
    
    def toXml(self):
        pass
    
    @staticmethod
    def fromXml(xmlString):
        pass
    
    
    
    
#UserGroup
#-User object stores a list of references to UserGroup objects it belongs to.
#-Has a unique name
#-Is defined at Hallo level
#-stores list of users+servers, but doesn't write that in XML
#-Has a permissionsMask
#-.rightsCheck(rightName,channelObject,serverObject)
#-UserGroups can belong to UserGroups, i.e. God can inherit from Op. They cannot belong to themselves

#if a user is part of multiple groups, then
#rightsCheck()
#return any([group.rightsCheck for group in mUserGroups])