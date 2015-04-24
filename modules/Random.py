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

    def __init__(self, params):
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
            numDice = line.lower().split('d')[0]
            numSides = line.lower().split('d')[1]
            return self.runDiceFormat(numDice,numSides)
        elif(rangeFormatRegex.match(line)):
            rangeMin = min(line.split('-'))
            rangeMax = max(line.split('-'))
            return self.runRangeFormat(rangeMin,rangeMax)
        else:
            return "Please give input in the form of X-Y or XdY."
    
    def runDiceFormat(self,numDice,numSides):
        'Rolls numDice number of dice, each with numSides number of sides'
        pass
    
    def runRangeFormat(self,rangeMin,rangeMax):
        'Generates a random number between rangeMin and rangeMax'
        rand = random.randint(rangeMin,rangeMax)
        return "I roll "+str(rand)+"!!!"
