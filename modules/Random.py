import re
import time
import urllib.parse

from xml.dom import minidom

from Function import Function
from inc.commons import Commons

class Roll(Function):
    '''
    Function to roll dice or pick random numbers in a given range
    '''
    mHelpName = "roll"                          #Name for use in help listing
    mNames = set(["roll","dice","random","random number"])        #Names which can be used to address the function
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Roll X-Y returns a random number between X and Y. Format: \"roll <min>-<max>\" or \"roll <num>d<sides>\""

    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def run(self,line,userObject,channelObject=None):
        'Runs the function'
        #Check which format the input is in.
        diceFormatRegex = re.compile("^[0-9]+d[0-9]+$",re.IGNORECASE)
        rangeFormatRegex = re.compile("^[0-9]+-[0-9]+$",re.IGNORECASE)
        if(diceFormatRegex.match(line)):
            numDice = int(line.lower().split('d')[0])
            numSides = int(line.lower().split('d')[1])
            return self.runDiceFormat(numDice,numSides)
        elif(rangeFormatRegex.match(line)):
            rangeMin = min([int(x) for x in line.split('-')])
            rangeMax = max([int(x) for x in line.split('-')])
            return self.runRangeFormat(rangeMin,rangeMax)
        else:
            return "Please give input in the form of X-Y or XdY."
    
    def runDiceFormat(self,numDice,numSides):
        'Rolls numDice number of dice, each with numSides number of sides'
        if(numDice==0 or numDice>100):
            return "Invalid number of dice."
        if(numSides==0 or numSides>1000000):
            return "Invalid number of sides."
        if(numDice==1):
            rand = Commons.getRandomInt(1,numSides)[0]
            return "I roll "+str(rand)+"!!!"
        else:
            diceRolls = Commons.getRandomInt(1,numSides,numDice)
            outputString = "I roll "
            outputString += ", ".join([str(x) for x in diceRolls])
            outputString += ". The total is " + str(sum(diceRolls)) + "."
            return outputString
    
    def runRangeFormat(self,rangeMin,rangeMax):
        'Generates a random number between rangeMin and rangeMax'
        rand = Commons.getRandomInt(rangeMin,rangeMax)[0]
        return "I roll "+str(rand)+"!!!"

class Choose(Function):
    '''
    Function to pick one of multiple given options
    '''
    mHelpName = "choose"                        #Name for use in help listing
    mNames = set(["choose","pick"])             #Names which can be used to address the function
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Choose X, Y or Z or ... Returns one of the options separated by \"or\" or a comma. Format: choose <first_option>, <second_option> ... <n-1th option> or <nth option>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,channelObject=None):
        choices = re.compile(', | or ',re.IGNORECASE).split(line)
        numchoices = len(choices)
        if(numchoices==1):
            return 'Please present me with more than 1 thing to choose from!'
        else:
            rand = Commons.getRandomInt(0,numchoices-1)[0]
            choice = choices[rand]
            return 'I choose "' + choice + '".'

class EightBall(Function):
    '''
    Magic 8 ball. Format: eightball
    '''
    #Name for use in help listing
    mHelpName = "eightball"
    #Names which can be used to address the function
    mNames = set(["eightball"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Magic 8 ball. Format: eightball"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,channelObject=None):
        responses = ['It is certain','It is decidedly so','Without a doubt','Yes definitely','You may rely on it']
        responses += ['As I see it yes','Most likely','Outlook good','Yes','Signs point to yes']
        responses += ['Reply hazy try again','Ask again later','Better not tell you now','Cannot predict now','Concentrate and ask again']
        responses += ["Don't count on it",'My reply is no','My sources say no','Outlook not so good','Very doubtful']
        rand = Commons.getRandomInt(0,len(responses)-1)[0]
        return responses[rand] + "."
    
    def getNames(self):
        'Returns the list of names for directly addressing the function'
        self.mNames = set(["eightball"])
        for magic in ['magic ','magic','']:
            for eight in ['eight','8']:
                for space in [' ','-','']:
                    self.mNames.add(magic+eight+space+"ball")
        self.mNames.add(self.mHelpName)
        return self.mNames

class ChosenOne(Function):
    '''
    Selects a random user from a channel
    '''
    #Name for use in help listing
    mHelpName = "chosen one"
    #Names which can be used to address the function
    mNames = set(["chosen one","chosenone","random user","random person"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Specifies who the chosen one is. Format: chosen one"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,channelObject=None):
        #If this command is run in privmsg, it won't work
        if(channelObject is None or channelObject.getType()!="channel"):
            return "This function can only be used in a channel"
        #Get the user list
        userSet = channelObject.getUserList()
        #Get list of users' names
        namesList = [userObject.getName() for userObject in userSet]
        rand = Commons.getRandomInt(0,len(namesList)-1)[0]
        return 'It should be obvious by now that ' + namesList[rand] + ' is the chosen one.'

class Foof(Function):
    '''
    FOOOOOOOOOF DOOOOOOOOOOF
    '''
    mHelpName = "foof"                        #Name for use in help listing
    mNames = set(["foof","fooof","foooof"])             #Names which can be used to address the function
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "FOOOOOOOOOF. Format: foof"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        'FOOOOOOOOOF. Format: foof'
        rand = Commons.getRandomInt(0,60)
        if(rand<=20):
            return 'doof'
        elif(rand<=40):
            return 'doooooof'
        else:
            if(rand==40+15):
                serverObject = userObject.getServer()
                serverObject.send('powering up...',destinationObject);
                time.sleep(5);
                return 'd' * 100 + 'o' * 1000 + 'f' * 200 + '!' * 50
            else:
                return 'ddddoooooooooooooooooooooffffffffff.'
    
    def getNames(self):
        'Returns the list of names for directly addressing the function'
        self.mNames = set(['f'+'o'*x+'f' for x in range(2,20)])
        self.mNames.add(self.mHelpName)
        return self.mNames
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        #Check if message matches any variation of foof
        if(re.search(r'foo[o]*f[!]*',fullLine,re.I)):
            #get destination object
            destinationObject = channelObject
            if(destinationObject is None):
                destinationObject = userObject
            #Return response
            out = self.run(fullLine,userObject,destinationObject)
            return out
    
    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set([Function.EVENT_MESSAGE])

class ThoughtForTheDay(Function):
    '''
    WH40K Thought for the day.
    '''
    mHelpName = "thought for the day"                        #Name for use in help listing
    #Names which can be used to address the function
    mNames = set(["thought for the day","thoughtfortheday","thought of the day","40k quote","wh40k quote","quote 40k"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "WH40K Thought for the day. Format: thought_for_the_day"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        'WH40K Thought for the day. Format: thought_for_the_day'
        thoughtList = Commons.readFiletoList('store/WH40K_ToTD2.txt')
        rand = Commons.getRandomInt(0,len(thoughtList)-1)[0]
        if(thoughtList[rand][-1] not in ['.','!','?']):
            thoughtList[rand] = thoughtList[rand] + "."
        return '"' + thoughtList[rand] + '"'

class Ouija(Function):
    '''
    Ouija board function. "Ouija board" is copyright Hasbro.
    '''
    #Name for use in help listing
    mHelpName = "ouija"
    #Names which can be used to address the function
    mNames = set(["ouija","ouija board","random words","message from the other side"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Ouija board function. Format: ouija <message>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        wordList = Commons.readFiletoList('store/ouija_wordlist.txt')
        randList = Commons.getRandomInt(0,len(wordList)-1,4)
        numWords = (randList[0]%3)+1
        outputString = "I'm getting a message from the other side..."
        outputString += " ".join([wordList[randList[x+2]] for x in range(numWords)])
        outputString += "."
        return outputString

class Scriptures(Function):
    '''
    Amarr scriptures
    '''
    #Name for use in help listing
    mHelpName = "scriptures"
    #Names which can be used to address the function
    mNames = set(["scriptures","amarr scriptures","amarr"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Recites a passage from the Amarr scriptures. Format: scriptures"
    
    mScriptureList = []
    
    def __init__(self):
        '''
        Constructor
        '''
        self.loadFromXml()
    
    def loadFromXml(self):
        doc = minidom.parse("store/scriptures.xml")
        scriptureListXml = doc.getElementsByTagName("scriptures")[0]
        for scriptureXml in scriptureListXml.getElementsByTagName("scripture"):
            self.mScriptureList.append(scriptureXml.firstChild.data)
    
    def run(self,line,userObject,destinationObject=None):
        rand = Commons.getRandomInt(0,len(self.mScriptureList)-1)[0]
        return self.mScriptureList[rand]

class CatGif(Function):
    '''
    Returns a random cat gif
    '''
    #Name for use in help listing
    mHelpName = "catgif"
    #Names which can be used to address the function
    mNames = set(["catgif","cat gif","random cat","random cat gif","random catgif","cat.gif"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random cat gif Format: cat gif"

    mScriptureList = []

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        apiKey = userObject.getServer().getHallo().getApiKey("thecatapi")
        if(apiKey is None):
            return "No API key loaded for cat api."
        url = "http://thecatapi.com/api/images/get?format=xml&api_key="+apiKey+"&type=gif"
        xmlString = Commons.loadUrlString(url)
        doc = minidom.parseString(xmlString)
        catUrl = doc.getElementsByTagName("url")[0].firstChild.data
        return catUrl

class RandomQuote(Function):
    '''
    Returns a random quote
    '''
    # Name for use in help listing
    mHelpName = "random quote"
    # Names which can be used to address the function
    mNames = set(["random quote","randomquote","quote"])
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a quote. Format: random quote"

    mScriptureList = []

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        apiKey = userObject.getServer().getHallo().getApiKey("mashape")
        if(apiKey is None):
            return "No API key loaded for mashape."
        url = "https://andruxnet-random-famous-quotes.p.mashape.com/"
        # Construct headers
        headers = []
        headers.append(["X-Mashape-Key", apiKey])
        headers.append(["Content-Type", "application/x-www-form-urlencoded"])
        headers.append(["Accept", "application/json"])
        # Get api response
        jsonDict = Commons.loadUrlJson(url, headers)
        # Construct response
        quote = jsonDict['quote']
        author = jsonDict['author']
        output = '"' + quote + '" - ' + author
        return output

class NightValeWeather(Function):
    '''
    Returns the current weather, in the style of "welcome to night vale"
    '''
    #Name for use in help listing
    mHelpName = "nightvale weather"
    #Names which can be used to address the function
    mNames = set(["night vale weather","nightvale weather","nightvale"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the current weather in the style of the podcast 'Welcome to Night Vale' Format: nightvale weather"
    
    mHalloObject = None
    
    def __init__(self):
        '''
        Constructor
        '''
    
    def run(self,line,userObject,destinationObject=None):
        #Get hallo object
        self.mHalloObject = userObject.getServer().getHallo()
        #Get playlist data from youtube api
        playlistData = self.getYoutubePlaylist("PL5bFd9WyHshXpZK-VPpH8UPXx6wCOIaQW")
        #Select a video from the playlist
        randVideo = Commons.getRandomChoice(playlistData)
        #Return video information
        return "And now, the weather: http://youtu.be/"+randVideo['video_id']+" "+randVideo['title']
    
    def passiveRun(self,event,fullLine,serverObject,userObject=None,channelObject=None):
        'Replies to an event not directly addressed to the bot.'
        fullLineClean = fullLine.lower().strip()
        #Get hallo's current name
        halloName = serverObject.getNick().lower()
        #Check if message matches specified patterns
        if(halloName+" with the weather" in fullLineClean):
            #get destination object
            destinationObject = channelObject
            if(destinationObject is None):
                destinationObject = userObject
            #Return response
            out = self.run(fullLine,userObject,destinationObject)
            return out
    
    def getPassiveEvents(self):
        'Returns a list of events which this function may want to respond to in a passive way'
        return set([Function.EVENT_MESSAGE])
    
    def getYoutubePlaylist(self,playlistId,pageToken=None):
        'Returns a list of video information for a youtube playlist.'
        listVideos = []
        #Get API key
        apiKey = self.mHalloObject.getApiKey("youtube")
        if(apiKey is None):
            return []
        #Find API url
        apiFields = "nextPageToken,items(snippet/title,snippet/resourceId/videoId)"
        apiUrl = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId="+playlistId+"&fields="+urllib.parse.quote(apiFields)+"&key="+apiKey
        if(pageToken is not None):
            apiUrl += "&pageToken="+pageToken
        #Load API response (in json).
        apiDict = Commons.loadUrlJson(apiUrl)
        for apiItem in apiDict['items']:
            newVideo = {}
            newVideo['title'] = apiItem['snippet']['title']
            newVideo['video_id'] = apiItem['snippet']['resourceId']['videoId']
            listVideos.append(newVideo)
        #Check if there's another page to add
        if("nextPageToken" in apiDict):
            listVideos.extend(self.getYoutubePlaylist(playlistId,apiDict['nextPageToken']))
        #Return list
        return listVideos
        
        
    
