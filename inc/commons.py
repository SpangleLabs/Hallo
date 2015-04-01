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
    