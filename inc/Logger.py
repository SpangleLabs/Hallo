import os
from threading import Lock
import datetime
from Function import Function
from inc.commons import Commons


class Logger:
    """
    Logging class. This is created and stored by the Hallo object.
    It exists in order to provide a single entry point to all logging.
    """
    mHallo = None
    mLock = None
    mEventDict = None

    def __init__(self, hallo):
        """
        Constructor
        """
        self.mHallo = hallo
        self.mLock = Lock()
        self.mEventDict = {}
        self.mEventDict[Function.EVENT_SECOND] = self.logSecond
        self.mEventDict[Function.EVENT_MINUTE] = self.logMinute
        self.mEventDict[Function.EVENT_HOUR] = self.logHour
        self.mEventDict[Function.EVENT_DAY] = self.logDay
        self.mEventDict[Function.EVENT_PING] = self.logPing
        self.mEventDict[Function.EVENT_MESSAGE] = self.logMessage
        self.mEventDict[Function.EVENT_JOIN] = self.logJoin
        self.mEventDict[Function.EVENT_LEAVE] = self.logLeave
        self.mEventDict[Function.EVENT_QUIT] = self.logQuit
        self.mEventDict[Function.EVENT_CHNAME] = self.logNameChange
        self.mEventDict[Function.EVENT_KICK] = self.logKick
        self.mEventDict[Function.EVENT_INVITE] = self.logInvite
        self.mEventDict[Function.EVENT_NOTICE] = self.logNotice
        self.mEventDict[Function.EVENT_MODE] = self.logModeChange
        self.mEventDict[Function.EVENT_CTCP] = self.logCtcp

    def log(self, event, fullLine, serverObject=None, userObject=None, channelObject=None):
        """The function which actually writes the logs."""
        # If channel is set, check logging
        if channelObject is not None and not channelObject.get_logging():
            return None
        # If channel not set, but user is set, check their logging settings.
        if channelObject is None and userObject is not None and not userObject.get_logging():
            return None
        # Check what type of event and pass to that to create line
        if event not in self.mEventDict:
            return None
        logFunction = self.mEventDict[event]
        logLine = logFunction(fullLine, serverObject, userObject, channelObject)
        # If logLine is null, do nothing.
        if logLine is None:
            return None
        # Create file name
        fileName = self.getFileName(serverObject, userObject, channelObject)
        # Write the log line
        self.addLine(fileName, logLine)
        return None
    
    def logFromSelf(self, event, fullLine, serverObject=None, userObject=None, channelObject=None):
        """Writes a log line for a message from hallo."""
        # If channel is set, check logging
        if channelObject is not None and not channelObject.get_logging():
            return None
        # If channel not set, but user is set, check their logging settings.
        if channelObject is None and userObject is not None and not userObject.get_logging():
            return None
        # Check what type of event and pass to that to create line
        if event not in self.mEventDict:
            return None
        logFunction = self.mEventDict[event]
        halloUserObject = serverObject.get_user_by_name(serverObject.get_nick())
        logLine = logFunction(fullLine, serverObject, halloUserObject, channelObject)
        # If logLine is null, do nothing.
        if logLine is None:
            return None
        # Create file name
        fileName = self.getFileName(serverObject, userObject, channelObject)
        # Write the log line
        self.addLine(fileName, logLine)
        return None
    
    def logSecond(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def logMinute(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def logHour(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def logDay(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def logPing(self, fullLine, serverObject, userObject, channelObject):
        return None
    
    def logMessage(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += '<' + userObject.get_name() + '> ' + fullLine
        return output
    
    def logJoin(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += userObject.get_name() + " joined " + channelObject.get_name()
        return output
    
    def logLeave(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += userObject.get_name() + " left " + channelObject.get_name()
        if fullLine.strip() != "":
            output += " (" + fullLine + ")"
        return output
    
    def logQuit(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += userObject.get_name() + " has quit."
        if fullLine.strip() != "":
            output += " (" + fullLine + ")"
        return output
    
    def logNameChange(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += "Nick change: " + fullLine + " -> " + userObject.get_name()
        return output
    
    def logKick(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += userObject.get_name() + " was kicked from " + channelObject.get_name()
        if fullLine.strip() != "":
            output += " (" + fullLine + ")"
        return output
    
    def logInvite(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += "Invite to " + channelObject.get_name() + ' from ' + userObject.get_name()
        return output
    
    def logNotice(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += "Notice from " + userObject.get_name() + ": " + fullLine
        return output
    
    def logModeChange(self, fullLine, serverObject, userObject, channelObject):
        output = Commons.current_timestamp() + " "
        output += userObject.get_name() + ' set ' + fullLine + ' on ' + channelObject.get_name()
        return output
    
    def logCtcp(self, fullLine, serverObject, userObject, channelObject):
        ctcpCommand = fullLine.split()[0]
        ctcpArguments = ' '.join(fullLine.split()[1:])
        if ctcpCommand.lower() == "action":
            output = Commons.current_timestamp() + " "
            output += "**" + userObject.get_name() + ' ' + ctcpArguments + '**'
            return output
        output = Commons.current_timestamp() + " "
        output += "<" + userObject.get_name() + ' (CTCP)> ' + fullLine
        return output
    
    def getFileName(self, serverObject, userObject, channelObject):
        """Finds the file name of the file to write the log to."""
        fileName = "logs/"
        fileDate = datetime.datetime.now().strftime("%Y-%m-%d")
        fileExt = ".txt"
        # If no server specified
        if serverObject is None:
            fileName += "@/"
            fileName += fileDate+fileExt
            return fileName
        # Otherwise, go into server directory
        fileName += serverObject.get_name() + "/"
        # Check if channel object is specified
        if channelObject is None:
            if userObject is None:
                # No channel or user
                fileName += "@/"
                fileName += fileDate+fileExt
                return fileName
            # No channel, but there is a user
            fileName += userObject.get_name() + "/"
            fileName += fileDate+fileExt
            return fileName
        # Channel object is set
        fileName += channelObject.get_name() + "/"
        fileName += fileDate+fileExt
        return fileName

    def addLine(self, fileName, line):
        """Adds a new line to a specified file."""
        # Acquire thread lock
        with self.mLock:
            # Create directories if they don't exist.
            fileNameSplit = fileName.split("/")
            for fileDir in ["/".join(fileNameSplit[:x]) for x in range(1, len(fileNameSplit))]:
                try:
                    os.mkdir(fileDir)
                except:
                    pass
            # Open file and write log
            logFile = open(fileName, "a")
            logFile.write(line+"\n")
            logFile.close()
