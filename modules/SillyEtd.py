from Destination import Channel
from Function import Function
from inc.Commons import Commons
import datetime
import math

from Server import Server


class FinnBot(Function):
    """
    Spouts random finnishisms reminiscent of ari
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "finnbot"
        # Names which can be used to address the function
        self.names = {"finnbot", "random finnishism", "aribot"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Simulates a typical finn in conversation. Format: finnbot"

    def run(self, line, user_obj, destination_obj=None):
        """Simulates a typical finn in conversation. Format: finnbot"""
        ari_quotes = ["|:", "After hearing you say that, I don't think we can ever be friends",
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
        quote = Commons.get_random_choice(ari_quotes)[0]
        if quote[-1] not in ['.', '?', '!']:
            quote += '.'
        return quote


class SilenceTheRabble(Function):
    """
    Deops everyone except 000242 and hallo, then mutes everyone
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "silence the rabble"
        # Names which can be used to address the function
        self.names = {"silence the rabble", "silencetherabble"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "ETD only. De-ops all but D000242 and self. Sets mute. Format: silence the rabble"

    def run(self, line, user_obj, destination_obj=None):
        # TODO: check if not opped?
        # if(not opped):
        #    return 'I cannot handle it, master!'
        if not user_obj.name.endswith('000242'):
            return "Error, you are not my master."
        server_obj = user_obj.get_server()
        if server_obj.get_type() == Server.TYPE_IRC:
            return "Error, this function is only available on IRC servers."
        if not isinstance(destination_obj, Channel):
            return "Error, this function can only be used in ETD."
        if destination_obj.name.lower() != "#ecco-the-dolphin":
            return "Error, this function can only be used in ETD."
        user_list = destination_obj.get_user_list()
        for user_obj in user_list:
            if user_obj.name.endswith("000242"):
                continue
            if user_obj.name.lower() == server_obj.name.lower():
                continue
            server_obj.send("MODE " + destination_obj.address + " -o " + user_obj.address, None, Server.MSG_RAW)
            server_obj.send("MODE " + destination_obj.address + " -v " + user_obj.address, None, Server.MSG_RAW)
        server_obj.send("MODE " + destination_obj.address + " +m", None, Server.MSG_RAW)
        return "I have done your bidding, master."


class PokeTheAsshole(Function):
    """
    Pokes dolphin a bunch, to see if he is awake.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "poke the asshole"
        # Names which can be used to address the function
        self.names = {"poke the asshole", "poketheasshole"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "ETD only. Voices and unvoices Dolphin repeatedly. Format: poke the asshole"

    def run(self, line, user_obj, destination_obj=None):
        # TODO: check if not opped?
        if not user_obj.name.endswith('000242'):
            return "Error, You are not my master."
        server_obj = user_obj.get_server()
        if server_obj.get_type() == Server.TYPE_IRC:
            return "Error, This function is only available on IRC servers."
        if destination_obj is None or destination_obj == user_obj:
            return "Error, This function can only be used in ETD."
        if destination_obj.name.lower() != "#ecco-the-dolphin":
            return "Error, This function can only be used in ETD."
        # Take input, or assume input is 5
        if line.strip().isdigit():
            number = int(line.strip())
        else:
            number = 5
        for _ in range(number):
            server_obj.send("MODE " + destination_obj.address + " +v Dolphin", None, Server.MSG_RAW)
            server_obj.send("MODE " + destination_obj.address + " -v Dolphin", None, Server.MSG_RAW)
        return 'Dolphin: You awake yet?'


class Trump(Function):
    """
    Announces the years that Donald Trump will win the US elections.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "trump"
        # Names which can be used to address the function
        self.names = {"trump", "donald trump"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the election years that Donald Trump will win US election. " \
                         "Format: \"trump <number of terms>\""

    def run(self, line, user_obj, destination_obj=None):
        line_clean = line.strip()
        try:
            num_terms = int(line_clean)
        except ValueError:
            num_terms = 4
        if num_terms > 10:
            num_terms = 10
        current_year = datetime.date.today().year
        first_year = math.ceil(current_year / 4) * 4
        output_terms = []
        for term in range(num_terms):
            election_year = first_year + (4 * term)
            output_terms.append("Trump " + str(election_year) + "!")
        output = " ".join(output_terms) + " IMPERATOR TRUMP!"
        return output


class Corbyn(Function):
    """
    Announces the years that Jeremy Corbyn will win the UK elections.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "corbyn"
        # Names which can be used to address the function
        self.names = {"corbyn", "jeremy corbyn"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the election years that Jeremy Corbyn will win UK election." \
                         "Format: \"corbyn <number of terms>\""

    def run(self, line, user_obj, destination_obj=None):
        line_clean = line.strip()
        try:
            num_terms = int(line_clean)
        except ValueError:
            num_terms = 4
        if num_terms > 10:
            num_terms = 10
        current_year = datetime.date.today().year
        first_year = math.ceil(current_year / 5) * 5
        output_terms = []
        for term in range(num_terms):
            election_year = first_year + (5 * term)
            output_terms.append("Corbyn " + str(election_year) + "!")
        output = " ".join(output_terms) + " CHAIRMAN CORBYN!"
        return output
