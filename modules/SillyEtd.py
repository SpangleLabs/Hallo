from Function import Function
from inc.commons import Commons
import datetime
import math

from Server import Server


class FinnBot(Function):
    """
    Spouts random finnishisms reminiscent of ari
    """
    # Name for use in help listing
    help_name = "finnbot"
    # Names which can be used to address the function
    names = {"finnbot", "random finnishism", "aribot"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Simulates a typical finn in conversation. Format: finnbot"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """Simulates a typical finn in conversation. Format: finnbot"""
        ariQuotes = ["|:", "After hearing you say that, I don't think we can ever be friends",
                     "Brb, cutting down a forest", "Can't answer, I'm shaving and it'll take all day",
                     "Can't hear you over all this atheism!",
                     "Can this wait until after i've listened to this song 100 times on repeat?",
                     "Could use less degrees", "Don't want to hear it, too busy complaining about the tap water",
                     "Goony goon goon", "Hang on, I have to help some micronationalist",
                     "Hey guys, check out my desktop: http://hallo.dr-spangle.com/DESKTOP.PNG",
                     "If we get into a fight, I'll pick you up and run away",
                     "I happen to be an expert on this subject", "I think I've finished constructing a hate engine",
                     "It's about time for me to play through adom again", "It's kind of hard to type while kneeling",
                     "I wish I could answer, but i'm busy redditing", "*lifeless stare*", "Lol, perl",
                     "Lol, remember when i got eli to play crawl for a week?", "Needs moar haskell",
                     "NP: Bad Religion - whatever song",
                     "Remember that thing we were going to do? Now I don't want to do it", "Smells like Oulu",
                     "Some Rahikkala is getting married, you are not invited",
                     "That blows, but I cannot relate to your situation", "This somehow reminds me of my army days",
                     "Whatever, if you'll excuse me, i'm gonna bike 50 kilometers",
                     "You guys are things that say things", "You're under arrest for having too much fun",
                     "I have found a new favourite thing to hate"]
        # TODO: add swear filters again sometime
        # ariswearquotes = ["FUCK. FINNISH. PEOPLE!!!", "FUCK MANNERHEIM", "YOU'RE A PERSON OF SHIT"]
        quote = Commons.get_random_choice(ariQuotes)[0]
        if quote[-1] not in ['.', '?', '!']:
            quote += '.'
        return quote


class SilenceTheRabble(Function):
    """
    Deops everyone except 000242 and hallo, then mutes everyone
    """
    # Name for use in help listing
    help_name = "silence the rabble"
    # Names which can be used to address the function
    names = {"silence the rabble", "silencetherabble"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "ETD only. De-ops all but D000242 and self. Sets mute. Format: silence the rabble"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # TODO: check if not opped?
        # if(not opped):
        #    return 'I cannot handle it, master!'
        if not user_obj.get_name().endswith('000242'):
            return "You are not my master."
        serverObject = user_obj.get_server()
        if serverObject.get_type() == Server.TYPE_IRC:
            return "This function is only available on IRC servers."
        if destination_obj is None or destination_obj == user_obj:
            return "This function can only be used in ETD."
        if destination_obj.get_name().lower() != "#ecco-the-dolphin":
            return "This function can only be used in ETD."
        userList = destination_obj.get_user_list()
        for user_obj in userList:
            if user_obj.get_name().endswith("000242"):
                continue
            if user_obj.get_name().lower() == serverObject.get_nick().lower():
                continue
            serverObject.send("MODE " + destination_obj.get_name() + " -o " + user_obj.get_name(), None, "raw")
            serverObject.send("MODE " + destination_obj.get_name() + " -v " + user_obj.get_name(), None, "raw")
        serverObject.send("MODE " + destination_obj.get_name() + " +m", None, "raw")
        return "I have done your bidding, master."


class PokeTheAsshole(Function):
    """
    Pokes dolphin a bunch, to see if he is awake.
    """
    # Name for use in help listing
    help_name = "poke the asshole"
    # Names which can be used to address the function
    names = {"poke the asshole", "poketheasshole"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "ETD only. Voices and unvoices Dolphin repeatedly. Format: poke the asshole"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # TODO: check if not opped?
        if not user_obj.get_name().endswith('000242'):
            return "You are not my master."
        serverObject = user_obj.get_server()
        if serverObject.get_type() == Server.TYPE_IRC:
            return "This function is only available on IRC servers."
        if destination_obj is None or destination_obj == user_obj:
            return "This function can only be used in ETD."
        if destination_obj.get_name().lower() != "#ecco-the-dolphin":
            return "This function can only be used in ETD."
        # Take input, or assume input is 5
        if line.strip().isdigit():
            number = int(line.strip())
        else:
            number = 5
        for _ in range(number):
            serverObject.send("MODE " + destination_obj.get_name() + " +v Dolphin", None, "raw")
            serverObject.send("MODE " + destination_obj.get_name() + " -v Dolphin", None, "raw")
        return 'Dolphin: You awake yet?'


class Trump(Function):
    """
    Announces the years that Donald Trump will win the US elections.
    """
    # Name for use in help listing
    help_name = "trump"
    # Names which can be used to address the function
    names = {"trump", "donald trump"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Returns the election years that Donald Trump will win US election. Format: \"trump <number of terms>\""

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        lineClean = line.strip()
        try:
            numTerms = int(lineClean)
        except ValueError:
            numTerms = 4
        if numTerms > 10:
            numTerms = 10
        currentYear = datetime.date.today().year
        firstYear = math.ceil(currentYear / 4) * 4
        outputTerms = []
        for term in range(numTerms):
            electionYear = firstYear + (4 * term)
            outputTerms.append("Trump " + str(electionYear) + "!")
        output = " ".join(outputTerms) + " IMPERATOR TRUMP!"
        return output


class Corbyn(Function):
    """
    Announces the years that Jeremy Corbyn will win the UK elections.
    """
    # Name for use in help listing
    help_name = "corbyn"
    # Names which can be used to address the function
    names = {"corbyn", "jeremy corbyn"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Returns the election years that Jeremy Corbyn will win UK election." \
                "Format: \"corbyn <number of terms>\""

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        lineClean = line.strip()
        try:
            numTerms = int(lineClean)
        except ValueError:
            numTerms = 4
        if numTerms > 10:
            numTerms = 10
        currentYear = datetime.date.today().year
        firstYear = math.ceil(currentYear / 5) * 5
        outputTerms = []
        for term in range(numTerms):
            electionYear = firstYear + (5 * term)
            outputTerms.append("Corbyn " + str(electionYear) + "!")
        output = " ".join(outputTerms) + " CHAIRMAN CORBYN!"
        return output
