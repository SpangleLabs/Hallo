from Function import Function
from inc.commons import Commons

class E621(Function):
    '''
    Returns a random image from e621
    '''
    #Name for use in help listing
    mHelpName = "e621"
    #Names which can be used to address the function
    mNames = set(["e621"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random e621 result using the search you specify. Format: e621 <tags>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.replace(' ','%20')
        url = 'https://e621.net/post/index.json?tags=order:random%20score:%3E0%20'+lineClean+'%20&limit=1'
        returnList = Commons.loadUrlJson(url)
        if(len(returnList)==0):
            return "No results."
        else:
            result = returnList[0]
            link = "http://e621.net/post/show/"+str(result['id'])
            if(result['rating']=='e'):
                rating = "(Explicit)"
            elif(result['rating']=="q"):
                rating = "(Questionable)"
            elif(result['rating']=="s"):
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            lineResponse = line.replace("-rating:s","")
            return "e621 search for \""+lineResponse+"\" returned: "+link+" "+rating

class RandomPorn(Function):
    '''
    Returns a random explicit image from e621
    '''
    #Name for use in help listing
    mHelpName = "random porn"
    #Names which can be used to address the function
    mNames = set(["random porn","randomporn"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random explicit e621 result using the search you specify. Format: random porn <tags>"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        lineClean = line.replace(' ','%20')
        functionDispatcher = userObject.getServer().getHallo().getFunctionDispatcher()
        e621Class = functionDispatcher.getFunctionByName("e621")
        e621Object = functionDispatcher.getFunctionObject(e621Class)
        return e621Object.run(lineClean+"%20-rating:s",userObject,destinationObject)

class Butts(Function):
    '''
    Returns a random butt from e621
    '''
    #Name for use in help listing
    mHelpName = "butts"
    #Names which can be used to address the function
    mNames = set(["random butt","butts"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Returns a random image from e621 for the search \"butt\". Format: butts"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        functionDispatcher = userObject.getServer().getHallo().getFunctionDispatcher()
        e621Class = functionDispatcher.getFunctionByName("e621")
        e621Object = functionDispatcher.getFunctionObject(e621Class)
        return e621Object.run("butt",userObject,destinationObject)
