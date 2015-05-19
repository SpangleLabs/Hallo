from Function import Function

class Operator(Function):
    '''
    Gives a user on an irc server "operator" status.
    '''
    #Name for use in help listing
    mHelpName = "op"
    #Names which can be used to address the function
    mNames = set(["op","operator","give op","gib op","get op","give operator","gib operator","get operator"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Op member in given channel, or current channel if no channel given. Or command user if no member given. Format: op <name> <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!="irc"):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        #If 0 arguments, op user who called command.
        lineSplit = line.split()
        if(len(lineSplit)==0):
            serverObject.send("MODE "+destinationObject.getName()+" +o "+userObject.getName(),None,"raw")
            return "Op status given."
        #If 1 argument, see if it's a channel or a user.
        if(len(lineSplit)==1):
            #If message was sent in privmsg, it's referring to a channel
            if(destinationObject is not None and destinationObject != userObject):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" +o "+userObject.getName(),None,"raw")
                return "Op status given."
            #If it starts with '#', check it's a channel hallo is in.
            if(line.startswith("#")):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" +o "+userObject.getName(),None,"raw")
                return "Op status given."
            #Check if it's a user in current channel
            targetUser = serverObject.getUserByName(line)
            if(targetUser is None or not destinationObject.isUserInChannel(targetUser)):
                return "That user is not in this channel."
            #TODO: check if hallo has op in this channel.
            serverObject.send("MODE "+destinationObject.getName()+" +o "+targetUser.getName(),None,"raw")
            return "Op status given."
        #If 2 arguments, determine which is channel and which is user.
        if(lineSplit[0].startswith("#")):
            targetChannel = serverObject.getChannelByName(lineSplit[0])
            targetUser = serverObject.getUserByName(lineSplit[1])
        elif(lineSplit[1].startswith("#")):
            targetChannel = serverObject.getChannelByName(lineSplit[1])
            targetUser = serverObject.getUserByName(lineSplit[0])
        else:
            return "Unrecognised input. Please specify user and channel."
        #Do checks on target channel and user
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        if(targetUser is None or not targetUser.isOnline()):
            return "That user is not online."
        if(not targetChannel.isUserInChannel(targetUser)):
            return "That user is not in that channel."
        serverObject.send("MODE "+targetChannel.getName()+" +o "+targetUser.getName(),None,"raw")
        return "Op status given."









