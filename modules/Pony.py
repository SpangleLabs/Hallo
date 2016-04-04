from Function import Function
from xml.dom import minidom
from inc.commons import Commons

class PonyEpisode(Function):
    '''
    Random pony episode function.
    '''
    #Name for use in help listing
    mHelpName = "pony episode"
    #Names which can be used to address the function
    mNames = set(["pony episode","ponyep","pony ep","mlp episode","episode pony","random pony episode","random mlp episode"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Chooses a pony episode to watch at random. Format: \"pony_ep\" to pick a random pony episode, \"pony_ep song\" to pick a random pony episode which includes a song."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/pony/pony_episodes.xml")
        ponyEpisodesListXml = doc.getElementsByTagName("pony_episodes")[0]
        episodeList = []
        songList = []
        #Loop through pony episodes, adding to episodeList (or songList, if there is a song)
        for ponyEpisodeXml in ponyEpisodesListXml.getElementsByTagName("pony_episode"):
            episodeDict = {}
            episodeDict['name'] = ponyEpisodeXml.getElementsByTagName("name")[0].firstChild.data
            episodeDict['full_code'] = ponyEpisodeXml.getElementsByTagName("full_code")[0].firstChild.data
            if(Commons.stringToBool(ponyEpisodeXml.getElementsByTagName("song")[0].firstChild.data)):
                songList.append(episodeDict)
            episodeList.append(episodeDict)
        #If song, get episode from song list, otherwise get one from episode list
        if(line.strip().lower()!="song"):
            episode = Commons.getRandomChoice(episodeList)[0]
        else:
            episode = Commons.getRandomChoice(songList)[0]
        #Return output
        return "You should choose: " + episode['full_code'] + " - " + episode['name'] + "."
    
class BestPony(Function):
    '''
    Selects a pony from MLP and declares it bestpony.
    '''
    #Name for use in help listing
    mHelpName = "bestpony"
    #Names which can be used to address the function
    mNames = set(["bestpony","best pony","random pony","pony","bestpone","best pone","pone"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Who is bestpony? Format: bestpony"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Load XML
        doc = minidom.parse("store/pony/ponies.xml")
        ponyListXml = doc.getElementsByTagName("ponies")[0]
        #Use the weighted list of categories to pick a category for the pony
        weightedCategories = ["mane6", "mane6", "mane6", "mane6", "mane6", "princess", "princess", "princess", "princess", "cmc", "cmc", "cmc", "ponyville", "ponyville", "villain", "villain", "wonderbolt", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming", "notapony", "other", "pet"]
        randomCategory = Commons.getRandomChoice(weightedCategories)[0]
        ponyList = []
        #Loop through ponies, adding to pony list.
        for ponyEpisodeXml in ponyListXml.getElementsByTagName("pony"):
            ponyDict = {}
            ponyDict['name'] = ponyEpisodeXml.getElementsByTagName("name")[0].firstChild.data
            ponyDict['pronoun'] = ponyEpisodeXml.getElementsByTagName("full_code")[0].firstChild.data
            ponyDict['categories'] = [categoryXml.firstChild.data for categoryXml in ponyEpisodeXml.getElementsByTagName("category")]
            if(randomCategory in ponyDict['categories']):
                ponyList.append(ponyDict)
        #Select the two halves of the message to display
        messageHalf1 = ["Obviously {X} is best pony because ", "Well, everyone knows that {X} is bestpony, I mean ", "The best pony is certainly {X}, ", "There's no debate, {X} is bestpony, ", "Bestpony? You must be talking about {X}, "]
        messageHalf2 = ["{Y}'s just such a distinctive character.", "{Y} really just stands out.", "{Y} really makes the show worth watching for me.", "{Y} stands up for what's best for everypony.", "I can really identify with that character.", "I just love the colourscheme I suppose.", "I mean, why not?"]
        randomHalf1 = Commons.getRandomChoice(messageHalf1)[0]
        randomHalf2 = Commons.getRandomChoice(messageHalf2)[0]
        #Select a random pony, or, if it's eli, select Pinkie Pie
        chosenPony = Commons.getRandomChoice(ponyList)[0]
        if(userObject.getName().endswith("000242")):
            chosenPony = {}
            chosenPony['name'] = "Pinkie Pie"
            chosenPony['pronoun'] = "she"
            chosenPony['categories'] = ["mane6"]
        #Assemble and output the message
        outputMessage = randomHalf1.replace("{X}",chosenPony['name']) + randomHalf2.replace("{Y}",chosenPony['pronoun'])
        return outputMessage
    
    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set([Function.EVENT_MESSAGE])
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        cleanFullLine = fullLine.lower()
        if("who" in cleanFullLine and ("best pony" in cleanFullLine or "bestpony" in cleanFullLine)):
            return self.run(cleanFullLine,userObject,channelObject)

class Cupcake(Function):
    '''
    Gives out cupcakes
    '''
    #Name for use in help listing
    mHelpName = "cupcake"
    #Names which can be used to address the function
    mNames = set(["cupcake","give cupcake","give cupcake to"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        'Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>'
        if(line.strip()==''):
            return "You must specify a recipient for the cupcake."
        #Get some required objects
        serverObject = userObject.getServer()
        recipientUserName = line.split()[0]
        recipientUserObject = serverObject.getUserByName(recipientUserName)
        #If user isn't online, I can't send a cupcake
        if(not recipientUserObject.isOnline()):
            return "No one called " + recipientUserName + " is online."
        #Generate the output message, adding cupcake type if required
        if(recipientUserName==line.strip()):
            outputMessage = "\x01ACTION gives " + recipientUserName + " a cupcake, from " + userObject.getName() + ".\x01"
        else:
            cupcakeType = line[len(recipientUserName):].strip()
            outputMessage = "\x01ACTION gives " + recipientUserName + " a " + cupcakeType + " cupcake, from " + userObject.getName() + ".\x01"
        #Get both users channel lists, and then the intersection
        userChannelList = userObject.getChannelList()
        recipientChannelList = recipientUserObject.getChannelList()
        intersectionList = userChannelList.intersection(recipientChannelList)
        #If current channel is in the intersection, send there.
        if(destinationObject in intersectionList):
            return outputMessage
        #Get list of channels that hallo is in inside that intersection
        validChannels = [chan for chan in intersectionList if chan.isInChannel()]
        #If length of valid channel list is nonzero, pick a channel and send.
        if(len(validChannels)!=0):
            chosenChannel = Commons.getRandomChoice(validChannels)[0]
            serverObject.send(outputMessage,chosenChannel,"message")
            return "Cupcake sent."
        #If no valid intersection channels, see if there are any valid recipient channels
        validChannels = [chan for chan in recipientChannelList if chan.isInChannel()]
        if(len(validChannels)!=0):
            chosenChannel = Commons.getRandomChoice(validChannels)[0]
            serverObject.send(outputMessage,chosenChannel,"message")
            return "Cupcake sent."
        #Otherwise, use privmsg
        serverObject.send(outputMessage,recipientUserObject,"message")
        return "Cupcake sent."
        
        
        




