from Function import Function

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