
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
    
    def setRight(self,right,value):
        'Sets the value of the specified right in the rights map'
        if(value == None and right in self.mRightsMap):
            del self.mRightsMap[right]
        self.mRightsMap[right] = value

    def toXml(self):
        'Returns the FunctionMask object XML'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("permission_mask")
        doc.appendChild(root)
        #create rights elements
        for mapRight in self.mRightsMap:
            if(self.mRightsMap[mapRight]==None):
                continue
            rightElement = doc.createElement("right")
            #Add right name
            nameElement = doc.createElement("name")
            nameElement.appendChild(doc.createTextNode(mapRight))
            rightElement.appendChild(nameElement)
            #Add right value
            valueElement = doc.createElement("value")
            valueElement.appendChild(doc.createTextNode(self.mRightsMap[mapRight]))
            rightElement.appendChild(valueElement)
            #Add right element to list
            root.appendChild(rightElement)
        #output XML string
        return doc.toxml()
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new Destination object from XML'
        raise NotImplementedError