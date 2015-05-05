from Function import Function

class Permissions(Function):
    '''
    Change permissions for a specified PermissionMask
    '''
    #Name for use in help listing
    mHelpName = "permissions"
    #Names which can be used to address the function
    mNames = set(["permissions","permissionmask","permission mask"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Changes the permissions of a specified permission map. Format: permissions <location> <permission> <on/off>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        pass