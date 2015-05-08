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
    SERVER_NAMES = ["server","serv","s"]
    CHANNEL_NAMES = ["channel","chan","room"]
    USER_GROUP_NAMES = ["usergroup","user_group","user-group","group"]
    USER_NAMES = ["user","person","u"]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineSplit = line.split()
        if(len(lineSplit)<3):
            return "You need to specify a location, a right and the value"
        boolInput = lineSplit[-1]
        rightInput = lineSplit[-2]
        locationInput = lineSplit[:-3]
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
        #If locationInput is a list with more than 2 elements, I don't know how to proceed.
        if(len(locationInput)>2):
            return "I'm not sure how to interpret that PermissionMask location"
        #If they've specified a server & channel or server & user, parse here
        if(len(locationInput)==2):
            #Find server object.
            if(any([locationInput[0].startswith(serverStr+"=") for serverStr in self.SERVER_NAMES])):
                serverName = locationInput[0].split("=")[1]
                locationOther = locationInput[1]
            elif(any([locationInput[1].startswith(serverStr+"=") for serverStr in self.SERVER_NAMES])):
                serverName = locationInput[1].split("=")[1]
                locationOther = locationInput[0]
            else:
                return "No server name found."
            serverObject = userObject.getServer().getHallo().getServerByName(serverName)
            if(serverObject is None):
                return "No server exists by that name."
            #Check if they have specified a channel
            if(any([locationOther.startswith(channelStr+"=") for channelStr in self.CHANNEL_NAMES])):
                #Get channel by that name
                channelName = locationOther.split("=")[1]
                channelObject = userObject.getServer().getChannelByName(channelName)
                permissionMask = channelObject.getPermissionMask()
                return permissionMask
            #Check if they've specified a user
            if(any([locationOther.startswith(userStr+"=") for userStr in self.USER_NAMES])):
                #Get the user by that name
                userName = locationOther.split("=")[1]
                userObject.getServer().getUserByName(userName)
                permissionMask = userObject.getPermissionMask()
                return permissionMask
            return "Input not understood. You specified a server but not channel or user?"
        ##All following have length locationInput ==1.
        #Check if they want to set generic hallo permissions
        if(locationInput[0] in self.HALLO_NAMES):
            permissionMask = userObject.getServer().getHallo().getPermissionMask()
            return permissionMask
        #Check if they have asked for current server
        if(locationInput[0] in self.SERVER_NAMES):
            permissionMask = userObject.getServer().getPermissionMask()
            return permissionMask
        #Check if they have specified a server
        if(any([locationInput[0].startswith(serverStr+"=") for serverStr in self.SERVER_NAMES])):
            serverName = locationInput[0].split("=")[1]
            serverObject = userObject.getServer().getHallo().getServerByName(serverName)
            if(serverObject is None):
                return "No server exists by that name."
            permissionMask = serverObject.getPermissionMask()
            return permissionMask
        #Check if they've asked for current channel
        if(locationInput[0] in self.CHANNEL_NAMES):
            #Check if this is a channel, and not privmsg.
            if(destinationObject==None or destinationObject==userObject):
                return "You can't set generic channel permissions in a privmsg."
            permissionMask = destinationObject.getPermissionMask()
            return permissionMask
        #Check if they have specified a channel
        if(any([locationInput[0].startswith(channelStr+"=") for channelStr in self.CHANNEL_NAMES])):
            #Get channel by that name
            channelName = locationInput[0].split("=")[1]
            channelObject = userObject.getServer().getChannelByName(channelName)
            permissionMask = channelObject.getPermissionMask()
            return permissionMask
        #Check if they've specified a user group?
        if(any([locationInput[0].startswith(userGroupStr+"=") for userGroupStr in self.USER_GROUP_NAMES])):
            #See if you can find a UserGroup with that name
            userGroupName = locationInput[0].split("=")[1]
            halloObject = userObject.getServer().getHallo()
            userGroupObject = halloObject.getUserGroupByName(userGroupName)
            if(userGroupObject==None):
                return "No user group exists by that name."
            #get permission mask and output
            permissionMask = userGroupObject.getPermissionMask()
            return permissionMask
        #Check if they've specified a user
        if(any([locationInput[0].startswith(userStr+"=") for userStr in self.USER_NAMES])):
            #Get the user by that name
            userName = locationInput[0].split("=")[1]
            userObject.getServer().getUserByName(userName)
            permissionMask = userObject.getPermissionMask()
            return permissionMask
        #Check if their current channel has any user by the name of whatever else they might have said?
        if(destinationObject==None or destinationObject==userObject):
            userList = destinationObject.getUserList()
            userListMatching = [userObject for userObject in userList if userObject.getName()==locationInput[0]]
            if(len(userListMatching)==0):
                return "I do not understand your input. I cannot find that Permission Mask."
            userObject = userListMatching[0]
            permissionMask = userObject.getPermissionMask()
            return permissionMask
        #My normal approaches failed. Generic error message
        return None
            



