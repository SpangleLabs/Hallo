import re
import random

from Function import Function

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
    mHelpDocs = "Choose X, Y or Z or ... Returns one of the options separated by "or" or a comma. Format: choose <first_option>, <second_option> ... <n-1th option> or <nth option>"
    
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
    