from Function import Function
from inc.commons import Commons
import math

class Hailstone(Function):
    '''
    Runs a collatz (or hailstone) function on a specified number, returning the sequence generated.
    '''
    #Name for use in help listing
    mHelpName = "hailstone"
    #Names which can be used to address the Function
    mNames = set(["hailstone","collatz","collatz sequence"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "The hailstone function has to be given with a number (to generate the collatz sequence of.)"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        'Returns the hailstone sequence for a given number. Format: hailstone <number>'
        lineClean = line.strip().lower()
        if(not lineClean.isdigit()):
            return "The hailstone function has to be given with a number (to generate the collatz sequence of.)"
        else:
            number = int(lineClean)
            sequence = self.collatzSequence([number])
            outputString = "Hailstone (Collatz) sequence for " + str(number) + ": "
            outputString += '->'.join(str(x) for x in sequence) + " (" + str(len(sequence)) + " steps.)"
            return outputString
    
    def collatzSequence(self,sequence):
        num = int(sequence[-1])
        if(num==1):
            return sequence
        elif(num%2 == 0):
            sequence.append(num//2)
            return self.collatzSequence(sequence)
        else:
            sequence.append(3*num+1)
            return self.collatzSequence(sequence)

class NumberWord(Function):
    '''
    Converts a number to the textual representation of that number.
    '''
    #Name for use in help listing
    mHelpName = "number"
    #Names which can be used to address the Function
    mNames = set(["number","number word","numberword"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns the textual representation of a given number. Format: number <number>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        if(line.count(' ')==0):
            number = line
            lang = "american"
        elif(line.split()[1].lower() in ["british","english"]):
            number = line.split()[0]
            lang = "english"
        elif(line.split()[1].lower() in ["european","french"]):
            number = line.split()[0]
            lang = "european"
        else:
            number = line.split()[0]
            lang = "american"
        if(Commons.checkNumbers(number)):
            number = number
        #TODO: implement this, once calc is transferred
#        elif(ircbot_chk.ircbot_chk.chk_msg_calc(self,number)):
#            number = mod_calc.fn_calc(self,number,client,destination)
#            if(str(number)[-1]=='.'):
#                number = number[:-1]
        else:
            return "You must enter a valid number or calculation."
        return self.numberWord(number,lang) + "."

    def numberWord(self,number,lang="american"):
        #Set up some arrays
        digits = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
        tens = ['zero','ten','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
        normalSegs = ['','thousand','million','billion','trillion','quadrillion','quintillion','sextillion','septillion','octillion','nonillion','decillion','undecillion','duodecillion','tredecillion']
        europeanSegs = ['','thousand','million','milliard','billion','billiard','trillion','trilliard','quadrillion','quadrilliard','quintillion','quintilliard','sextillion','sextilliard','septillion']
        englishSegs = ['','thousand','million','thousand million','billion','thousand billion','trillion','thousand trillion','quadrillion','thousand quadrillion','quintillion','thousand quintillion','sextillion','thousand sextillion','septillion']
        #Check for amount of decimal points
        if(number.count('.')>1):
            return "There's too many decimal points in that."
        #If there's a decimal point, write decimal parts
        elif(number.count('.')==1):
            expNumber = number.split('.')
            numberDecimal = expNumber[1]
            number = expNumber[0]
            decimal = " point"
            for num in numberDecimal:
                decimal = decimal + " " + digits[int(num)]
        else:
            decimal = ""
        #Convert number to a string, to string
        number = str(number)
        #Check if number is negative
        if(number[0]=="-"):
            number = number[1:]
            string = 'negative '
        else:
            string = ''
        #find number of segments, and justify up to a number of digits divisible by 3
        segments = int(math.ceil(float(len(number))/3)+0.01)
        number = number.rjust(3*segments,'0')
        #If number is zero, say zero.
        if(number == "000"):
            string += "zero"
        #Write out segments
        for seg in range(segments):
            start = seg*3
            end = start+3
            segment = number[start:end]
            #string = string + "(" + segment + ")"
            #Convert first number of segment
            if(segment[0]!="0"):
                string = string + digits[int(segment[0])] + " hundred "
                if(int(segment[1:]) != 0):
                    string = string + "and "
            elif(seg!=0 and int(segment[1:])!=0):
                string = string + "and "
            #Convert second and third numbers of segment
            if(int(segment[1:]) == 0):
                pass
            elif(int(segment[1:]) < 20):
                string = string + digits[int(segment[1:])]
            else:
                string = string + tens[int(segment[1])]
                if(segment[2]!="0"):
                    string = string + "-" + digits[int(segment[2])]
            #Add segment cardinal.
            if(seg!=(segments-1) and segment != "000"):
                if(lang.lower() == "american"):
                    string = string + " " + normalSegs[segments-seg-1]
                elif(lang.lower() == "english"):
                    string = string + " " + englishSegs[segments-seg-1]
                elif(lang.lower() == "european"):
                    string = string + " " + europeanSegs[segments-seg-1]
                else:
                    string = string + " " + normalSegs[segments-seg-1]
            if(seg!=(segments-1) and int(number[end:end+3])!=0):
                string = string + ', '
        #Put string together and output
        string = string + decimal
        return string








