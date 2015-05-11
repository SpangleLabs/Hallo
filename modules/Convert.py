from xml.dom import minidom

class ConvertRepo:
    '''
    Configuration repository. Stores list of ConvertTypes, ConvertPrefixGroups, etc
    '''
    mTypeList = []

    def __init__(self):
        '''
        Constructor
        '''
        raise NotImplementedError
    
    def getTypeList(self):
        'Returns the full list of ConvertType objects'
        raise NotImplementedError

    def findTypes(self,name1,name2):
        'Finds out what types are valid for a pair of names.'
        raise NotImplementedError
    
    @staticmethod
    def loadFromXml(self):
        'Loads Convert Repo from XML.'
        raise NotImplementedError
    
    def saveToXml(self):
        'Saves Convert Repo to XML.'
        raise NotImplementedError
    
class ConvertType:
    '''
    Conversion unit type object.
    '''
    mName = None
    mUnitList = []
    
    def __init__(self,name):
        raise NotImplementedError
    
    def getName(self):
        'Returns the name of the ConvertType object'
        raise NotImplementedError
    
    def setName(self,name):
        'Change the name of the ConvertType object'
        raise NotImplementedError
    
    def getUnitList(self):
        'Returns the full list of ConvertUnit objects'
        raise NotImplementedError
    
    def getUnitByName(self,name):
        'Get a unit by a specified name'
        raise NotImplementedError

    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertType object from XML'
        raise NotImplementedError
    
    def toXml(self):
        'Writes ConvertType object as XML'
        raise NotImplementedError

class ConvertUnit:
    '''
    Conversion unit object.
    '''
    mNameList = []
    mAbbreviationList = []
    mValidPrefixGroup = None
    mValue = None
    mType = None
    mOffset = None
    mLastUpdated = None
    
    def __init__(self,convertType,names,value):
        raise NotImplementedError
    
    def getNames(self):
        'Returns the full list of names for a unit.'
        raise NotImplementedError
    
    def removeName(self,name):
        'Removes a name from the list of names for a unit.'
        raise NotImplementedError
    
    def addName(self,name):
        'Adds a name to the list of names for a unit.'
        raise NotImplementedError
    
    def getAbbreviations(self):
        'Returns the full list of abbreviations for a unit.'
        raise NotImplementedError
    
    def removeAbbreviation(self,abbreviation):
        'Removes an abbreviation from the list of abbreviations for a unit.'
        raise NotImplementedError
    
    def addAbbreviation(self,abbreviation):
        'Adds an abbreviation to the list of abbreviations for a unit.'
        raise NotImplementedError
    
    def getPrefixGroup(self):
        'Returns the value of the unit.'
        raise NotImplementedError
    
    def setPrefixGroup(self,prefixGroup):
        'Changes the value of the unit.'
        raise NotImplementedError
    
    def getValue(self):
        'Returns the value of the unit.'
        raise NotImplementedError
    
    def setValue(self,value):
        'Changes the value of the unit.'
        raise NotImplementedError
    
    def getOffset(self):
        'Returns the offset of the unit.'
        raise NotImplementedError
    
    def setOffset(self,offset):
        'Changes the offset of the unit.'
        raise NotImplementedError
    
    def getLastUpdated(self):
        'Returns the last updated time of the unit.'
        raise NotImplementedError
    
    def getType(self):
        'Returns the ConvertType which "owns" this ConvertUnit.'
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertUnit object from XML.'
        raise NotImplementedError
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("unit")
        doc.appendChild(root)
        #Add name elements
        for nameStr in self.mNameList:
            nameElement = doc.createElement("name")
            nameElement.appendChild(doc.createTextNode(nameStr))
            root.appendChild(nameElement)
        #Add abbreviations
        for abbrStr in self.mAbbreviationList:
            abbrElement = doc.createElement("abbr")
            abbrElement.appendChild(doc.createTextNode(abbrStr))
            root.appendChild(abbrElement)
        #Add prefix group
        if(self.mValidPrefixGroup is not None):
            validPrefixGroupName = self.mValidPrefixGroup.getName()
            validPrefixGroupElement = doc.createElement("valid_prefix_group")
            validPrefixGroupElement.appendChild(doc.createTextNode(validPrefixGroupName))
            root.appendChild(validPrefixGroupElement)
        #Add value element
        valueElement = doc.createElement("value")
        valueElement.appendChild(doc.createTextNode(str(self.mValue)))
        root.appendChild(valueElement)
        #Add offset
        if(self.mOffset is not None):
            offsetElement = doc.createElement("offset")
            offsetElement.appendChild(doc.createTextNode(str(self.mOffset)))
            root.appendChild(offsetElement)
        #Add update time
        if(self.mLastUpdated is not None):
            lastUpdateElement = doc.createElement("last_update")
            lastUpdateElement.appendChild(doc.createTextNode(str(self.mLastUpdated)))
            root.appendChild(lastUpdateElement)
        #Output XML
        return doc.toxml()
    
class ConvertPrefixGroup:
    '''
    Group of Conversion Prefixes.
    '''
    mName = None
    mPrefixList = []
    
    def __init__(self,name):
        raise NotImplementedError
    
    def getName(self):
        return self.mName
    
    def getPrefixList(self):
        return self.mPrefixList
    
    def getPrefixByName(self):
        raise NotImplementedError
    
    def addPrefix(self,prefix):
        'Adds a new prefix to the prefix list'
        self.mPrefixList.append(prefix)
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertUnit object from XML.'
        #Load document
        doc = minidom.parse(xmlString)
        #Get name and create object
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newPrefixGroup = ConvertPrefixGroup(newName)
        #Loop through prefix elements, creating and adding objects.
        for prefixXml in doc.getElementsByTagName("prefix"):
            prefixObject = ConvertPrefix.fromXml(prefixXml.toxml())
            newPrefixGroup.addPrefix(prefixObject)
        #Return created PrefixGroup
        return newPrefixGroup
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("prefix_group")
        doc.appendChild(root)
        #Add name element
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        #Add prefixes
        for prefixObject in self.mPrefixList:
            prefixElement = minidom.parse(prefixObject.toXml()).firstChild
            root.appendChild(prefixElement)
        #Output XML
        return doc.toxml()

class ConvertPrefix:
    '''
    Conversion prefix.
    '''
    mPrefix = None
    mAbbreviation = None
    mMultiplier = None
    
    def __init__(self,prefix,abbreviation,multiplier):
        raise NotImplementedError
    
    def getPrefix(self):
        'Returns the name of the prefix'
        raise NotImplementedError
    
    def getAbbreviation(self):
        'Returns the abbreviation for the prefix'
        raise NotImplementedError
    
    def getMultiplier(self):
        'Returns the multiplier the prefix has'
        raise NotImplementedError
    
    @staticmethod
    def fromXml(xmlString):
        'Loads a new ConvertUnit object from XML.'
        doc = minidom.parse(xmlString)
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newAbbreviation = doc.getElementsByTagName("abbr")[0].firstChild.data
        newValue = doc.getElementsByTagName("value")[0].firstChild.data
        newPrefix = ConvertPrefix(newName,newAbbreviation,newValue)
        return newPrefix
    
    def toXml(self):
        'Outputs a ConvertUnit object as XML.'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("prefix")
        doc.appendChild(root)
        #Add name
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mPrefix))
        root.appendChild(nameElement)
        #Add abbreviation
        abbrElement = doc.createElement("abbr")
        abbrElement.appendChild(doc.createTextNode(self.mAbbreviation))
        root.appendChild(abbrElement)
        #Add multiplier
        valueElement = doc.createElement("value")
        valueElement.appendChild(doc.createTextNode(str(self.mMultiplier)))
        root.appendChild(valueElement)
        #Return XML
        return doc.toxml()
    
class ConvertMeasure:
    '''
    Convert meaure object. An amount with a unit.
    '''
    mAmount = None
    mUnit = None
    
    def __init__(self,amount,unit):
        raise NotImplementedError
    
    def getUnit(self):
        'Returns the unit of the measure.'
        raise NotImplementedError
    
    def getAmount(self):
        'Returns the amount of the measure.'
        raise NotImplementedError
    
    def convertTo(self,unit):
        'Creates a new measure, equal in value but with a different unit.'
        raise NotImplementedError
        








