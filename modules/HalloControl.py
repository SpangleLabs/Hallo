from Function import Function

class ConfigSave(Function):
    '''
    Save the current config to xml.
    '''
    #Name for use in help listing
    mHelpName = "config save"
    #Names which can be used to address the function
    mNames = set(["config save","configsave","save config"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Save the config and pickle it. godmod only."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        halloObject = userObject.getServer().getHallo()
        halloObject.saveToXml()
