import time

class Commons(object):
    '''
    Class of commons methods, useful anywhere, but all static.
    '''
    mEndLine = '\r\n'

    @staticmethod
    def currentTimestamp():
        '''
        Constructor
        '''
        return "[{:02d}:{:02d}:{:02d}]".format(*time.gmtime()[3:6])

    @staticmethod    
    def chunkString(string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))
    
    @staticmethod
    def chunkStringDot(string,length):
        if(len(string)<length):
            return [string]
        else:
            listOfStrings = [string[:length-3]+'...']
            restOfString = string[length-3:]
            while(restOfString>length-3):
                listOfStrings += ['...'+restOfString[:length-6]+'...']
                restOfString = restOfString[length-6:]
            listOfStrings += ['...'+restOfString]
            return listOfStrings
    
    @staticmethod
    def readFiletoList(filename):
        f = open(filename,"r")
        fileList = []
        rawLine = f.readline()
        while rawLine != '':
            fileList.append(rawLine.replace("\n",''))
            rawLine = f.readline()
        return fileList