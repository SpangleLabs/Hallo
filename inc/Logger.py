import os
from threading import Lock
import datetime

class Logger:
    '''
    Logging class. This is created and stored by the Hallo object.
    It exists in order to provie a single entry point to all logging.
    '''
    mLock = None

    def __init__(self, params):
        '''
        Constructor
        '''
        self.mLock = Lock()
    
    def log(self,event,fullLine,serverObject=None,userObject=None,channelObject=None):
        'The function which actually writes the logs.'
        pass
    
    def getFileName(self,serverObject,userObject,channelObject):
        'Finds the file name of the file to write the log to.'
        fileName = "logs/"#
        fileDate = datetime.datetime.now().strftime("%Y-%m-%d")
        fileExt = ".txt"
        #If no server specified
        if(serverObject is None):
            fileName += "@/"
            fileName += fileDate+fileExt
            return fileName
        #Otherwise, go into server directory
        fileName += serverObject.getName()+"/"
        #Check if channel object is specified
        if(channelObject is None):
            if(userObject is None):
                #No channel or user
                fileName += "@/"
                fileName += fileDate+fileExt
                return fileName
            #No channel, but there is a user
            fileName += userObject.getName()+"/"
            fileName += fileDate+fileExt
            return fileName
        #Channel object is set
        fileName += channelObject.getName()+"/"
        fileName += fileDate+fileExt
        return fileName

    def addLine(self,fileName,line):
        'Adds a new line to a specified file.'
        #Aquire thread lock
        with self.mLock:
            #Create directories if they don't exist.
            fileNameSplit = fileName.split("/")
            for fileDir in ["/".join(fileNameSplit[:x]) for x in range(1,len(fileNameSplit))]:
                try:
                    os.mkdir(fileDir)
                except:
                    pass
            #Open file and write log
            logFile = open(fileName,"a")
            logFile.write(line+"\n")
            logFile.close()

