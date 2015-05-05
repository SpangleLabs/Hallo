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
    
    HALLO_NAMES = ["hallo","core","all","*","default"]
    SERVER_NAMES = ["server","serv"]
    CHANNEL_NAMES = ["channel","chan","room"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineSplit = line.split()
        locationInput = lineSplit[0].lower()
        #Search for the permissionMask they want.
        permissionMask = self.findPermissionMask(locationInput,userObject,destinationObject)
        #If it comes back unspecified, generic error message
        if(permissionMask is None):
            return "I can't find that permission mask. Specify which you wish to modify as user={username}, or similarly for usergroup, channel, server or hallo."
        #If it comes back with an error message, return that error
        #TODO: use exception.
        if(permissionMask.__class__.__name__ == "str"):
            return permissionMask
        pass
    
    def findPermissionMask(self,locationInput,userObject,destinationObject):
        #Check if they want to set generic hallo permissions
        if(locationInput in self.HALLO_NAMES):
            permissionMask = userObject.getServer().getHallo().getPermissionMask()
            return permissionMask
        #Check if they have asked for current server
        if(locationInput in self.SERVER_NAMES):
            permissionMask = userObject.getServer().getPermissionMask()
            return permissionMask
        #Check if they have specified a server
        if(any([locationInput.startswith(serverStr+"=") for serverStr in self.SERVER_NAMES])):
            serverName = locationInput.split("=")[1]
            serverObject = userObject.getServer().getHallo().getServerByName(serverName)
            if(serverObject is None):
                return "No server exists by that name."
            permissionMask = serverObject.getPermissionMask()
            return permissionMask
        #Check if they've asked for current channel
        if(locationInput in self.CHANNEL_NAMES):
            #Check if this is a channel, and not privmsg.
            if(destinationObject==None or destinationObject==userObject):
                return "You can't set generic channel permissions in a privmsg."
            



