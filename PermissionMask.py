
from xml.dom import minidom

class PermissionMask(object):
    '''
    Permission mask object, stores which rights are enabled or disabled by level
    '''
    mRightsMap = None
    
    def __init__(self):
        self.mRightsMap = {}
    
    def getRight(self,right):
        'Gets the value of the specified right in the rights map'
        if(right in self.mRightsMap):
            return self.mRightsMap[right]
        return None
    
    def setRight(self,right,value):
        'Sets the value of the specified right in the rights map'
        if(value == None and right in self.mRightsMap):
            del self.mRightsMap[right]
        try:
            value = value.lower()
        except AttributeError:
            pass
        if(value=='true' or value=='1' or value==1):
            value = True
        if(value=='false' or value=='0' or value==0):
            value = False
        if(value in [True,False]):
            self.mRightsMap[right] = value
    
    def isEmpty(self):
        'Returns a boolean representing whether the PermissionMask is "empty" or has no rights set.'
        return len(self.mRightsMap)==0

    def toXml(self):
        'Returns the FunctionMask object XML'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("permission_mask")
        doc.appendChild(root)
        #Add rights list element
        rightListElement = doc.createElement("right_list")
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
            rightListElement.appendChild(rightElement)
        root.appendChild(rightListElement)
        #output XML string
        return doc.toxml()
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new Destination object from XML'
        doc = minidom.parse(xmlString)
        newMask = PermissionMask()
        #Load rights
        rightsListXml = doc.getElementsByTagName("right_list")
        for rightXml in rightsListXml.getElementsByTagName("right"):
            rightName = rightXml.getElementsByTagName("name")[0].firstChild.data
            rightValue = rightXml.getElementsByTagName("value")[0].firstChild.data
            newMask.setRight(rightName,rightValue)
        return newMask

