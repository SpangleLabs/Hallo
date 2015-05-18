from Function import Function
import random

class FinnBot(Function):
    '''
    Spouts random finnishisms reminiscent of ari
    '''
    #Name for use in help listing
    mHelpName = "finnbot"
    #Names which can be used to address the function
    mNames = set(["finnbot","random finnishism"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Simulates a typical finn in conversation. Format: finnbot"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        'Simulates a typical finn in conversation. Format: finnbot'
        ariQuotes = ["|:", "After hearing you say that, I don't think we can ever be friends", "Brb, cutting down a forest", "Can't answer, I'm shaving and it'll take all day", "Can't hear you over all this atheism!", "Can this wait until after i've listened to this song 100 times on repeat?", "Could use less degrees", "Don't want to hear it, too busy complaining about the tap water", "Goony goon goon", "Hang on, I have to help some micronationalist", "Hey guys, check out my desktop: http://hallo.dr-spangle.com/DESKTOP.PNG", "If we get into a fight, I'll pick you up and run away", "I happen to be an expert on this subject", "I think I've finished constructing a hate engine", "It's about time for me to play through adom again", "It's kind of hard to type while kneeling", "I wish I could answer, but i'm busy redditing", "*lifeless stare*", "Lol, perl", "Lol, remember when i got eli to play crawl for a week?", "Needs moar haskell", "NP: Bad Religion - whatever song", "Remember that thing we were going to do? Now I don't want to do it", "Smells like Oulu", "Some Rahikkala is getting married, you are not invited", "That blows, but I cannot relate to your situation", "This somehow reminds me of my army days", "Whatever, if you'll excuse me, i'm gonna bike 50 kilometers", "You guys are things that say things", "You're under arrest for having too much fun","I have found a new favourite thing to hate"]
        #TODO: add swear filters again sometime
        #ariswearquotes = ["FUCK. FINNISH. PEOPLE!!!", "FUCK MANNERHEIM", "YOU'RE A PERSON OF SHIT"]
        #if(self.conf['server'][destination[0]]['channel'][destination[1]]['sweardetect']):
        #    for quote in ariswearquotes:
        #        ariquotes.append(quote)
        quote = random.choice(ariQuotes)
        if(quote[-1] not in ['.','?','!']):
            quote = quote + '.'
        return quote

class SilenceTheRabble(Function):
    '''
    Deops everyone except 000242 and hallo, then mutes everyone
    '''
    #Name for use in help listing
    mHelpName = "silence the rabble"
    #Names which can be used to address the function
    mNames = set(["silence the rabble","silencetherabble"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "ETD only. De-ops all but D000242 and self. Sets mute. Format: silence the rabble"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #TODO: check if not opped?
        #if('@' + self.conf['server'][destination[0]]['nick'] not in self.core['server'][destination[0]]['channel'][destination[1]]['user_list']):
        #    return 'I cannot handle it, master!'
        if(not userObject.endswith('000242')):
            return "You are not my master."
        if(destinationObject is None or destinationObject==userObject):
            return "This function can only be used in ETD."
        if(destinationObject.getName().lower() != "#ecco-the-dolphin"):
            return "This function can only be used in ETD."
        userList = destinationObject.getUserList()
        serverObject = userObject.getServer()
        for userObject in userList:
            if(userObject.getName().endswith("000242")):
                continue
            if(userObject.getName().lower()==serverObject.getNick().lower()):
                continue
            serverObject.send("MODE "+destinationObject.getName()+" -o "+userObject.getName(),None,"raw")
            serverObject.send("MODE "+destinationObject.getName()+" -v "+userObject.getName(),None,"raw")
        serverObject.send("MODE "+destinationObject.getName()+" +m",None,"raw")
        return "I have done your bidding, master."

class PokeTheAsshole(Function):
    '''
    Pokes dolphin a bunch, to see if he is awake.
    '''
    #Name for use in help listing
    mHelpName = "poke the asshole"
    #Names which can be used to address the function
    mNames = set(["poke the asshole","poketheasshole"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "ETD only. Voices and unvoices Dolphin repeatedly. Format: poke the asshole"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self,line,userObject,destinationObject=None):
        #TODO: check if not opped?
        if(not userObject.endswith('000242')):
            return "You are not my master."
        if(destinationObject is None or destinationObject==userObject):
            return "This function can only be used in ETD."
        if(destinationObject.getName().lower() != "#ecco-the-dolphin"):
            return "This function can only be used in ETD."
        if(line.strip().isdigit()):
            number = int(line.strip())
        else:
            number = 5
        serverObject = userObject.getServer()
        for _ in range(number):
            serverObject.send("MODE "+destinationObject.getName()+" +v Dolphin",None,"raw")
            serverObject.send("MODE "+destinationObject.getName()+" -v Dolphin",None,"raw")
        return 'Dolphin: You awake yet?'

