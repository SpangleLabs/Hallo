from xml.dom import minidom

class ConvertRepo:
    '''
    Configuration repository. Stores list of ConvertTypes, ConvertPrefixGroups, etc
    '''
    mTypeList = []
    mPrefixGroupList = []

    def __init__(self):
        '''
        Constructor
        '''
        #Nothing needs doing
        pass
    
    def getTypeList(self):
        'Returns the full list of ConvertType objects'
        return self.mTypeList
    
    def addType(self,newType):
        'Adds a new ConvertType object to the type list'
        self.mTypeList.append(newType)
    
    def removeType(self,delType):
        'Removes a ConvertType object from the type list'
        if(delType in self.mTypeList):
            self.mTypeList.remove(delType)
    
    def getTypeByName(self,name):
        'Gets a ConvertType object with the matching name.'
        for typeObject in self.mTypeList:
            if(typeObject.getName()==name):
                return typeObject
        for typeObject in self.mTypeList:
            if(typeObject.getName().lower()==name.lower()):
                return typeObject
        return None
    
    def getPrefixGroupList(self):
        'Returns the full list of ConvertPrefixGroup objects'
        return self.mPrefixGroupList
    
    def addPrefixGroup(self,prefixGroup):
        'Adds a new ConvertPrefixGroup object to the prefix group list'
        self.mPrefixGroupList.append(prefixGroup)
    
    def removePrefixGroup(self,prefixGroup):
        'Removes a ConvertPrefixGroup object from the prefix group list'
        if(prefixGroup in self.mPrefixGroupList):
            self.mPrefixGroupList.remove(prefixGroup)
    
    def getPrefixGroupByName(self,name):
        'Gets a ConvertPrefixGroup object with the matching name.'
        for prefixGroupObject in self.mPrefixGroupList:
            if(prefixGroupObject.getName().lower()==name.lower()):
                return prefixGroupObject
        return None

    def findTypes(self,name1,name2):
        'Finds out what types are valid for a pair of names.'
        raise NotImplementedError
    
    @staticmethod
    def loadFromXml(self):
        'Loads Convert Repo from XML.'
        doc = minidom.parse("store/convert.xml")
        #Create new object
        newRepo = ConvertRepo()
        #Loop through prefix groups
        for prefixGroupXml in doc.getElementsByTagName("prefix_group"):
            prefixGroupObject = ConvertPrefixGroup.fromXml(newRepo,prefixGroupXml.toxml())
            newRepo.addPrefixGroup(prefixGroupObject)
        #Loop through types
        for typeXml in doc.getElementsByTagName("type"):
            typeObject = ConvertType.fromXml(newRepo,typeXml.toxml())
            newRepo.addType(typeObject)
        #Return new repo object
        return newRepo
    
    def saveToXml(self):
        'Saves Convert Repo to XML.'
        #Create document, with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='convert',
            publicId='', 
            systemId='convert.dtd',
        )
        doc = docimp.createDocument(None,'convert',doctype)
        #get root element
        root = doc.getElementsByTagName("convert")[0]
        #Add prefix groups
        for prefixGroupObject in self.mPrefixGroupList:
            prefixGroupElement = minidom.parse(prefixGroupObject.toXml()).firstChild
            root.appendChild(prefixGroupElement)
        #Add types
        for typeObject in self.mTypeList:
            typeElement = minidom.parse(typeObject.toXml()).firstChild
            root.appendChild(typeElement)
        #save XML
        doc.writexml(open("store/convert.xml","w"),addindent="\t",newl="\n")
    
class ConvertType:
    '''
    Conversion unit type object.
    '''
    mRepo = None
    mName = None
    mDecimals = 2
    mBaseUnit = None
    mUnitList = []
    
    def __init__(self,repo,name):
        self.mRepo = repo
        self.mName = name
    
    def getRepo(self):
        'Returns the ConvertRepo which owns this ConvertType object'
        return self.mRepo
    
    def getName(self):
        'Returns the name of the ConvertType object'
        return self.mName
    
    def setName(self,name):
        'Change the name of the ConvertType object'
        self.mName = name
    
    def getDecimals(self):
        'Returns the number of decimals of the ConvertType object'
        return self.mDecimals
    
    def setDecimals(self,decimals):
        'Change the number of decimals of the ConvertType object'
        self.mDecimals = decimals
    
    def getBaseUnit(self):
        'Returns the base unit object of the ConvertType object'
        return self.mBaseUnit
    
    def setBaseUnit(self,baseUnit):
        'Change the base unit object of the ConvertType object'
        self.mBaseUnit = baseUnit
    
    def getUnitList(self):
        'Returns the full list of ConvertUnit objects'
        return self.mUnitList
    
    def addUnit(self,unit):
        'Adds a new ConvertUnit object to unit list'
        self.mUnitList.append(unit)
        
    def removeUnit(self,unit):
        'Removes a ConvertUnit object to unit list'
        if(unit in self.mUnitList):
            self.mUnitList.remove(unit)
    
    def getUnitByName(self,name):
        'Get a unit by a specified name'
        for unitObject in self.mUnitList:
            if(unitObject.getName()==name):
                return unitObject
        for unitObject in self.mUnitList:
            if(unitObject.getName().lower()==name.lower()):
                return unitObject
        return None

    @staticmethod
    def fromXml(repo,xmlString):
        'Loads a new ConvertType object from XML'
        #Load document
        doc = minidom.parse(xmlString)
        #Get name and create ConvertType object
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newType = ConvertPrefixGroup(repo,newName)
        #Get number of decimals
        newDecimals = int(doc.getElementsByTagName("decimals")[0].firstChild.data)
        newType.setDecimals(newDecimals)
        #Get base unit
        baseUnitXml = doc.getElementsByTagName("base_unit")[0].getElementsByTagName("unit")[0]
        baseUnitObject = ConvertUnit.fromXml(newType,baseUnitXml.toxml())
        newType.setBaseUnit(baseUnitObject)
        #Loop through unit elements, creating and adding objects.
        for unitXml in doc.getElementsByTagName("unit"):
            unitObject = ConvertUnit.fromXml(self,unitXml.toxml())
            newType.addUnit(unitObject)
        #Return created PrefixGroup
        return newType
    
    def toXml(self):
        'Writes ConvertType object as XML'
        #create document
        doc = minidom.Document()
        #create root element
        root = doc.createElement("type")
        doc.appendChild(root)
        #Add name element
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(self.mName))
        root.appendChild(nameElement)
        #Add decimals element
        nameElement = doc.createElement("decimals")
        nameElement.appendChild(doc.createTextNode(str(self.mDecimals)))
        root.appendChild(nameElement)
        #Add base unit element
        baseUnitElement = doc.createElement("base_unit")
        baseUnitUnitElement = minidom.parse(self.mBaseUnit.toXml()).firstChild
        baseUnitElement.appendChild(baseUnitUnitElement)
        root.appendChild(baseUnitElement)
        #Add units
        for unitObject in self.mUnitList:
            unitElement = minidom.parse(unitObject.toXml()).firstChild
            root.appendChild(unitElement)
        #Output XML
        return doc.toxml()

class ConvertUnit:
    '''
    Conversion unit object.
    '''
    mType = None
    mNameList = []
    mAbbreviationList = []
    mValidPrefixGroup = None
    mValue = None
    mOffset = None
    mLastUpdated = None
    
    def __init__(self,convertType,names,value):
        self.mType = convertType
        self.mNameList = names
        self.mValue = value
    
    def getType(self):
        'Returns the ConvertType which "owns" this ConvertUnit.'
        return self.mType
    
    def getNameList(self):
        'Returns the full list of names for a unit.'
        return self.mNameList
    
    def addName(self,name):
        'Adds a name to the list of names for a unit.'
        self.mNameList.append(name)
    
    def removeName(self,name):
        'Removes a name from the list of names for a unit.'
        if(name in self.mNameList):
            self.mNameList.remove(name)
    
    def getAbbreviationList(self):
        'Returns the full list of abbreviations for a unit.'
        return self.mAbbreviationList
    
    def addAbbreviation(self,abbreviation):
        'Adds an abbreviation to the list of abbreviations for a unit.'
        self.mAbbreviationList.append(abbreviation)
    
    def removeAbbreviation(self,abbreviation):
        'Removes an abbreviation from the list of abbreviations for a unit.'
        if(abbreviation in self.mAbbreviationList):
            self.mAbbreviationList.remove(abbreviation)
    
    def getPrefixGroup(self):
        'Returns the value of the unit.'
        return self.mValidPrefixGroup
    
    def setPrefixGroup(self,prefixGroup):
        'Changes the value of the unit.'
        self.mValidPrefixGroup = prefixGroup
    
    def getValue(self):
        'Returns the value of the unit.'
        return self.mValue
    
    def setValue(self,value):
        'Changes the value of the unit.'
        self.mValue = value
    
    def getOffset(self):
        'Returns the offset of the unit.'
        return self.mOffset
    
    def setOffset(self,offset):
        'Changes the offset of the unit.'
        self.mOffset = offset
    
    def getLastUpdated(self):
        'Returns the last updated time of the unit.'
        return self.mLastUpdated
    
    def setLastUpdated(self,updateTime):
        'Changes the last updated time of the unit.'
        self.mLastUpdated = updateTime
    
    @staticmethod
    def fromXml(convertType,xmlString):
        'Loads a new ConvertUnit object from XML.'
        #Load document
        doc = minidom.parse(xmlString)
        #Get names, value and create object
        newNameList = []
        for nameXml in doc.getElementsByTagName("name"):
            newName = nameXml.firstChild.data
            newNameList.append(newName)
        newValue = float(doc.getElementsByTagName("value")[0].firstChild.data)
        newUnit = ConvertUnit(convertType,newNameList,newValue)
        #Loop through abbreviation elements, adding them.
        for abbrXml in doc.getElementsByTagName("abbr"):
            newAbbr = abbrXml.firstChild.data
            newUnit.addAbbreviation(newAbbr)
        #Add prefix group
        if(len(doc.getElementsByTagName("valid_prefix_group"))!=0):
            convertRepo = convertType.getRepo()
            validPrefixGroupName = doc.getElementsByTagName("valid_prefix_group")[0].firstChild.data
            validPrefixGroup = convertRepo.getPrefixGroupByName(validPrefixGroupName)
            newUnit.setPrefixGroup(validPrefixGroup)
        #Get offset
        if(len(doc.getElementsByTagName("offset"))!=0):
            newOffset = doc.getElementsByTagName("offset")
            newUnit.setOffset(newOffset)
        #Get update time
        if(len(doc.getElementsByTagName("last_update"))!=0):
            newLastUpdated = doc.getElementsByTagName("last_update")[0].firstChild.data
            newUnit.setLastUpdated(newLastUpdated)
        #Return created ConvertUnit
        return newUnit
    
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
    mRepo = None
    mName = None
    mPrefixList = []
    
    def __init__(self,repo,name):
        self.mRepo = repo
        self.mName = name
    
    def getRepo(self):
        'Returns the ConvertRepo owning this prefix group'
        return self.mRepo
    
    def getName(self):
        'Returns the prefix group name'
        return self.mName
    
    def setName(self,name):
        'Sets the prefix group name'
        self.mName = name
    
    def getPrefixList(self):
        'Returns the full list of prefixes in the group'
        return self.mPrefixList
    
    def addPrefix(self,prefix):
        'Adds a new prefix to the prefix list'
        self.mPrefixList.append(prefix)
        
    def removePrefix(self,prefix):
        'Removes a prefix from the prefix list'
        if(prefix in self.mPrefixList):
            self.mPrefixList.remove(prefix)
    
    def getPrefixByName(self):
        'Gets the prefix with the specified name or abbreviation'
        raise NotImplementedError
    
    @staticmethod
    def fromXml(repo,xmlString):
        'Loads a new ConvertUnit object from XML.'
        #Load document
        doc = minidom.parse(xmlString)
        #Get name and create object
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newPrefixGroup = ConvertPrefixGroup(repo,newName)
        #Loop through prefix elements, creating and adding objects.
        for prefixXml in doc.getElementsByTagName("prefix"):
            prefixObject = ConvertPrefix.fromXml(self,prefixXml.toxml())
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
    mPrefixGroup = None
    mPrefix = None
    mAbbreviation = None
    mMultiplier = None
    
    def __init__(self,prefixGroup,prefix,abbreviation,multiplier):
        self.mPrefixGroup = prefixGroup
        self.mPrefix = prefix
        self.mAbbreviation = abbreviation
        self.mMultiplier = multiplier
    
    def getPrefixGroup(self):
        'Returns the prefix group of the prefix'
        return self.mPrefixGroup
    
    def getPrefix(self):
        'Returns the name of the prefix'
        return self.mPrefix
    
    def setPrefix(self,name):
        'Sets the name of the prefix'
        self.mPrefix = name
    
    def getAbbreviation(self):
        'Returns the abbreviation for the prefix'
        return self.mAbbreviation
    
    def setAbbreviation(self,abbreviation):
        'Sets the abbreviation for the prefix'
        self.mAbbreviation = abbreviation
    
    def getMultiplier(self):
        'Returns the multiplier the prefix has'
        return self.mMultiplier
    
    def setMultiplier(self,multiplier):
        'Sets the multiplier the prefix has'
        self.mMultiplier = multiplier
    
    @staticmethod
    def fromXml(prefixGroup,xmlString):
        'Loads a new ConvertUnit object from XML.'
        doc = minidom.parse(xmlString)
        newName = doc.getElementsByTagName("name")[0].firstChild.data
        newAbbreviation = doc.getElementsByTagName("abbr")[0].firstChild.data
        newValue = doc.getElementsByTagName("value")[0].firstChild.data
        newPrefix = ConvertPrefix(prefixGroup,newName,newAbbreviation,newValue)
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
        








