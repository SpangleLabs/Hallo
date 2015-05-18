from Function import Function
import random
import time

class Is(Function):
    '''
    A fun function which makes hallo respond to any message starting "hallo is..."
    '''
    #Name for use in help listing
    mHelpName = "is"
    #Names which can be used to address the function
    mNames = set(["is"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Placeholder. Format: is"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        return "I am?"

class Blank(Function):
    '''
    Blank function which makes hallo respond to all messages of the format "hallo"
    '''
    #Name for use in help listing
    mHelpName = ""
    #Names which can be used to address the function
    mNames = set([""])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "I wonder if this works. Format: "
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        return "Yes?"

class Alarm(Function):
    '''
    Alarm function, responds with a wooo wooo alarm.
    '''
    #Name for use in help listing
    mHelpName = "alarm"
    #Names which can be used to address the function
    mNames = set(["alarm"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Alarm. Format: alarm <subject>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        return 'woo woooooo woooooo ' + line + ' wooo wooo!'

class ArcticTerns(Function):
    '''
    Posts a link to a random image of an arctic tern.
    '''
    #Name for use in help listing
    mHelpName = "arctic tern"
    #Names which can be used to address the function
    mNames = set(["arctic tern","arctic terns","mods asleep","arctictern","arcticterns","mods"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Alarm. Format: alarm <subject>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        if(lineClean in ['nap','napping','plush']):
            number = random.randint(0,1)
            link = 'http://dr-spangle.com/AT/N0' + str(number) + '.JPG'
            return 'Plush arctic terns! ' + link
        number = random.randint(0,61)
        link = 'http://dr-spangle.com/AT/' + str(number).zfill(2) + '.JPG'
        return 'Arctic terns!! ' + link

class SlowClap(Function):
    '''
    Makes hallo do a slow clap in the current or specified channel.
    '''
    #Name for use in help listing
    mHelpName = "slowclap"
    #Names which can be used to address the function
    mNames = set(["slowclap","slow clap"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Slowclap. Format: slowclap"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        serverObject = userObject.getServer()
        if(lineClean==""):
            if(destinationObject is not None):
                serverObject.send("*clap*",destinationObject)
                time.sleep(0.5)
                serverObject.send("*clap*",destinationObject)
                time.sleep(2)
                return '*clap.*'
            else:
                return "You want me to slowclap yourself?"
        channelObject = serverObject.getChannelByName(lineClean)
        if(not channelObject.isInChannel()):
            return "I'm not in that channel."
        serverObject.send("*clap*",channelObject)
        time.sleep(0.5)
        serverObject.send("*clap*",channelObject)
        time.sleep(2)
        serverObject.send("*clap.*",channelObject)
        return "done. :)"

class Boop(Function):
    '''
    Boops people. Probably on the nose.
    '''
    #Name for use in help listing
    mHelpName = "boop"
    #Names which can be used to address the function
    mNames = set(["boop","noseboop","nose boop"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Boops people. Format: boop <name>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        'Boops people. Format: boop <name>'
        lineClean = line.strip().lower()
        if(lineClean==''):
            return "This function boops people, as such you need to specify a person for me to boop, in the form 'Hallo boop <name>' but without the <> brackets."
        #Get useful objects
        serverObject = userObject.getServer()
        #Split arguments, see how many there are.
        lineSplit = lineClean.split()
        #If one argument, check that the user is in the current channel.
        if(len(lineSplit)==1):
            destUserObject = serverObject.getUserByName(lineClean)
            if(destUserObject is None or not destUserObject.isOnline()):
                return "No one by that name is online."
            serverObject.send("\x01ACTION boops "+destUserObject.getName()+".\x01",destinationObject)
            return "Done."
        #If two arguments, see if one is a channel and the other a user.
        channelTest1 = serverObject.getChannelByName(lineSplit[0])
        if(channelTest1.isInChannel()):
            destChannel = channelTest1
            destUser = serverObject.getUserByName(lineSplit[1])
        else:
            channelTest2 = serverObject.getChannelByName(lineSplit[1])
            if(channelTest2.isInChannel()):
                destChannel = channelTest2
                destUser = serverObject.getUserByName(lineSplit[0])
            else:
                return "I'm not in any channel by that name."
        #If user by that name is not online, return a message saying that.
        if(not destUser.isOnline()):
            return "No user by that name is online."
        #Send boop, then return done.
        serverObject.send("\x01ACTION boops "+destUser.getName()+".\x01",destChannel)
        return "Done."




