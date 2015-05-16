from xml.dom import minidom
from inc.commons import Commons
from Function import Function
import re
import time

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
    
    def getFullUnitList(self):
        'Returns the full list of ConvertUnit objects, in every ConvertType object.'
        convertUnitList = []
        for typeObject in self.mTypeList:
            convertUnitList += typeObject.getUnitList()
        return convertUnitList
    
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
    
    @staticmethod
    def loadFromXml():
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
        return [self.mBaseUnit]+self.mUnitList
    
    def addUnit(self,unit):
        'Adds a new ConvertUnit object to unit list'
        self.mUnitList.append(unit)
        
    def removeUnit(self,unit):
        'Removes a ConvertUnit object to unit list'
        if(unit in self.mUnitList):
            self.mUnitList.remove(unit)
    
    def getUnitByName(self,name):
        'Get a unit by a specified name or abbreviation'
        fullUnitList = [self.mBaseUnit]+self.mUnitList
        for unitObject in fullUnitList:
            if(name in unitObject.getNameList()):
                return unitObject
        for unitObject in fullUnitList:
            if(name.lower() in [unitName.lower() for unitName in unitObject.getNameList()]):
                return unitObject
        for unitObject in fullUnitList:
            if(name in unitObject.getAbbreviationList()):
                return unitObject
        for unitObject in fullUnitList:
            if(name.lower() in [unitName.lower() for unitName in unitObject.getAbbreviationList()]):
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
    mOffset = 0
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
        self.mLastUpdated = time.time()
        self.mValue = value
    
    def getOffset(self):
        'Returns the offset of the unit.'
        return self.mOffset
    
    def setOffset(self,offset):
        'Changes the offset of the unit.'
        self.mLastUpdated = time.time()
        self.mOffset = offset
    
    def getLastUpdated(self):
        'Returns the last updated time of the unit.'
        return self.mLastUpdated
    
    def setLastUpdated(self,updateTime):
        'Changes the last updated time of the unit.'
        self.mLastUpdated = updateTime
    
    def hasName(self,inputName):
        'Checks if a specified name is a valid name or abbreviation for this unit.'
        if(inputName.lower() in [name.lower() for name in self.mNameList]):
            return True
        if(inputName.lower() in [abbr.lower() for abbr in self.mAbbreviationList]):
            return True
        return False
        
    def getPrefixFromUserInput(self,userInput):
        'Returns the prefix matching the user inputed unit name. None if no prefix. False if the input does not match this unit at all.'
        for name in self.mNameList:
            #If {X} is in the name, it means prefix goes in the middle.
            if("{X}" in name):
                nameStart = name.split("{X}")[0].lower()
                nameEnd = name.split("{X}")[1].lower()
                #Ensure that userinput starts with first half and ends with second half.
                if(not userInput.lower().startswith(nameStart) or not userInput.lower().endswith(nameEnd)):
                    continue
                userPrefix = userInput[len(nameStart):len(userInput)-len(nameEnd)]
                #If user prefix is blank, return None
                if(userPrefix==""):
                    return None
                #If no prefix group is valid, accept blank string, reject anything else.
                if(self.mValidPrefixGroup is None):
                    continue
                #Get the prefix in the group whose name matches the user input
                prefixObject = self.mValidPrefixGroup.getPrefixByName(userPrefix)
                if(prefixObject is None):
                    continue
                return prefixObject
            #So, {X} isn't in the name, so it's a standard name.
            if(not userInput.lower().endswith(name.lower())):
                continue
            #Find out what the user said was the prefix
            userPrefix = userInput[:len(userInput)-len(name)]
            if(userPrefix==""):
                return None
            #If no prefix group is valid and user didn't input a blank string, reject
            if(self.mValidPrefixGroup is None):
                continue
            #Get group's prefix that matches name
            prefixObject = self.mValidPrefixGroup.getPrefixByName(userPrefix)
            if(prefixObject is None):
                continue
            return prefixObject
        #Do the same as above, but with abbreviations
        for abbreviation in self.mAbbreviationList:
            #If {X} is in the abbreviation, it means prefix goes in the middle.
            if("{X}" in abbreviation):
                abbreviationStart = abbreviation.split("{X}")[0].lower()
                abbreviationEnd = abbreviation.split("{X}")[1].lower()
                #Ensure that userinput starts with first half and ends with second half.
                if(not userInput.lower().startswith(abbreviationStart) or not userInput.lower().endswith(abbreviationEnd)):
                    continue
                userPrefix = userInput[len(abbreviationStart):len(userInput)-len(abbreviationEnd)]
                #If user prefix is blank, return None
                if(userPrefix==""):
                    return None
                #If no prefix group is valid, accept blank string, reject anything else.
                if(self.mValidPrefixGroup is None):
                    continue
                #Get the prefix in the group whose abbreviation matches the user input
                prefixObject = self.mValidPrefixGroup.getPrefixByAbbreviation(userPrefix)
                if(prefixObject is None):
                    continue
                return prefixObject
            #So, {X} isn't in the abbreviation, so it's a standard abbreviation.
            if(not userInput.lower().endswith(abbreviation.lower())):
                continue
            #Find out what the user said was the prefix
            userPrefix = userInput[:len(userInput)-len(abbreviation)]
            if(userPrefix==""):
                return None
            #If no prefix group is valid and user didn't input a blank string, reject
            if(self.mValidPrefixGroup is None):
                continue
            #Get group's prefix that matches abbreviation
            prefixObject = self.mValidPrefixGroup.getPrefixByAbbreviation(userPrefix)
            if(prefixObject is None):
                continue
            return prefixObject
        return False
    
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
            newOffset = float(doc.getElementsByTagName("offset")[0].firstChild.data)
            newUnit.setOffset(newOffset)
        #Get update time
        if(len(doc.getElementsByTagName("last_update"))!=0):
            newLastUpdated = float(doc.getElementsByTagName("last_update")[0].firstChild.data)
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
        if(self.mOffset != 0):
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
    
    def getPrefixByName(self,name):
        'Gets the prefix with the specified name'
        for prefixObject in self.mPrefixList:
            if(prefixObject.getName() == name):
                return prefixObject
        for prefixObject in self.mPrefixList:
            if(prefixObject.getName().lower() == name.lower()):
                return prefixObject
        return None
    
    def getPrefixByAbbreviation(self,abbreviation):
        'Gets the prefix with the specified abbreviation'
        for prefixObject in self.mPrefixList:
            if(prefixObject.getAbbreviation() == abbreviation):
                return prefixObject
        for prefixObject in self.mPrefixList:
            if(prefixObject.getAbbreviation().lower() == abbreviation.lower()):
                return prefixObject
        return None
    
    def getAppropriatePrefix(self,value):
        multiplierBiggerThanOne = True
        for prefixObject in self.mPrefixList:
            multiplier = prefixObject.getMultiplier()
            if(multiplierBiggerThanOne and multiplier<1):
                multiplierBiggerThanOne = False
                if(value>1):
                    return None
            afterPrefix = value/prefixObject.getMultiplier()
            if(afterPrefix>1):
                return prefixObject
        return None
    
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
        newValue = float(doc.getElementsByTagName("value")[0].firstChild.data)
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
    Convert measure object. An amount with a unit.
    '''
    mAmount = None
    mUnit = None
    
    def __init__(self,amount,unit):
        self.mAmount = amount
        self.mUnit = unit
    
    def getUnit(self):
        'Returns the unit of the measure.'
        return self.mUnit
    
    def getAmount(self):
        'Returns the amount of the measure.'
        return self.mAmount
    
    def convertTo(self,unit):
        'Creates a new measure, equal in value but with a different unit.'
        #Check units are the same type
        if(self.mUnit.getType() != unit.getType()):
            raise Exception("These are not the same unit type.")
        #get base unit
        baseUnit = self.mUnit.getType().getBaseUnit()
        newAmount = self.mAmount * baseUnit.getValue()
        baseOffset = baseUnit.getOffset()
        if(baseOffset is not None):
            newAmount = newAmount + baseOffset
        #Convert from base unit to new unit
        unitOffset = unit.getOffset()
        if(baseOffset is not None):
            newAmount = newAmount - unitOffset
        newAmount = newAmount / unit.getValue()
        newMeasure = ConvertMeasure(newAmount,unit)
        return newMeasure
    
    def convertToBase(self):
        'Creates a new measure, equal in value, but with the base unit of the unit type.'
        baseUnit = self.mUnit.getType().getBaseUnit()
        newUnit = baseUnit
        unitValue = baseUnit.getValue()
        newAmount = self.mAmount * unitValue
        offset = baseUnit.getOffset()
        if(offset is not None):
            newAmount = newAmount + offset
        newMeasure = ConvertMeasure(newAmount,newUnit)
        return newMeasure
    
    def toString(self):
        'Converts the measure to a string for output.'
        decimalPlaces = self.mUnit.getType().getDecimals()
        decimalFormat = "{:"+str(decimalPlaces)+"f}"
        prefixGroup = self.mUnit.getPrefixGroup()
        #If there is no prefix group, output raw.
        if(prefixGroup is None):
            return decimalFormat.format(self.mAmount) + " " + self.mUnit.getName()
        #Ask the prefix group for the most appropriate prefix for the value.
        appropriatePrefix = prefixGroup.getAppropriatePrefix(self.mAmount)
        outputAmount = self.mAmount / appropriatePrefix.getMultiplier()
        #Output string
        return decimalFormat.format(outputAmount) + " " + appropriatePrefix.getName() + self.mUnit.getName()
    
    def __str__(self):
        return self.toString()
    
    def toStringWithPrefix(self,prefix):
        'Converts the measure to a string with the specified prefix.'
        decimalPlaces = self.mUnit.getType().getDecimals()
        decimalFormat = "{:"+str(decimalPlaces)+"f}"
        #Calculate the output amount
        outputAmount = self.mAmount / prefix.getMultiplier()
        #Output string
        return decimalFormat.format(outputAmount) + " " + prefix.getName() + self.mUnit.getName()
    
    @staticmethod
    def buildListFromUserInput(repo,userInput):
        'Creates a new measure from a user inputed line'
        userInputClean = userInput.strip()
        #Search through the line for digits, pull them amount as a preliminary amount and strip the rest of the line.
        #TODO: add calculation?
        preliminaryAmountString = Commons.getDigitsFromStartOrEnd(userInputClean)
        if(preliminaryAmountString is None):
            raise Exception("Cannot find amount.")
        preliminaryAmountValue = float(preliminaryAmountString)
        #Remove amountString from userInput
        if(userInput.startswith(preliminaryAmountString)):
            userInput = userInput[len(preliminaryAmountString):]
        else:
            userInput = userInput[:-len(preliminaryAmountString)]
        #Loop all units, seeing which might match userInput with prefixes. Building a list of valid measures for this input.
        newMeasureList = []
        for unitObject in repo.getFullUnitList():
            prefixObject = unitObject.getPrefixFromUserInput(userInput)
            if(prefixObject is False):
                continue
            newAmount = preliminaryAmountValue * prefixObject.getMultiplier()
            newMeasure = ConvertMeasure(newAmount,unitObject)
            newMeasureList.append(newMeasure)
        #If list is still empty, throw an exception.
        if(len(newMeasureList)==0):
            raise Exception("Unrecognised unit.")
        #Return list of matching measures.
        return newMeasureList

class Convert(Function):
    '''
    Function to convert units from one to another
    '''
    #Name for use in help listing
    mHelpName = "convert"
    #Names which can be used to address the Function
    mNames = set(["convert","conversion"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "converts values from one unit to another. Format: convert <value> <old unit> to <new unit>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        return self.convertParse(line)
        
    def convertParse(self,line,passive=False):
        #Create regex to find the place to split a user string.
        splitRegex = re.compile(' into | to |->| in ',re.IGNORECASE)
        #Load ConvertRepo
        repo = ConvertRepo.loadFromXml()
        #See if the input needs splitting.
        if(splitRegex.search(line) is None):
            try:
                fromMeasureList = ConvertMeasure.buildListFromUserInput()
                return self.convertOneUnit(fromMeasureList,passive)
            except Exception as e:
                if(passive):
                    return None
                return "I don't understand your input. ("+str(e)+") Please format like so: convert <value> <old unit> to <new unit>"
        #Split input
        lineSplit = splitRegex.split(line)
        #If there are more than 2 parts, be confused.
        if(len(lineSplit)>2):
            if(passive):
                return None
            return "I don't understand your input. (Are you specifying 3 units?) Please format like so: convert <value> <old unit> to <new unit>"
        #Try loading the first part as a measure 
        try:
            fromMeasureList = ConvertMeasure.buildListFromUserInput(repo,lineSplit[0])
            return self.convertTwoUnit(fromMeasureList,lineSplit[1],passive)
        except:
            #Try loading the second part as a measure
            try:
                fromMeasureList = ConvertMeasure.buildListFromUserInput(repo,lineSplit[1])
                return self.convertTwoUnit(fromMeasureList,lineSplit[0],passive)
            except Exception as e:
                #If both fail, send an error message
                if(passive):
                    return None
                return "I don't understand your input. ("+str(e)+") Please format like so: convert <value> <old unit> to <new unit>"
    
    
    def convertOneUnit(self,fromMeasureList,passive):
        'Converts a single given measure into whatever base unit of the type the measure is.'
        outputLines = []
        for fromMeasure in fromMeasureList:
            toMeasure = fromMeasure.convertToBase()
            outputLines.append(self.outputLine(fromMeasure,toMeasure))
        if(len(outputLines)==0):
            if(passive):
                return None
            return "I don't understand your input. (No units specified.) Please format like so: convert <value> <old unit> to <new unit>"
        return "\n".join(outputLines)
    
    def convertTwoUnit(self,fromMeasureList,userInputTo,passive):
        'Converts a single given measure into whatever unit is specified.'
        outputLines = []
        for fromMeasure in fromMeasureList:
            for toUnitObject in fromMeasure.getUnit().getType().getUnitList():
                prefixObject = toUnitObject.getPrefixFromUserInput(userInputTo)
                if(prefixObject is False):
                    continue
                toMeasure = fromMeasure.convertTo(toUnitObject)
                outputLines.append(self.outputLineWithToPrefix(fromMeasure,toMeasure,prefixObject))
        if(len(outputLines)==0):
            if(passive):
                return None
            return "I don't understand your input. (No units specified or found.) Please format like so: convert <value> <old unit> to <new unit>"
        return "\n".join(outputLines)
        
    def outputLine(self,fromMeasure,toMeasure):
        'Creates a line to output for the equality of a fromMeasure and toMeasure.'
        lastUpdate = toMeasure.getUnit().getLastUpdated() or fromMeasure.getUnit().getLastUpdated()
        outputString = fromMeasure.toString() + " = " + toMeasure.toString() + "."
        if(lastUpdate is not None):
            outputString += " (Last updated: " + Commons.formatUnixTime(lastUpdate) + ")"
        return outputString

    def outputLineWithToPrefix(self,fromMeasure,toMeasure,toPrefix):
        'Creates a line to output for the equality of a fromMeasure and toMeasure, with a specified prefix for the toMeasure.'
        lastUpdate = toMeasure.getUnit().getLastUpdated() or fromMeasure.getUnit().getLastUpdated()
        outputString = fromMeasure.toString() + " = " + toMeasure.toStringWithPrefix(toPrefix) + "."
        if(lastUpdate is not None):
            outputString += " (Last updated: " + Commons.formatUnixTime(lastUpdate) + ")"
        return outputString

    def getPassiveEvents(self):
        return Function.EVENT_MESSAGE
    
    def passiveRun(self,event,fullLine,serverObject,userObject,channelObject):
        return self.convertParse(fullLine,True)

class UpdateCurrencies(Function):
    '''
    Updates all currencies in the ConvertRepo
    '''
    #Name for use in help listing
    mHelpName = "update currencies"
    #Names which can be used to address the Function
    mNames = set(["update currencies","convert update currencies"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Update currency conversion figures, using data from the money converter, the European central bank, forex and preev."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        outputLines = []
        #Load convert repo.
        repo = ConvertRepo.loadFromXml()
        #Update with Money Converter
        outputLines.append(self.updateFromMoneyConverterData(repo) or "Updated currency data from The Money Converter.")
        #Update with the European Bank
        outputLines.append(self.updateFromEuropeanBankData(repo) or "Updated currency data from The European Bank.")
        #Update with Forex
        outputLines.append(self.updateFromForexData(repo) or "Updated currency data from Forex.")
        #Update with Preev
        outputLines.append(self.updateFromPreevData(repo) or "Updated currency data from Preev.")
        #Save repo
        repo.saveToXml()
        #Return output
        return "\n".join(outputLines)

    def getPassiveEvents(self):
        return Function.EVENT_HOUR
    
    def passiveRun(self,event,fullLine,serverObject,userObject,channelObject):
        #Load convert repo.
        repo = ConvertRepo.loadFromXml()
        #Update with Money Converter
        self.updateFromMoneyConverterData(repo)
        #Update with the European Bank
        self.updateFromEuropeanBankData(repo)
        #Update with Forex
        self.updateFromForexData(repo)
        #Update with Preev
        self.updateFromPreevData(repo)
        #Save repo
        repo.saveToXml()
        return None

    def updateFromMoneyConverterData(self,repo):
        'Updates the value of conversion currency units using The Money Convertor data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull xml data from monet converter website
        url = 'http://themoneyconverter.com/rss-feed/EUR/rss.xml'
        xmlString = Commons.loadUrlString(url)
        #Parse data
        doc = minidom.parseString(xmlString)
        root = doc.getElementsByTagName("rss")[0]
        channelElement = root.getElementsByTagName("channel")[0]
        #Loop through items, finding currencies and values
        for itemElement in channelElement.getElementsByTagName("item"):
            #Get currency code from title
            itemTitle = itemElement.getElementsByTagName("title")[0].firstChild.data
            currencyCode = itemTitle.replace("/EUR","")
            #Load value from description and get the reciprocal
            itemDescription = itemElement.getElementsByTagName("description")[0].firstChild.data
            currencyValue = 1/float(Commons.getDigitsFromStartOrEnd(itemDescription.split("=")[1].strip().replace(",","")))
            #Get currency unit, set currency value.
            currencyUnit = currencyType.getUnitByName(currencyCode)
            #If unrecognised currency, continue
            if(currencyUnit is None):
                continue
            #Set value
            currencyUnit.setValue(currencyValue)

    def updateFromEuropeanBankData(self,repo):
        'Updates the value of conversion currency units using The European Bank data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull xml data from european bank website
        url = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
        xmlString = Commons.loadUrlString(url)
        #Parse data
        doc = minidom.parseString(xmlString)
        root = doc.getElementsByTagName("gesmes:Envelope")[0]
        cubeOneElement = root.getElementsByTagName("Cube")[0]
        cubeTwoElement = cubeOneElement.getElementsByTagName("Cube")[0]
        for cubeThreeElement in cubeTwoElement.getElementsByTagName("Cube"):
            #Get currency code from currency Attribute
            currencyCode = cubeThreeElement.getAttributeNode("currency").nodeValue
            #Get value from rate attribute and get reciprocal.
            currencyValue = 1/float(cubeThreeElement.getAttributeNode("rate").nodeValue)
            #Get currency unit
            currencyUnit = currencyType.getUnitByName(currencyCode)
            #If unrecognised currency, SKIP
            if(currencyUnit is None):
                continue
            #Set Value
            currencyUnit.setValue(currencyValue)
    
    def updateFromForexData(self,repo):
        'Updates the value of conversion currency units using Forex data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull xml data from forex website
        url = 'http://rates.fxcm.com/RatesXML3'
        xmlString = Commons.loadUrlString(url)
        #Parse data
        doc = minidom.parseString(xmlString)
        ratesElement = doc.getElementsByTagName("Rates")
        for rateElement in ratesElement.getElementsByTagName("Rate"):
            #Get data from element
            symbolData = rateElement.getElementsByTagName("Symbol")[0].firstChild.data
            if(not symbolData.startswith("EUR")):
                continue
            bidData = float(rateElement.getElementsByTagName("Bid")[0].firstChild.data)
            askData = float(rateElement.getElementsByTagName("Ask")[0].firstChild.data)
            #Get currency code and value from data
            currencyCode = symbolData[3:]
            currencyValue = 1/(0.5*bidData*askData)
            #Get currency unit
            currencyUnit = currencyType.getUnitByName(currencyCode)
            #If unrecognised code, skip
            if(currencyUnit is None):
                continue
            #Set Value
            currencyUnit.setValue(currencyValue)
    
    def updateFromPreevData(self,repo):
        'Updates the value of conversion cryptocurrencies using Preev data.'
        #Get currency ConvertType
        currencyType = repo.getTypeByName("currency")
        #Pull json data from preev website, combine into 1 dict
        jsonDict = {}
        jsonDict['ltc'] = Commons.loadUrlJson("http://preev.com/pulse/units:ltc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        jsonDict['ppc'] = Commons.loadUrlJson("http://preev.com/pulse/units:ppc+usd/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        jsonDict['btc'] = Commons.loadUrlJson("http://preev.com/pulse/units:btc+eur/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        jsonDict['xdg'] = Commons.loadUrlJson("http://preev.com/pulse/units:xdg+btc/sources:bter+cryptsy+bitfinex+bitstamp+btce+localbitcoins+kraken")
        #Loop through currency codes
        for jsonKey in jsonDict:
            currencyCode = jsonKey
            #currencyDict contains the actual information about the currency
            currencyDict = jsonDict[jsonKey][jsonKey]
            currencyRef = list(currencyDict)[0]
            #Add up the volume and trade from each market, to find average trade price across them all
            totalVolume = 0
            totalTrade = 0
            for market in currencyDict[currencyRef]:
                marketVolume = currencyDict[currencyRef][market]['volume']
                marketLast = currencyDict[currencyRef][market]['last']
                totalVolume += marketVolume
                totalTrade += marketLast * marketVolume
            #Calculate currency value, compared to referenced currency, from total market average
            currencyValueRef = totalTrade/totalVolume
            #Get the ConvertUnit object for the currency reference
            currencyRefObject = currencyType.getUnitByName(currencyRef)
            if(currencyRefObject is None):
                continue
            #Work out the value compared to base unit by multiplying value of each
            currencyValue = currencyValueRef * currencyRefObject.getValue()
            #Get the currency unit and update the value
            currencyUnit = currencyType.getUnitByName(currencyCode)
            if(currencyUnit is None):
                continue
            currencyUnit.setValue(currencyValue)

class ConvertViewRepo(Function):
    '''
    Lists types, units, names, whatever.
    '''
    #Name for use in help listing
    mHelpName = "convert view repo"
    #Names which can be used to address the Function
    mNames = set(["convert view repo","convert view","convert list"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns information about the conversion repository."
    
    NAMES_TYPE = ["type","t"]
    NAMES_UNIT = ["unit","u"]
    NAMES_PREFIXGROUP = ["prefixgroup","prefix_group","prefix-group","group","g","pg"]
    NAMES_PREFIX = ["prefix","p"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repo
        repo = ConvertRepo.loadFromXml()
        #Check if type is specified
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            #Get type name and object
            typeName = self.findAnyParameter(self.NAMES_TYPE,line)
            typeObject = repo.getTypeByName(typeName)
            if(typeObject is None):
                return "Unrecognised type."
            #Check if unit & type are specified
            if(self.findAnyParameter(self.NAMES_UNIT,line)):
                #Get unit name and object
                unitName = self.findAnyParameter(self.NAMES_UNIT,line)
                unitObject = typeObject.getUnitByName(unitName)
                if(unitObject is None):
                    return "Unrecognised unit."
                return self.outputUnitAsString(unitObject)
            #Type is defined, but not unit.
            return self.outputTypeAsString(typeObject)
        #Check if prefix group is specified
        if(self.findAnyParameter(self.NAMES_PREFIXGROUP,line)):
            #Check if prefix & group are specified
            prefixGroupName = self.findAnyParameter(self.NAMES_PREFIXGROUP,line)
            prefixGroupObject = repo.getPrefixGroupByName(prefixGroupName)
            if(prefixGroupObject is None):
                return "Unrecognised prefix group."
            #Check if prefix group & prefix are specified
            if(self.findAnyParameter(self.NAMES_PREFIX,line)):
                #Get prefix name and object
                prefixName = self.findAnyParameter(self.NAMES_PREFIX,line)
                prefixObject = prefixGroupObject.getPrefixByName(prefixName) or prefixGroupObject.getPrefixByAbbreviation(prefixName)
                if(prefixGroupObject is None):
                    return "Unrecognised prefix."
                return self.outputPrefixAsString(prefixObject)
            #Prefix group is defined, but not prefix
            return self.outputPrefixGroupAsString(prefixGroupObject)
        #Check if unit is specified
        if(self.findAnyParameter(self.NAMES_UNIT,line)):
            unitName = self.findAnyParameter(self.NAMES_UNIT,line)
            outputLines = []
            #Loop through types, getting units for each type
            for typeObject in repo.getTypeList():
                unitObject = typeObject.getUnitByName(unitName)
                #If unit exists by that name, add the string format to output list
                if(unitObject is not None):
                    outputLines.append(self.outputUnitAsString(unitObject))
            if(len(outputLines)==0):
                return "Unrecognised unit."
            return "\n".join(outputLines)
        #Check if prefix is specified
        if(self.findAnyParameter(self.NAMES_PREFIX,line)):
            prefixName = self.findAnyParameter(self.NAMES_PREFIX,line)
            outputLines = []
            #Loop through groups, getting prefixes for each group
            for prefixGroupObject in repo.getPrefixGroupList()():
                prefixObject = prefixGroupObject.getPrefixByName(prefixName)
                #If prefix exists by that name, add the string format to output list
                if(prefixObject is not None):
                    outputLines.append(self.outputPrefixAsString(prefixObject))
            if(len(outputLines)==0):
                return "Unrecognised prefix."
            return "\n".join(outputLines)
        #Nothing was specified, return info on the repo.
        return self.outputRepoAsString(repo)
    
    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self,paramList,line):
        'Finds one of any parameter in a line.'
        for paramName in paramList:
            if(self.findParameter(paramName,line) is not None):
                return self.findParameter(paramName,line)
        return False
    
    def outputRepoAsString(self,repo):
        'Outputs a Conversion Repository as a string'
        outputString = "Conversion Repo:\n"
        outputString += "Unit types: " + ", ".join([typeObject.getName() for typeObject in repo.getTypeList()]) + "\n"
        outputString += "Prefix groups: " + ", ".join([typeObject.getName() for typeObject in repo.getTypeList()])
        return outputString

    def outputTypeAsString(self,typeObject):
        'Outputs a Conversion Type object as a string'
        outputString = "Conversion Type: (" + typeObject.getName() + ")\n"
        outputString += "Decimals: " + str(typeObject.getDecimals()) + "\n"
        outputString += "Base unit: " + typeObject.getBaseUnit().getNameList()[0] + "\n"
        outputString += "Other units: "
        unitNameList = [unitObject.getNames()[0] for unitObject in typeObject.getUnitList() if unitObject != typeObject.getBaseUnit()]
        outputString += ", ".join(unitNameList)
        return outputString

    def outputUnitAsString(self,unitObject):
        'Outputs a Conversion Unit object as a string'
        outputLines = []
        outputLines.append("Conversion Unit: (" + unitObject.getNameList()[0] + ")")
        outputLines.append("Type: " + unitObject.getType().getName())
        outputLines.append("Name list: " + ", ".join(unitObject.getNameList()))
        outputLines.append("Abbreviation list: " + ", ".join(unitObject.getAbbreviationList()))
        outputLines.append("Value: 1 " + unitObject.getNameList()[0] + " = " + str(unitObject.getValue()) + " " + unitObject.getType().getBaseUnit().getNameList()[0])
        outputLines.append("Offset: 0 " + unitObject.getNameList()[0] + " = " + str(unitObject.getOffset()) + " " + unitObject.getType().getBaseUnit().getNameList()[0])
        lastUpdate = unitObject.getLastUpdated()
        if(lastUpdate is not None):
            outputLines.append("Last updated: " + Commons.formatUnixTime(lastUpdate))
        prefixGroupName = unitObject.getValidPrefixGroup().getName()
        if(prefixGroupName is not None):
            outputLines.append("Prefix group: " + prefixGroupName)
        return "\n".join(outputLines)

    def outputPrefixGroupAsString(self,prefixGroupObject):
        'Outputs a Conversion PrefixGroup object as a string'
        outputString = "Prefix group: (" + prefixGroupObject.getName() + ")\n"
        outputString += "Prefix list: " + ", ".join([prefixObject.getName() for prefixObject in prefixGroupObject.getPrefixList()])
        return outputString
    
    def outputPrefixAsString(self,prefixObject):
        'Outputs a Conversion prefix object as a string'
        outputString = "Prefix: (" + prefixObject.getPrefix() + ")\n"
        outputString += "Abbreviation: " + prefixObject.getAbbreviation() + "\n"
        outputString += "Multiplier: " + str(prefixObject.getName())
        return outputString
    
class ConvertSet(Function):
    '''
    Function to set the value of a unit manually.
    Will create a new unit if no unit is found.
    '''
    #Name for use in help listing
    mHelpName = "convert set"
    #Names which can be used to address the Function
    mNames = set(["convert set"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets the value of a unit, Format: <amount> <unit_set> = <amount>? <unit_reference>."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load Conversion Repo
        repo = ConvertRepo.loadFromXml()
        #Create regex to find the place to split a user string.
        splitRegex = re.compile(' into | to |->| in ',re.IGNORECASE)
        #Split input
        lineSplit = splitRegex.split(line)
        #If there are more than 2 parts, be confused.
        if(len(lineSplit)>2):
            return "I don't understand your input. (Are you specifying 3 units?) Please format like so: convert <value> <old unit> to <new unit>"
        #Try loading the second part (reference measure) as a measure
        try:
            refMeasureList = ConvertMeasure.buildListFromUserInput(repo,lineSplit[1])
        except Exception:
            try:
                refMeasureList = ConvertMeasure.buildListFromUserInput(repo,"1"+lineSplit[1])
            except:
                return "I don't understand the second half of your input."
        #Try loading the first part as a measure
        try:
            varMeasureList = ConvertMeasure.buildListFromUserInput(repo,lineSplit[0])
        except:
            try:
                varMeasureList = ConvertMeasure.buildListFromUserInput(repo,"1"+lineSplit[0])
            except:
                #Add a unit.
                return self.addUnit(lineSplit[0],refMeasureList)
        return self.setUnit(varMeasureList,refMeasureList)
    
    def setUnit(self,varMeasureList,refMeasureList):
        #Find list of pairs of measures, sharing a type
        measurePairList = []
        for varMeasure in varMeasureList:
            varMeasureType = varMeasure.getUnit().getType()
            for refMeasure in refMeasureList:
                refMeasureType = refMeasure.getUnit().getType()
                if(varMeasureType==refMeasureType):
                    measurePair = {}
                    measurePair['var'] = varMeasure
                    measurePair['ref'] = refMeasure
                    measurePairList.append(measurePair)
        #Check lists have exactly 1 pair sharing a type
        if(len(measurePairList)==0):
            return "These units do not share the same type."
        if(len(measurePairList) > 1):
            return "It is ambiguous which units you are referring to."
        #Get the correct varMeasure and refMeasure and all associated required variables
        varMeasure = measurePairList[0]['var']
        refMeasure = measurePairList[0]['ref']
        varAmount = varMeasure.getAmount()
        refAmount = refMeasure.getAmount()
        varUnit = varMeasure.getUnit()
        varName = varUnit.getNameList()[0]
        baseName = varUnit.getType().getBaseUnit().getNameList()[0]
        refUnit = refMeasure.getUnit()
        varValue = varUnit.getValue()
        refValue = refUnit.getValue()
        varOffset = varUnit.getOffset()
        refOffset = refUnit.getOffset()
        #If varUnit is the base unit, it cannot be set.
        if(varUnit == varUnit.getType().getBaseUnit()):
            return "You cannot change values of the base unit."
        #If either given amount are zero, set the offset of varUnit.
        if(varAmount==0 or refAmount==0):
            #Calculate the new offset
            newOffset = (refAmount-(varAmount*varValue))*refValue+refOffset
            varUnit.setOffset(newOffset)
            #Save repo
            repo = varUnit.getType().getRepo()
            repo.saveToXml()
            #Output message
            return "Set new offset for " + varName + ": 0 " + varName + " = " + str(newOffset) + " " + baseName + "."
        #Get new value
        newValue = (refAmount-((varOffset-refOffset)/refValue))/varAmount
        varUnit.setValue(newValue)
        #Save repo
        repo = varUnit.getType().getRepo()
        repo.saveToXml()
        #Output message
        return "Set new value for " + varName + ": Δ 1 " + varName + " = Δ " + str(newValue) + " " + baseName + "."
    
    def addUnit(self,userInput,refMeasureList):
        #Check reference measure has exactly 1 unit option
        if(len(refMeasureList)==0):
            return "There is no defined unit matching the reference name."
        if(len(refMeasureList) > 1):
            return "It is ambiguous which unit you are referring to."
        #Get unit type
        refMeasure = refMeasureList[0]
        refAmount = refMeasure.getAmount()
        refUnit = refMeasure.getUnit()
        refType = refUnit.getType()
        refValue = refUnit.getValue()
        refOffset = refUnit.getOffset()
        baseUnit = refType.getBaseUnit()
        baseName = baseUnit.getNameList()[0]
        #Get amount & unit name
        inputAmountString = Commons.getDigitsFromStartOrEnd(userInput)
        if(inputAmountString is None):
            return "Please specify an amount when setting a new unit."
        inputAmountFloat = float(inputAmountString)
        #Remove amountString from userInput
        if(userInput.startswith(inputAmountString)):
            inputName = userInput[len(inputAmountString):]
        else:
            inputName = userInput[:-len(inputAmountString)]
        #Check name isn't already in use.
        if(refType.getUnitByName(inputName) is not None):
            return "There's already a unit of that type by that name."
        #Add unit
        newUnit = ConvertUnit(refType,[inputName],1)
        refType.addUnit(newUnit)
        #Update offset or value, based on what the user inputed.
        #If either given amount are zero, set the offset of varUnit.
        if(inputAmountFloat==0 or refAmount==0):
            #Calculate the new offset
            newOffset = (refAmount-(inputAmountFloat*1))*refValue+refOffset
            newUnit.setOffset(newOffset)
            #Save repo
            repo = refUnit.getType().getRepo()
            repo.saveToXml()
            #Output message
            return "Created new unit " + inputName + " with offset: 0 " + inputName + " = " + str(newOffset) + " " + baseName + "."
        #Get new value
        newValue = (refAmount-((0-refOffset)/refValue))/inputAmountFloat
        newUnit.setValue(newValue)
        #Save repo
        repo = refUnit.getType().getRepo()
        repo.saveToXml()
        #Output message
        return "Created new unit " + inputName + " with value: 1 " + inputName + " = " + str(newValue) + " " + baseName + "."

class ConvertAddType(Function):
    '''
    Adds a new conversion type.
    '''
    #Name for use in help listing
    mHelpName = "convert add type"
    #Names which can be used to address the Function
    mNames = set(["convert add type"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Adds a new conversion unit type and base unit."
    
    NAMES_BASEUNIT = ["baseunit","base_unit","base-unit","unit","u","b","bu"]
    NAMES_DECIMALS = ["decimals","decimal","decimalplaces","dp","d"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repo, clean line
        repo = ConvertRepo.loadFromXml()
        lineClean = line.strip()
        #Check if base unit is defined
        unitName = None
        if(self.findAnyParameter(self.NAMES_BASEUNIT,lineClean)):
            unitName = self.findAnyParameter(self.NAMES_BASEUNIT,lineClean)
        #Check if decimal places is defined
        decimals = None
        if(self.findAnyParameter(self.NAMES_DECIMALS,lineClean)):
            try:
                decimals = int(self.findAnyParameter(self.NAMES_DECIMALS,lineClean))
            except:
                decimals = None
        #Clean unit and type setting from the line to just get the name to remove
        paramRegex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)",re.IGNORECASE)
        multispaceRegex = re.compile("\s+")
        inputName = paramRegex.sub("\1\4",lineClean).strip()
        inputName = multispaceRegex.sub(" ",inputName)
        #Check that type name doesn't already exist.
        existingType = repo.getTypeByName(inputName)
        if(existingType is not None):
            return "A type by this name already exists."
        #Check base unit name was defined.
        if(unitName is None):
            return "You must define a base unit for this type using unit=<unit name>."
        #Create new type, Create new unit, set unit as base unit, set decimals
        newType = ConvertType(repo,inputName)
        newBaseUnit = ConvertUnit(newType,[unitName],1)
        newType.setBaseUnit(newBaseUnit)
        if(decimals is not None):
            newType.setDecimals(decimals)
        #add type to repo, save
        repo.addType(newType)
        repo.saveToXml()
        #Output message
        outputString = "Created new type \"" +inputName + "\" with base unit \"" + unitName + "\""
        if(decimals is not None):
            outputString += " and " + str(decimals) + " decimal places"
        outputString += "."
        return outputString

class ConvertSetTypeDecimals(Function):
    '''
    Sets the number of decimal places to show for a unit type.
    '''
    #Name for use in help listing
    mHelpName = "convert set type decimals"
    #Names which can be used to address the Function
    mNames = set(["convert set type decimals","convert set type decimal"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets the number of decimal places to show for a unit type."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load convert repo
        repo = ConvertRepo.loadFromXml()
        #Get decimals from input
        inputDecimals = Commons.getDigitsFromStartOrEnd(line)
        #If decimals is null, return error
        if(inputDecimals is None):
            return "Please specify a conversion type and a number of decimal places it should output."
        #Get type name from input
        if(line.startswith(inputDecimals)):
            inputName = line[len(inputDecimals):].strip()
        else:
            inputName = line[:-len(inputDecimals)].strip()
        #Convert decimals to integer
        decimals = int(float(inputDecimals))
        #Get selected type
        inputType = repo.getTypeByName(inputName)
        #If type does not exist, return error
        if(inputType is None):
            return "This is not a recognised conversion type."
        #Set decimals
        inputType.setDecimals(decimals)
        #Save repo
        repo.saveToXml()
        #Output message
        return "Set the number of decimal places to display for \"" + inputType.getName() + "\" type units at " + str(decimals) + " places."

class ConvertRemoveUnit(Function):
    '''
    Removes a specified unit from the conversion repo.
    '''
    #Name for use in help listing
    mHelpName = "convert remove unit"
    #Names which can be used to address the Function
    mNames = set(["convert remove unit","convert delete unit","convert unit remove","convert unit delete"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Removes a specified unit from the conversion repository."
    
    NAMES_TYPE = ["type","t"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load convert repo
        repo = ConvertRepo.loadFromXml()
        #Check if a type is specified
        typeName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            typeName = self.findAnyParameter(self.NAMES_TYPE,line)
        #Clean type setting from the line to just get the name to remove
        paramRegex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)",re.IGNORECASE)
        inputName = paramRegex.sub("\1\4",line).strip()
        #Find unit
        if(typeName is not None):
            typeObject = repo.getTypeByName(typeName)
            if(typeObject is None):
                return "This conversion type is not recognised."
            inputUnit = typeObject.getUnitByName(inputName)
            if(inputUnit is None):
                return "This unit name is not recognised for that unit type."
        else:
            inputUnitList = []
            for typeObject in repo.getTypeList():
                inputUnit = typeObject.getUnitByName(inputName)
                if(inputUnit is not None):
                    inputUnitList.append(inputUnit)
            #Check if results are 0
            if(len(inputUnitList)==0):
                return "No unit by that name is found in any type."
            #Check if results are >=2
            if(len(inputUnitList)>=2):
                return ""
            inputUnit = inputUnitList[0]
        #Ensure it is not a base unit for its type
        if(inputUnit == inputUnit.getType().getBaseUnit()):
            return "You cannot remove the base unit for a unit type."
        #Remove unit
        inputUnitName = inputUnit.getNames()[0]
        inputUnit.getType().removeUnit(inputUnit)
        #Done
        return "Removed unit \""+ inputUnitName +"\" from conversion repository."

    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self,paramList,line):
        'Finds one of any parameter in a line.'
        for paramName in paramList:
            if(self.findParameter(paramName,line) is not None):
                return self.findParameter(paramName,line)
        return False

class ConvertUnitAddName(Function):
    '''
    Adds a new name to a unit.
    '''
    #Name for use in help listing
    mHelpName = "convert unit add name"
    #Names which can be used to address the Function
    mNames = set(["convert unit add name"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Adds a new name to a unit."
    
    NAMES_UNIT = ["unit","u"]
    NAMES_TYPE = ["type","t"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repository
        repo = ConvertRepo.loadFromXml()
        #Check for type=
        typeName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            typeName = self.findAnyParameter(self.NAMES_TYPE,line)
        #Check for unit=
        unitName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            unitName = self.findAnyParameter(self.NAMES_TYPE,line)
        #clean up the line
        paramRegex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)",re.IGNORECASE)
        inputName = paramRegex.sub("\1\4",line).strip()
        #Get unit list
        if(typeName is None):
            unitList = repo.getFullUnitList()
        else:
            typeObject = repo.getTypeByName(typeName)
            if(typeObject is None):
                return "Unrecognised type."
            unitList =  typeObject.getUnitList()
        #If no unit=, try splitting the line to find where the old name ends and new name begins
        if(unitName is None):
            #Start splitting from shortest left-string to longest.
            lineSplit = inputName.split()
            inputUnitList = []
            foundName = False
            for inputUnitName in [' '.join(lineSplit[:x+1]) for x in range(len(lineSplit))]:
                for unitObject in unitList:
                    if(unitObject.hasName(inputUnitName)):
                        inputUnitList.append(unitObject)
                        foundName = True
                if(foundName):
                    break
            newUnitName = inputName[len(inputUnitName):].strip()
        else:
            inputUnitList = []
            for unitObject in unitList:
                if(unitObject.hasName(inputUnitName)):
                    inputUnitList.append(unitObject)
            newUnitName = inputName
        #If 0 units found, throw error
        if(len(inputUnitList)==0):
            return "No unit found by that name."
        #If 2+ units found, throw error
        if(len(inputUnitList)>=2):
            return "Unit name is too ambiguous, please specify with unit= and type= ."
        unitObject = inputUnitList[0]
        #Add the new name
        unitObject.addName(newUnitName)
        #Save repo
        repo.saveToXml()
        #Output message
        return "Added \""+newUnitName+"\" as a new name for the \""+unitObject.getNameList()[0]+"\" unit."

    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self,paramList,line):
        'Finds one of any parameter in a line.'
        for paramName in paramList:
            if(self.findParameter(paramName,line) is not None):
                return self.findParameter(paramName,line)
        return False

class ConvertUnitAddAbbreviation(Function):
    '''
    Adds a new abbreviation to a unit.
    '''
    #Name for use in help listing
    mHelpName = "convert unit add abbreviation"
    #Names which can be used to address the Function
    mNames = set(["convert unit add abbreviation","convert unit add abbr"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Adds a new abbreviation to a unit."
    
    NAMES_UNIT = ["unit","u"]
    NAMES_TYPE = ["type","t"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repository
        repo = ConvertRepo.loadFromXml()
        #Check for type=
        typeName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            typeName = self.findAnyParameter(self.NAMES_TYPE,line)
        #Check for unit=
        unitName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            unitName = self.findAnyParameter(self.NAMES_TYPE,line)
        #clean up the line
        paramRegex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)",re.IGNORECASE)
        inputAbbr = paramRegex.sub("\1\4",line).strip()
        #Get unit list
        if(typeName is None):
            unitList = repo.getFullUnitList()
        else:
            typeObject = repo.getTypeByName(typeName)
            if(typeObject is None):
                return "Unrecognised type."
            unitList =  typeObject.getUnitList()
        #If no unit=, try splitting the line to find where the old name ends and new name begins
        if(unitName is None):
            #Start splitting from shortest left-string to longest.
            lineSplit = inputAbbr.split()
            inputUnitList = []
            foundAbbr = False
            for inputUnitName in [' '.join(lineSplit[:x+1]) for x in range(len(lineSplit))]:
                for unitObject in unitList:
                    if(unitObject.hasName(inputUnitName)):
                        inputUnitList.append(unitObject)
                        foundAbbr = True
                if(foundAbbr):
                    break
            newUnitAbbr = inputAbbr[len(inputUnitName):].strip()
        else:
            inputUnitList = []
            for unitObject in unitList:
                if(unitObject.hasName(inputUnitName)):
                    inputUnitList.append(unitObject)
            newUnitAbbr = inputAbbr
        #If 0 units found, throw error
        if(len(inputUnitList)==0):
            return "No unit found by that name."
        #If 2+ units found, throw error
        if(len(inputUnitList)>=2):
            return "Unit name is too ambiguous, please specify with unit= and type= ."
        unitObject = inputUnitList[0]
        #Add the new name
        unitObject.addAbbreviation(newUnitAbbr)
        #Save repo
        repo.saveToXml()
        #Output message
        return "Added \""+newUnitAbbr+"\" as a new abbreviation for the \""+unitObject.getNameList()[0]+"\" unit."

    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self,paramList,line):
        'Finds one of any parameter in a line.'
        for paramName in paramList:
            if(self.findParameter(paramName,line) is not None):
                return self.findParameter(paramName,line)
        return False

class ConvertUnitRemoveName(Function):
    '''
    Removes a name or abbreviation from a unit, unless it's the last name.
    '''
    #Name for use in help listing
    mHelpName = "convert unit remove name"
    #Names which can be used to address the Function
    mNames = set(["convert unit remove name","convert unit delete name","convert unit remove abbreviation","convert unit delete abbreviation","convert unit remove abbr","convert unit delete abbr","convert remove unit name","convert delete unit name","convert remove unit abbreviation","convert delete unit abbreviation","convert remove unit abbr","convert delete unit abbr"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Removes a name or abbreviation from a unit, unless it's the last name."
    
    NAMES_UNIT = ["unit","u"]
    NAMES_TYPE = ["type","t"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repo, clean line
        repo = ConvertRepo.loadFromXml()
        lineClean = line.strip()
        #Check if unit is defined
        unitName = None
        if(self.findAnyParameter(self.NAMES_UNIT,lineClean)):
            unitName = self.findAnyParameter(self.NAMES_UNIT,lineClean)
        #Check if type is defined
        typeName = None
        if(self.findAnyParameter(self.NAMES_TYPE,lineClean)):
            typeName = self.findAnyParameter(self.NAMES_TYPE,lineClean)
            if(repo.getTypeByName(typeName) is None):
                return "Invalid type specified."
        #Clean unit and type setting from the line to just get the name to remove
        paramRegex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)",re.IGNORECASE)
        inputName = paramRegex.sub("\1\4",lineClean).strip()
        #Check if description is sufficient to narrow it to 1 and only 1 unit
        userUnitOptions = []
        for unitObject in repo.getFullUnitList():
            #If type is defined and not the same as current unit, skip it
            if(typeName is not None and typeName != unitObject.getType().getName()):
                continue
            #if unit name is defined and not a valid name for the unit, skip it.
            if(unitName is not None and not unitObject.hasName(unitName)):
                continue
            #If inputName is not a valid name for the unit, skip it.
            if(not unitObject.hasName(inputName)):
                continue
            #Otherwise it's the one, add it to the list
            userUnitOptions.append(unitObject)
        #Check if that narrowed it down correctly.
        if(len(userUnitOptions)==0):
            return "There are no units matching that description."
        if(len(userUnitOptions)>=2):
            return "It is ambiguous which unit you refer to."
        #Check this unit has other names.
        userUnit = userUnitOptions[0]
        if(len(userUnit.getNameList())==1):
            return "This unit only has 1 name, you cannot remove its last name."
        #Remove name
        userUnit.removeName(inputName)
        #Save repo
        repo.saveToXml()
        #Output
        return "Removed name \""+inputName+"\" from \""+userUnit.getNamelist()[0]+"\" unit."

    
    def findParameter(self,paramName,line):
        'Finds a parameter value in a line, if the format parameter=value exists in the line'
        paramValue = None
        paramRegex = re.compile("(^|\s)"+paramName+"=([^\s]+)(\s|$)",re.IGNORECASE)
        paramSearch = paramRegex.search(line)
        if(paramSearch is not None):
            paramValue = paramSearch.group(2)
        return paramValue

    def findAnyParameter(self,paramList,line):
        'Finds one of any parameter in a line.'
        for paramName in paramList:
            if(self.findParameter(paramName,line) is not None):
                return self.findParameter(paramName,line)
        return False

class ConvertUnitSetPrefixGroup(Function):
    '''
    Sets the prefix group for a unit.
    '''
    #Name for use in help listing
    mHelpName = "convert unit remove name"
    #Names which can be used to address the Function
    mNames = set(["convert unit remove name","convert unit delete name","convert unit remove abbreviation","convert unit delete abbreviation","convert unit remove abbr","convert unit delete abbr","convert remove unit name","convert delete unit name","convert remove unit abbreviation","convert delete unit abbreviation","convert remove unit abbr","convert delete unit abbr"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Removes a name or abbreviation from a unit, unless it's the last name."
    
    NAMES_UNIT = ["unit","u"]
    NAMES_TYPE = ["type","t"]
    NAMES_PREFIXGROUP = ["prefixgroup","prefix_group","prefix-group","group","g","pg"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load repository
        repo = ConvertRepo.loadFromXml()
        #Check for type=
        typeName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            typeName = self.findAnyParameter(self.NAMES_TYPE,line)
        #Check for unit=
        unitName = None
        if(self.findAnyParameter(self.NAMES_TYPE,line)):
            unitName = self.findAnyParameter(self.NAMES_TYPE,line)
        #Check for prefixgroup=
        prefixGroupName = None
        if(self.findAnyParameter(self.NAMES_PREFIXGROUP,line)):
            prefixGroupName = self.findAnyParameter(self.NAMES_PREFIXGROUP,line)
        #clean up the line
        paramRegex = re.compile("(^|\s)([^\s]+)=([^\s]+)(\s|$)",re.IGNORECASE)
        inputName = paramRegex.sub("\1\4",line).strip()
        #Get prefix group
        if(prefixGroupName is None):
            lineSplit = inputName.split()
            if(repo.getPrefixGroupByName(lineSplit[0]) is not None):
                prefixGroup = repo.getPrefixGroupByName(lineSplit[0])
                inputName = ' '.join(lineSplit[1:])
            elif(repo.getPrefixGroupByName(lineSplit[-1]) is not None):
                prefixGroup = repo.getPrefixGroupByName(lineSplit[-1])
                inputName = ' '.join(lineSplit[:-1])
            elif(lineSplit[0].lower()=="none"):
                prefixGroup = None
                inputName = ' '.join(lineSplit[1:])
            elif(lineSplit[-1].lower()=="none"):
                prefixGroup = None
                inputName = ' '.join(lineSplit[1:])
            else:
                return "Prefix group not recognised."
        else:
            prefixGroup = repo.getPrefixGroupByName(prefixGroupName)
            if(prefixGroup is None and prefixGroupName.lower()!="none"):
                return "Prefix group not recognised."
        #Get unit list
        if(typeName is None):
            unitList = repo.getFullUnitList()
        else:
            typeObject = repo.getTypeByName(typeName)
            if(typeObject is None):
                return "Unrecognised type."
            unitList =  typeObject.getUnitList()
        #If no unit=, try splitting the line to find where the old name ends and new name begins
        if(unitName is None):
            inputUnitList = []
            for unitObject in unitList:
                if(unitObject.hasName(inputName)):
                    inputUnitList.append(unitObject)
        else:
            inputUnitList = []
            for unitObject in unitList:
                if(unitObject.hasName(unitName)):
                    inputUnitList.append(unitObject)
        #If 0 units found, throw error
        if(len(inputUnitList)==0):
            return "No unit found by that name."
        #If 2+ units found, throw error
        if(len(inputUnitList)>=2):
            return "Unit name is too ambiguous, please specify with unit= and type= ."
        unitObject = inputUnitList[0]
        #Set the prefix group
        unitObject.setPrefixGroup(prefixGroup)
        #Save repo
        repo.saveToXml()
        #Output message
        if(prefixGroup is None):
            prefixGroupName = "none"
        else:
            prefixGroupName = prefixGroup.getName()
        return "Set \""+prefixGroupName+"\" as the prefix group for the \""+unitObject.getNameList()[0]+"\" unit."


