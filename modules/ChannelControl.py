from Function import Function
from inc.commons import Commons
from Server import Server

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
        if(serverObject.getType()!=Server.TYPE_IRC):
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
        #TODO: check if hallo has op in this channel.
        serverObject.send("MODE "+targetChannel.getName()+" +o "+targetUser.getName(),None,"raw")
        return "Op status given."

class DeOperator(Function):
    '''
    Removes a user on an irc server's "operator" status.
    '''
    #Name for use in help listing
    mHelpName = "deop"
    #Names which can be used to address the function
    mNames = set(["deop","deoperator","unoperator","take op","del op","delete op","remove op","take operator","del operator","delete op","remove operator"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Deop member in given channel, or current channel if no channel given. Or command user if no member given. Format: deop <name> <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!=Server.TYPE_IRC):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        #If 0 arguments, op user who called command.
        lineSplit = line.split()
        if(len(lineSplit)==0):
            serverObject.send("MODE "+destinationObject.getName()+" -o "+userObject.getName(),None,"raw")
            return "Op status taken."
        #If 1 argument, see if it's a channel or a user.
        if(len(lineSplit)==1):
            #If message was sent in privmsg, it's referring to a channel
            if(destinationObject is not None and destinationObject != userObject):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" -o "+userObject.getName(),None,"raw")
                return "Op status taken."
            #If it starts with '#', check it's a channel hallo is in.
            if(line.startswith("#")):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" -o "+userObject.getName(),None,"raw")
                return "Op status taken."
            #Check if it's a user in current channel
            targetUser = serverObject.getUserByName(line)
            if(targetUser is None or not destinationObject.isUserInChannel(targetUser)):
                return "That user is not in this channel."
            #TODO: check if hallo has op in this channel.
            serverObject.send("MODE "+destinationObject.getName()+" -o "+targetUser.getName(),None,"raw")
            return "Op status taken."
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
        #TODO: check if hallo has op in this channel.
        serverObject.send("MODE "+targetChannel.getName()+" -o "+targetUser.getName(),None,"raw")
        return "Op status taken."

class Voice(Function):
    '''
    Gives a user on an irc server "voice" status.
    '''
    #Name for use in help listing
    mHelpName = "voice"
    #Names which can be used to address the function
    mNames = set(["voice","give voice","gib voice","get voice"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Voice member in given channel, or current channel if no channel given, or command user if no member given. Format: voice <name> <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!=Server.TYPE_IRC):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        #If 0 arguments, op user who called command.
        lineSplit = line.split()
        if(len(lineSplit)==0):
            serverObject.send("MODE "+destinationObject.getName()+" +v "+userObject.getName(),None,"raw")
            return "Voice status given."
        #If 1 argument, see if it's a channel or a user.
        if(len(lineSplit)==1):
            #If message was sent in privmsg, it's referring to a channel
            if(destinationObject is not None and destinationObject != userObject):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" +v "+userObject.getName(),None,"raw")
                return "Voice status given."
            #If it starts with '#', check it's a channel hallo is in.
            if(line.startswith("#")):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" +v "+userObject.getName(),None,"raw")
                return "Voice status given."
            #Check if it's a user in current channel
            targetUser = serverObject.getUserByName(line)
            if(targetUser is None or not destinationObject.isUserInChannel(targetUser)):
                return "That user is not in this channel."
            #TODO: check if hallo has op in this channel.
            serverObject.send("MODE "+destinationObject.getName()+" +v "+targetUser.getName(),None,"raw")
            return "Voice status given."
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
        #TODO: check if hallo has op in this channel.
        serverObject.send("MODE "+targetChannel.getName()+" +o "+targetUser.getName(),None,"raw")
        return "Voice status given."

class DeVoice(Function):
    '''
    Removes a user on an irc server's "voice" status.
    '''
    #Name for use in help listing
    mHelpName = "devoice"
    #Names which can be used to address the function
    mNames = set(["devoice","unvoice","take voice","del voice","delete voice","remove voice"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "UnVoice member in given channel, or current channel if no channel given, or command user if no member given. Format: devoice <name> <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!=Server.TYPE_IRC):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        #If 0 arguments, op user who called command.
        lineSplit = line.split()
        if(len(lineSplit)==0):
            serverObject.send("MODE "+destinationObject.getName()+" -o "+userObject.getName(),None,"raw")
            return "Voice status given."
        #If 1 argument, see if it's a channel or a user.
        if(len(lineSplit)==1):
            #If message was sent in privmsg, it's referring to a channel
            if(destinationObject is not None and destinationObject != userObject):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" -v "+userObject.getName(),None,"raw")
                return "Voice status taken."
            #If it starts with '#', check it's a channel hallo is in.
            if(line.startswith("#")):
                channel = serverObject.getChannelByName(line)
                if(channel is None or not channel.isInChannel()):
                    return "I'm not in that channel."
                #TODO: check if hallo has op in that channel.
                serverObject.send("MODE "+channel.getName()+" -v "+userObject.getName(),None,"raw")
                return "Voice status taken."
            #Check if it's a user in current channel
            targetUser = serverObject.getUserByName(line)
            if(targetUser is None or not destinationObject.isUserInChannel(targetUser)):
                return "That user is not in this channel."
            #TODO: check if hallo has op in this channel.
            serverObject.send("MODE "+destinationObject.getName()+" -v "+targetUser.getName(),None,"raw")
            return "Voice status taken."
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
        #TODO: check if hallo has op in this channel.
        serverObject.send("MODE "+targetChannel.getName()+" -v "+targetUser.getName(),None,"raw")
        return "Voice status taken."

class Invite(Function):
    '''
    IRC only, invites users to a given channel.
    '''
    #Name for use in help listing
    mHelpName = "invite"
    #Names which can be used to address the function
    mNames = set(["invite"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Invite someone to a channel"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!=Server.TYPE_IRC):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        lineSplit = line.split()
        if(len(lineSplit)==0):
            return "Please specify a person to invite and/or a channel to invite to."
        #If 1 argument, see if it's a channel or a user.
        if(len(lineSplit)==1):
            if(line.startswith("#")):
                targetChannel = serverObject.getChannelByName(line)
                if(targetChannel is None or not targetChannel.isInChannel()):
                    return "I'm not in that channel."
                serverObject.send("INVITE "+userObject.getName()+" "+targetChannel.getName(),None,"raw")
                return "Invited "+userObject.getName()+" to "+targetChannel.getName()+"."
            if(destinationObject is None or destinationObject==userObject):
                return "You can't invite a user to privmsg."
            targetUser = serverObject.getUserByName(line)
            if(targetUser is None or not targetUser.isOnline()):
                return "That user is not online."
            serverObject.send("INVITE "+targetUser.getName()+" "+destinationObject.getName())
            return "Invited "+targetUser.getName()+" to "+destinationObject.getName()+"."
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
        if(targetChannel.isUserInChannel(targetUser)):
            return "That user is already in that channel."
        #TODO: check if hallo has op in this channel.
        serverObject.send("INVITE "+targetUser.getName()+" "+targetChannel.getName(),None,"raw")
        return "Invited "+targetUser.getName()+" to "+targetChannel.getName()+"."

class Mute(Function):
    '''
    Mutes the current or a selected channel. IRC only.
    '''
    #Name for use in help listing
    mHelpName = "mute"
    #Names which can be used to address the function
    mNames = set(["mute"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Mutes a given channel or current channel. Format: mute <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #TODO: check if hallo has op.
        #Check if no arguments were provided
        if(line.strip()==""):
            targetChannel = destinationObject
            if(targetChannel is None or targetChannel==userObject):
                return "You can't set mute on a privmsg."
            serverObject.send("MODE "+targetChannel.getName()+" +m",None,"raw")
            return "Set mute."
        #Get channel from user input
        targetChannel = serverObject.getChannelByName(line.strip())
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        serverObject.send("MODE "+targetChannel.getName()+" +m",None,"raw")
        return "Set mute in "+targetChannel.getName()+"."

class UnMute(Function):
    '''
    Mutes the current or a selected channel. IRC only.
    '''
    #Name for use in help listing
    mHelpName = "unmute"
    #Names which can be used to address the function
    mNames = set(["unmute","un mute"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Unmutes a given channel or current channel if none is given. Format: unmute <channel>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #TODO: check if hallo has op.
        #Check if no arguments were provided
        if(line.strip()==""):
            targetChannel = destinationObject
            if(targetChannel is None or targetChannel==userObject):
                return "You can't set mute on a privmsg."
            serverObject.send("MODE "+targetChannel.getName()+" -m",None,"raw")
            return "Unset mute."
        #Get channel from user input
        targetChannel = serverObject.getChannelByName(line.strip())
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        serverObject.send("MODE "+targetChannel.getName()+" -m",None,"raw")
        return "Unset mute in "+targetChannel.getName()+"."

class Kick(Function):
    '''
    Kicks a specified user from a specified channel. IRC Only.
    '''
    #Name for use in help listing
    mHelpName = "kick"
    #Names which can be used to address the function
    mNames = set(["kick"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Kick given user in given channel, or current channel if no channel given."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If server isn't IRC type, we can't give op.
        if(serverObject.getType()!=Server.TYPE_IRC):
            return "This function is only available for IRC servers."
        #TODO: check if hallo has op?
        #Check input is not blank
        if(line.strip()==""):
            return "Please specify who to kick."
        #Check if 1 argument is given.
        lineSplit = line.split()
        if(len(lineSplit)==1):
            targetUser = serverObject.getUserByName(line.strip())
            if(destinationObject is None or destinationObject == userObject):
                return "I can't kick someone from a privmsg. Please specify a channel."
            if(targetUser is None or not targetUser.isOnline() or not destinationObject.isUserInChannel(targetUser)):
                return "That user isn't in this channel."
            serverObject.send("KICK "+destinationObject.getName()+" "+targetUser.getName(),None,"raw")
            return "Kicked "+targetUser.getName()+" from "+destinationObject.getName()+"."
        #Check if first argument is a channel
        if(lineSplit[0].startswith("#")):
            targetChannel = serverObject.getChannelByName(lineSplit[0])
            targetUser = serverObject.getUserByName(lineSplit[1])
            message = ""
            if(len(lineSplit)>2):
                message = " ".join(lineSplit[2:])
            if(targetChannel is None or not targetChannel.isInChannel()):
                return "I'm not in that channel."
            if(targetUser is None or not targetUser.isOnline()):
                return "That user is not online."
            if(not targetChannel.isUserInChannel(targetUser)):
                return "That user is not in that channel."
            serverObject.send("KICK "+targetChannel.getName()+" "+targetUser.getName()+" "+message,None,"raw")
            return "Kicked "+targetUser.getName()+" from "+targetChannel.getName()+"."
        #Check if second argument is a channel.
        if(lineSplit[1].startswith("#")):
            targetChannel = serverObject.getChannelByName(lineSplit[1])
            targetUser = serverObject.getUserByName(lineSplit[0])
            message = ""
            if(len(lineSplit)>2):
                message = " ".join(lineSplit[2:])
            if(targetChannel is None or not targetChannel.isInChannel()):
                return "I'm not in that channel."
            if(targetUser is None or not targetUser.isOnline()):
                return "That user is not online."
            if(not targetChannel.isUserInChannel(targetUser)):
                return "That user is not in that channel."
            serverObject.send("KICK "+targetChannel.getName()+" "+targetUser.getName()+" "+message,None,"raw")
            return "Kicked "+targetUser.getName()+" from "+targetChannel.getName()+"."
        #Otherwise, it is a user and a message.
        targetChannel = destinationObject
        targetUser = serverObject.getUserByName(lineSplit[0])
        message = ""
        if(len(lineSplit)>2):
            message = " ".join(lineSplit[2:])
        if(destinationObject is None or destinationObject == userObject):
            return "I can't kick someone from a privmsg. Please specify a channel."
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        if(targetUser is None or not targetUser.isOnline()):
            return "That user is not online."
        if(not targetChannel.isUserInChannel(targetUser)):
            return "That user is not in that channel."
        serverObject.send("KICK "+targetChannel.getName()+" "+targetUser.getName()+" "+message,None,"raw")
        return "Kicked "+targetUser.getName()+" from "+targetChannel.getName()+"."
        
class ChannelCaps(Function):
    '''
    Set caps lock for a channel.
    '''
    #Name for use in help listing
    mHelpName = "caps lock"
    #Names which can be used to address the function
    mNames = set(["caps lock","channel caps","channel caps lock","chan caps","chan caps lock","channelcapslock"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets caps lock for channel on or off."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If no arguments given, toggle caps lock in current destination
        lineClean = line.strip()
        if(lineClean==''):
            destinationObject.setUpperCase(not destinationObject.isUpperCase())
            return "Caps lock toggled."
        #If line has 1 argument, 
        lineSplit = lineClean.split()
        if(len(lineSplit)==1):
            #Check if a boolean was specified
            inputBool = Commons.stringToBool(lineSplit[0])
            if(inputBool is not None):
                destinationObject.setUpperCase(inputBool)
                return "Caps lock set "+{False: 'off', True: 'on'}[inputBool]+"."
            #Check if a channel was specified
            targetChannel = serverObject.getChannelByName(lineSplit[0])
            if(targetChannel.isInChannel()):
                targetChannel.setUpperCase(not targetChannel.isUpperCase())
                return "Caps lock togged in "+targetChannel.getName()+"."
            #Otherwise input unknown
            return "I don't understand your input, please specify a channel and whether to turn caps lock on or off."
        #Otherwise line has 2 or more arguments.
        #Check if first argument is boolean
        inputBool = Commons.stringToBool(lineSplit[0])
        targetChannelName = lineSplit[1]
        if(inputBool is None):
            inputBool = Commons.stringToBool(lineSplit[1])
            targetChannelName = lineSplit[0]
        if(inputBool is None):
            return "I don't understand your input, please specify a channel and whether to turn caps lock on or off."
        targetChannel = serverObject.getChannelByName(targetChannelName)
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        destinationObject.setUpperCase(inputBool)
        return "Caps lock set "+{False: 'off', True: 'on'}[inputBool]+" in "+targetChannel.getName()+"."

class ChannelLogging(Function):
    '''
    Set logging for a channel.
    '''
    #Name for use in help listing
    mHelpName = "logging"
    #Names which can be used to address the function
    mNames = set(["logging","channel logging","channel log","chan logging","chan log"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets or toggles logging for channel."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If no arguments given, toggle logging in current destination
        lineClean = line.strip()
        if(lineClean==''):
            destinationObject.setLogging(not destinationObject.getLogging())
            return "Logging toggled."
        #If line has 1 argument, 
        lineSplit = lineClean.strip()
        if(len(lineSplit)==1):
            #Check if a boolean was specified
            inputBool = Commons.stringToBool(lineSplit[0])
            if(inputBool is not None):
                destinationObject.setLogging(inputBool)
                return "Logging set "+{False: 'off', True: 'on'}[inputBool]+"."
            #Check if a channel was specified
            targetChannel = serverObject.getChannelByName(lineSplit[0])
            if(targetChannel.isInChannel()):
                targetChannel.setLogging(not targetChannel.getLogging())
                return "Logging togged in "+targetChannel.getName()+"."
            #Otherwise input unknown
            return "I don't understand your input, please specify a channel and whether to turn logging on or off."
        #Otherwise line has 2 or more arguments.
        #Check if first argument is boolean
        inputBool = Commons.stringToBool(lineSplit[0])
        targetChannelName = lineSplit[1]
        if(inputBool is None):
            inputBool = Commons.stringToBool(lineSplit[1])
            targetChannelName = lineSplit[0]
        if(inputBool is None):
            return "I don't understand your input, please specify a channel and whether to turn logging on or off."
        targetChannel = serverObject.getChannelByName(targetChannelName)
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        destinationObject.setLogging(inputBool)
        return "Logging set "+{False: 'off', True: 'on'}[inputBool]+" in "+targetChannel.getName()+"."

class ChannelPassiveFunctions(Function):
    '''
    Set whether passive functions are enabled in a channel.
    '''
    #Name for use in help listing
    mHelpName = "passive"
    #Names which can be used to address the function
    mNames = set(["passive"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets or toggles logging for channel."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def getNames(self):
        'Returns the list of names for directly addressing the function'
        self.mNames = set(["passive"])
        for chan in ["chan ","channel "]:
            for passive in ["passive","passive func","passive function","passive functions"]:
                self.mNames.add(chan+passive)
        return self.mNames

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If no arguments given, toggle passive functions in current destination
        lineClean = line.strip()
        if(lineClean==''):
            destinationObject.setPassiveEnabled(not destinationObject.isPassiveEnabled())
            return "Passive functions toggled."
        #If line has 1 argument, 
        lineSplit = lineClean.strip()
        if(len(lineSplit)==1):
            #Check if a boolean was specified
            inputBool = Commons.stringToBool(lineSplit[0])
            if(inputBool is not None):
                destinationObject.setPassiveEnabled(inputBool)
                return "Passive functions set "+{False: 'disabled', True: 'enabled'}[inputBool]+"."
            #Check if a channel was specified
            targetChannel = serverObject.getChannelByName(lineSplit[0])
            if(targetChannel.isInChannel()):
                targetChannel.setPassiveEnabled(not targetChannel.isPassiveEnabled())
                return "Passive functions togged in "+targetChannel.getName()+"."
            #Otherwise input unknown
            return "I don't understand your input, please specify a channel and whether to turn passive functions on or off."
        #Otherwise line has 2 or more arguments.
        #Check if first argument is boolean
        inputBool = Commons.stringToBool(lineSplit[0])
        targetChannelName = lineSplit[1]
        if(inputBool is None):
            inputBool = Commons.stringToBool(lineSplit[1])
            targetChannelName = lineSplit[0]
        if(inputBool is None):
            return "I don't understand your input, please specify a channel and whether to turn passive functions on or off."
        targetChannel = serverObject.getChannelByName(targetChannelName)
        if(targetChannel is None or not targetChannel.isInChannel()):
            return "I'm not in that channel."
        destinationObject.setPassiveEnabled(inputBool)
        return "Passive functions set "+{False: 'disabled', True: 'enabled'}[inputBool]+" in "+targetChannel.getName()+"."

class ChannelPassword(Function):
    '''
    Set password for a channel.
    '''
    #Name for use in help listing
    mHelpName = "channel password"
    #Names which can be used to address the function
    mNames = set(["channel password","chan password","channel pass","chan pass"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Sets or disables channel password."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #Get server object
        serverObject = userObject.getServer()
        #If no arguments given, turn the password for current channel off.
        lineClean = line.strip()
        if(lineClean==''):
            destinationObject.setPassword(None)
            return "Channel password disabled."
        #If line has 1 argument, set password for current channel
        lineSplit = lineClean.strip()
        if(len(lineSplit)==1):
            #Check if null was specified
            inputNull = Commons.isStringNull(lineSplit[0])
            if(inputNull):
                destinationObject.setPassword(None)
                return "Channel password disabled."
            else:
                destinationObject.setPassword(lineSplit[0])
                return "Channel password set."
        #Otherwise line has 2 or more arguments.
        #Assume first is channel, and second is password.
        inputNull = Commons.isStringNull(lineSplit[1])
        targetChannelName = lineSplit[0]
        targetChannel = serverObject.getChannelByName(targetChannelName)
        if(inputNull):
            destinationObject.setPassword(None)
            return "Channel password disabled for "+targetChannel.getName()+"."
        else:
            destinationObject.setPassword(lineSplit[1])
            return "Channel password set for "+targetChannel.getName()+"."
    








