from Function import Function

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
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        lineClean = line.strip().lower()
        if(lineClean=="list"):
            return self.listAll()
        elif(lineClean.isdigit()):
            return "Project euler"
        else:
            countSolutions = len(funcName for funcName in dir(self) if funcName[:5] == 'euler' and funcName[5:].isdigit())
            outputString = "I'm learning to complete the project Euler programming problems."
            outputString += "I've not done many so far, I've only done " + str(countSolutions) + " of the 514 problems."
            outputString += "But I'm working at it... say 'Hallo Euler list' and I'll list what I've done so far, "
            outputString += "say 'Hallo Euler {num}' for the answer to challenge number {num}."
            return outputString
    
    def listAll(self):
        return
    
    def euler1(self):
        return