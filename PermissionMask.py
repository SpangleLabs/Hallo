
from xml.dom import minidom

class PermissionMask(object):
    '''
    Permission mask object, stores which rights are enabled or disabled by level
    '''
    mRightsMap = {}
    
    def getRight(self,right):
        'Gets the value of the specified right in the rights map'
        if(right in self.mRightsMap):
            return self.mRightsMap[right]
        return None
        
    def toXml(self):
        'Returns the Destination object XML'
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new Destination object from XML'
        raise NotImplementedError