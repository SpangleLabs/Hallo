

class Destination:
    '''
    Destination is an object that both Channel and User inherit from. It just means messages can be sent to these entities.
    '''
    mName = None

    def __init__(self,name):
        '''
        Constructor
        '''
        self.mName = name
        
        
class Channel(Destination):
    def __init__(self, params):
        '''
        Constructor
        '''
    
    
class User(Destination):
    def __init__(self, params):
        '''
        Constructor
        '''