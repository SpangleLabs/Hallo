from threading import Lock
from Function import Function
from inc.commons import Commons
import datetime

class Printer:
    '''
    Printing class. This is created and stored by the Hallo object.
    It exists in order to provie a single entry point to all printing to screen.
    '''
    mHallo = None
    mLock = None
    mEventDict = None

    def __init__(self,hallo):
        '''
        Constructor
        '''
        self.mHallo = hallo
        self.mLock = Lock()
        self.mEventDict = {}
        self.mEventDict[Function.EVENT_SECOND] = self.printSecond
        self.mEventDict[Function.EVENT_MINUTE] = self.printMinute
        self.mEventDict[Function.EVENT_HOUR] = self.printHour
        self.mEventDict[Function.EVENT_DAY] = self.printDay
        self.mEventDict[Function.EVENT_PING] = self.printPing
        self.mEventDict[Function.EVENT_MESSAGE] = self.printMessage
        self.mEventDict[Function.EVENT_JOIN] = self.printJoin
        self.mEventDict[Function.EVENT_LEAVE] = self.printLeave
        self.mEventDict[Function.EVENT_QUIT] = self.printQuit
        self.mEventDict[Function.EVENT_CHNAME] = self.printNameChange
        self.mEventDict[Function.EVENT_KICK] = self.printKick
        self.mEventDict[Function.EVENT_INVITE] = self.printInvite
        self.mEventDict[Function.EVENT_NOTICE] = self.printNotice
        self.mEventDict[Function.EVENT_MODE] = self.printMode
        self.mEventDict[Function.EVENT_CTCP] = self.printCtcp
    
    def output(self,event,fullLine,serverObject=None,userObject=None,channelObject=None):
        'The function which actually prints the messages.'
        #Check what type of event and pass to that to create line
        if(event not in self.mEventDict):
            return None
        printFunction = self.mEventDict[event]
        printLine = printFunction(fullLine,serverObject,userObject,channelObject)
        #Output the log line
        print(printLine)
        return None
    
    def outputFromSelf(self,event,fullLine,serverObject=None,userObject=None,channelObject=None):
        'Prints lines for messages from hallo.'
        #Check what type of event and pass to that to create line
        if(event not in self.mEventDict):
            return None
        printFunction = self.mEventDict[event]
        halloUserObject = serverObject.getUserByName(serverObject.getNick())
        printLine = printFunction(fullLine,serverObject,halloUserObject,channelObject)
        #Write the log line
        print(printLine)
        return None
    
    def printSecond(self,fullLine,serverObject,userObject,channelObject):
        return None
    
    def printMinute(self,fullLine,serverObject,userObject,channelObject):
        return None
    
    def printHour(self,fullLine,serverObject,userObject,channelObject):
        return None
    
    def printDay(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output = "Day changed: "+datetime.datetime.now().strftime("%Y-%m-%d")
        return output
    
    def printPing(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        if(userObject is None):
            output += "["+serverObject.getName()+"] PING"
        else:
            output += "["+serverObject.getName()+"] PONG"
        return output
    
    def printMessage(self,fullLine,serverObject,userObject,channelObject):
        destinationObject = channelObject
        if(channelObject==None):
            destinationObject = userObject
        output = Commons.currentTimestamp() + " "
        output += "[" +serverObject.getName()+ "] "
        output += destinationObject.getName() + " "
        output += "<" + userObject.getName() + "> " + fullLine
        return output
    
    def printJoin(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += userObject.getName() + " joined " + channelObject.getName()
        return output
    
    def printLeave(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += userObject.getName() + " left " + channelObject.getName()
        if(fullLine.strip()!=""):
            output += " (" + fullLine + ")"
        return output
    
    def printQuit(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += userObject.getNick() + " has quit."
        if(fullLine.strip()!=""):
            output += " (" + fullLine + ")"
        return output
    
    def printNameChange(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += "Nick change: " + fullLine + " -> " + userObject.getName()
        return output
    
    def printKick(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += userObject.getName() + " was kicked from " + channelObject.getName()
        if(fullLine.strip()!=""):
            output += " (" + fullLine + ")"
        return output
    
    def printInvite(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += "Invite to " + channelObject.getName() + ' from ' + userObject.getName()
        return output
    
    def printNotice(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += "Notice from " + userObject.getName() + ": " + fullLine
        return output
    
    def printModeChange(self,fullLine,serverObject,userObject,channelObject):
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += userObject.getName() + ' set ' + fullLine + ' on ' + channelObject.getName()
        return output
    
    def printCtcp(self,fullLine,serverObject,userObject,channelObject):
        #Get useful data and objects
        ctcpCommand = fullLine.split()[0]
        ctcpArguments = ' '.join(fullLine.split()[1:])
        destinationObject = channelObject
        if(channelObject==None):
            destinationObject = userObject
        #Print CTCP actions differently to other CTCP commands
        if(ctcpCommand.lower()=="action"):
            output = Commons.currentTimestamp() + " "
            output += "[" + serverObject.getName() + "] "
            output += destinationObject.getName() + " "
            output += "**" + userObject.getName() + " " + ctcpArguments + "**"
            return output
        output = Commons.currentTimestamp() + " "
        output += "[" + serverObject.getName() + "] "
        output += destinationObject.getName() + " "
        output += "<" + userObject.getName() + " (CTCP)> " + fullLine
        return output

