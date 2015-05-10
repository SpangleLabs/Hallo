

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
    mNames = []
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
    
    def getValue(self):
        'Returns the value of the unit.'
        raise NotImplementedError
    
    def setValue(self,value):
        'Changes the value of the unit.'
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
        raise NotImplementedError
    
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












