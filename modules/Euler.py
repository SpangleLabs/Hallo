from Function import Function
import math

class Euler(Function):
    '''
    euler project functions
    '''
    #Name for use in help listing
    mHelpName = "euler"
    #Names which can be used to address the Function
    mNames = set(["euler","euler project","project euler"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Project Euler functions. Format: \"euler list\" to list project euler solutions. \"euler <number>\" for the solution to project euler problem of the given number."
    
    mHalloObject = None
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        #Some functions might need this.
        self.mHalloObject = userObject.getServer().getHallo()
        lineClean = line.strip().lower()
        if(lineClean=="list"):
            return self.listAll()
        elif(lineClean.isdigit()):
            return self.runFunction(lineClean)
        else:
            countSolutions = len(funcName for funcName in dir(self) if funcName[:5] == 'euler' and funcName[5:].isdigit())
            outputString = "I'm learning to complete the project Euler programming problems."
            outputString += "I've not done many so far, I've only done " + str(countSolutions) + " of the 514 problems."
            outputString += "But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, "
            outputString += "say 'Hallo Euler {num}' for the answer to challenge number {num}."
            return outputString
    
    def listAll(self):
        #list all available project Euler answers
        problemFuncNames = []
        for funcName in dir(self):
            if(funcName[:5] == 'euler' and funcName[5:].isdigit()):
                problemFuncNames.append(funcName[5:])
        problemFuncNames = sorted(problemFuncNames,key=int)
        outputString = "Currently I can do Project Euler problems " 
        outputString += ', '.join(problemFuncNames[:-1]) 
        outputString += " and " + problemFuncNames[-1] + "."
        return outputString
    
    def runFunction(self,numberString):
        functionName = "euler"+numberString
        functionNames = [funcName for funcName in dir(self) if funcName[:5] == 'euler' and funcName[5:].isdigit()]
        if(functionName not in functionNames):
            return "I don't think I've solved that one yet."
        functionObject = getattr(self,functionName)
        if(not hasattr(functionObject,"__call__")):
            return "That doesn't seem to work."
        try:
            outputString = "Euler project problem " + numberString + "? I think the answer is: " + str(functionObject()) + "."
        except Exception as e:
            outputString = "Hmm, seems that one doesn't work... darnit."
            print("EULER ERROR: " + str(e))
        return outputString
    
    def euler1(self):
        threeCount = math.floor(999/3)
        fiveCount = math.floor(999/5)
        fifteenCount = math.floor(999/15)
        threeSum = 3*((0.5*(threeCount**2))+(0.5*threeCount))
        fiveSum = 5*((0.5*(fiveCount**2))+(0.5*fiveCount))
        fifteenSum = 15*((0.5*(fifteenCount**2))+(0.5*fifteenCount))
        answer = threeSum + fiveSum - fifteenSum
        return answer
    
    def euler2(self):
        previousNum = 1
        currentNum = 2
        answer = 0
        while currentNum < 4000000:
            if(currentNum % 2 == 0):
                answer = answer + currentNum
            newNum = currentNum + previousNum
            previousNum = currentNum
            currentNum = newNum
        return answer
    
    def euler3(self):
        limit = 600851475143
        factorLimit = int(math.floor(math.sqrt(limit)))
        biggestPrimeFactor = 1
        for i in range(1,factorLimit):
            if(limit%i == 0):
                checkPrime = i
                checkPrimeLimit = int(math.floor(math.sqrt(checkPrime)))
                checkPrimeFactor = 1
                for j in range(1,checkPrimeLimit):
                    if(checkPrime%j == 0):
                        checkPrimeFactor = j
                if(checkPrimeFactor == 1):
                    biggestPrimeFactor = i
        return biggestPrimeFactor
    
    def euler4(self):
        biggestPalandrome = 0
        biggestPalandromeX = 0
        biggestPalandromeY = 0
        stopLoop = 100
        for x in range(999,100,-1):
            if(x < stopLoop):
                break
            for y in range(999,x,-1):
                product = x * y
                reverseProduct = int(str(product)[::-1])
                if(product == reverseProduct and product > biggestPalandrome):
                    biggestPalandrome = product
                    biggestPalandromeX = x
                    biggestPalandromeY = y
                    stopLoop = int(math.floor(biggestPalandrome/999))
        return "answer is: " + str(biggestPalandrome) + " = " + str(biggestPalandromeX) + "x" + str(biggestPalandromeY)
    
    
    
    
    
    
    