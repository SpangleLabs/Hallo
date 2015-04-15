

class Destination:
    '''
    Destination is an object that both Channel and User inherit from. It just means messages can be sent to these entities.
    '''
    mName = None

    def __init__(self,name):
        '''
        Constructor
        '''
        self.mName = name.lower()
        
    def getName(self):
        'Name getter'
        return self.mName.lower()
    
    def setName(self,name):
        'Name setter'
        self.mName = name.lower()
        
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