import re
import random
import time

from Function import Function
from inc.commons import Commons

class Roll(Function):
    '''
    Function to roll dice or pick random numbers in a given range
    '''
    mHelpName = "roll"                          #Name for use in help listing
    mNames = set(["roll","dice","random"])        #Names which can be used to address the function
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
            rand = random.randint(1,numSides)
            return "I roll "+str(rand)+"!!!"
        else:
            diceRolls = [random.randint(1,numSides) for _ in range(numDice)]
            outputString = "I roll "
            outputString += ", ".join([str(x) for x in diceRolls])
            outputString += ". The total is " + str(sum(diceRolls)) + "."
            return outputString
    
    def runRangeFormat(self,rangeMin,rangeMax):
        'Generates a random number between rangeMin and rangeMax'
        rand = random.randint(rangeMin,rangeMax)
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
            rand = random.randint(0,numchoices-1)
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
        rand = random.randint(0,len(responses)-1)
        return responses[rand] + "."
    
    def getNames(self):
        'Returns the list of names for directly addressing the function'
        for magic in ['magic ','magic','']:
            for eight in ['eight','8']:
                for space in [' ','-','']:
                    self.mNames.add(magic+eight+space+"ball")
        return self.mNames.add(self.mHelpName)
    
class ChoosenOne(Function):
    '''
    Selects a random user from a channel
    '''
    mHelpName = "choosen one"                        #Name for use in help listing
    mNames = set(["choosen one","chosenone","random user"])             #Names which can be used to address the function
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
        rand = random.randint(0,len(namesList)-1)
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
        rand = random.randint(0,2)
        if(rand==0):
            return 'doof'
        elif(rand==1):
            return 'doooooof'
        else:
            if(random.randint(0,20)==15):
                serverObject = userObject.getServer()
                serverObject.send('powering up...',destinationObject);
                time.sleep(5);
                return 'd' * 100 + 'o' * 1000 + 'f' * 200 + '!' * 50
            else:
                return 'ddddoooooooooooooooooooooffffffffff.'
    
    def getNames(self):
        'Returns the list of names for directly addressing the function'
        self.mNames = set(['f'+'o'*x+'f' for x in range(2,20)])
        return self.mNames.add(self.mHelpName)
    
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
        return set(Function.EVENT_MESSAGE)

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
        rand = random.randint(0,len(thoughtList)-1)
        if(thoughtList[rand][-1] not in ['.','!','?']):
            thoughtList[rand] = thoughtList[rand] + "."
        return '"' + thoughtList[rand] + '"'
