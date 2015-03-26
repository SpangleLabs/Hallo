import time

class Commons(object):
    '''
    Class of commons methods, useful anywhere, but all static.
    '''

    @staticmethod
    def currentTimestamp():
        '''
        Constructor
        '''
        return "[{:02d}:{:02d}:{:02d}]".format(*time.gmtime()[3:6])
        