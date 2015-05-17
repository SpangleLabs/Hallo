from Function import Function

class Longcat(Function):
    '''
    Draws a classic longcat
    '''
    #Name for use in help listing
    mHelpName = "longcat"
    #Names which can be used to address the function
    mNames = set(["longcat"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Make a longcat! Format: longcat <length>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        'Make a longcat! Format: longcat <length>'
        try:
            longcatSegments = int(line)
        except:
            longcatSegments = 5
        longcatHead = '    /\___/\ \n   /       \ \n  |  #    # |\n  \     @   |\n   \   _|_ /\n   /       \______\n  / _______ ___   \ \n  |_____   \   \__/\n   |    \__/\n'
        longcatSegment = '   |       |\n'
        longcatTail = '   /        \ \n  /   ____   \ \n  |  /    \  |\n  | |      | |\n  /  |      |  \ \n  \__/      \__/'
        longcat = longcatHead + longcatSegment * longcatSegments + longcatTail
        longcat += '\n Longcat is L' + 'o' * longcatSegments + 'ng!'
        return longcat


