import re
import time
import urllib.parse

from xml.dom import minidom

from Function import Function
from inc.commons import Commons


class Roll(Function):
    """
    Function to roll dice or pick random numbers in a given range
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "roll"  # Name for use in help listing
        self.names = {"roll", "dice", "random", "random number"}  # Names which can be used to address the function
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Roll X-Y returns a random number between X and Y. " \
                         "Format: \"roll <min>-<max>\" or \"roll <num>d<sides>\""

    def run(self, line, user_obj, destination_obj=None):
        """Runs the function"""
        # Check which format the input is in.
        dice_format_regex = re.compile("^[0-9]+d[0-9]+$", re.IGNORECASE)
        range_format_regex = re.compile("^[0-9]+-[0-9]+$", re.IGNORECASE)
        if dice_format_regex.match(line):
            num_dice = int(line.lower().split('d')[0])
            num_sides = int(line.lower().split('d')[1])
            return self.run_dice_format(num_dice, num_sides)
        elif range_format_regex.match(line):
            range_min = min([int(x) for x in line.split('-')])
            range_max = max([int(x) for x in line.split('-')])
            return self.run_range_format(range_min, range_max)
        else:
            return "Please give input in the form of X-Y or XdY."

    def run_dice_format(self, num_dice, num_sides):
        """Rolls numDice number of dice, each with numSides number of sides"""
        if num_dice == 0 or num_dice > 100:
            return "Invalid number of dice."
        if num_sides == 0 or num_sides > 1000000:
            return "Invalid number of sides."
        if num_dice == 1:
            rand = Commons.get_random_int(1, num_sides)[0]
            return "I roll " + str(rand) + "!!!"
        else:
            dice_rolls = Commons.get_random_int(1, num_sides, num_dice)
            output_string = "I roll "
            output_string += ", ".join([str(x) for x in dice_rolls])
            output_string += ". The total is " + str(sum(dice_rolls)) + "."
            return output_string

    def run_range_format(self, range_min, range_max):
        """Generates a random number between rangeMin and rangeMax"""
        rand = Commons.get_random_int(range_min, range_max)[0]
        return "I roll " + str(rand) + "!!!"


class Choose(Function):
    """
    Function to pick one of multiple given options
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "choose"  # Name for use in help listing
        self.names = {"choose", "pick"}  # Names which can be used to address the function
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Choose X, Y or Z or ... Returns one of the options separated by \"or\" or a comma. " \
                         "Format: choose <first_option>, <second_option> ... <n-1th option> or <nth option>"

    def run(self, line, user_obj, channel_obj=None):
        choices = re.compile(', | or ', re.IGNORECASE).split(line)
        numchoices = len(choices)
        if numchoices == 1:
            return 'Please present me with more than 1 thing to choose from!'
        else:
            rand = Commons.get_random_int(0, numchoices - 1)[0]
            choice = choices[rand]
            return 'I choose "' + choice + '".'


class EightBall(Function):
    """
    Magic 8 ball. Format: eightball
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "eightball"
        # Names which can be used to address the function
        self.names = {"eightball"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Magic 8 ball. Format: eightball"

    def run(self, line, user_obj, channel_obj=None):
        responses = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it']
        responses += ['As I see it yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes']
        responses += ['Reply hazy try again', 'Ask again later', 'Better not tell you now', 'Cannot predict now',
                      'Concentrate and ask again']
        responses += ["Don't count on it", 'My reply is no', 'My sources say no', 'Outlook not so good',
                      'Very doubtful']
        rand = Commons.get_random_int(0, len(responses) - 1)[0]
        return responses[rand] + "."

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = {"eightball"}
        for magic in ['magic ', 'magic', '']:
            for eight in ['eight', '8']:
                for space in [' ', '-', '']:
                    self.names.add(magic + eight + space + "ball")
        self.names.add(self.help_name)
        return self.names


class ChosenOne(Function):
    """
    Selects a random user from a channel
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "chosen one"
        # Names which can be used to address the function
        self.names = {"chosen one", "chosenone", "random user"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Specifies who the chosen one is. Format: chosen one"

    def run(self, line, user_obj, channel_obj=None):
        # If this command is run in privmsg, it won't work
        if channel_obj is None or channel_obj.is_user():
            return "This function can only be used in a channel"
        # Get the user list
        user_set = channel_obj.get_user_list()
        # Get list of users' names
        names_list = [userObject.get_name() for userObject in user_set]
        rand = Commons.get_random_int(0, len(names_list) - 1)[0]
        return 'It should be obvious by now that ' + names_list[rand] + ' is the chosen one.'


class Foof(Function):
    """
    FOOOOOOOOOF DOOOOOOOOOOF
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "foof"  # Name for use in help listing
        self.names = {"foof", "fooof", "foooof"}  # Names which can be used to address the function
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "FOOOOOOOOOF. Format: foof"

    def run(self, line, user_obj, destination_obj=None):
        """FOOOOOOOOOF. Format: foof"""
        rand = Commons.get_random_int(0, 60)
        if rand <= 20:
            return 'doof'
        elif rand <= 40:
            return 'doooooof'
        else:
            if rand == 40 + 15:
                server_obj = user_obj.get_server()
                server_obj.send('powering up...', destination_obj)
                time.sleep(5)
                return 'd' * 100 + 'o' * 1000 + 'f' * 200 + '!' * 50
            else:
                return 'ddddoooooooooooooooooooooffffffffff.'

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = set(['f' + 'o' * x + 'f' for x in range(2, 20)])
        self.names.add(self.help_name)
        return self.names

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        # Check if message matches any variation of foof
        if re.search(r'foo[o]*f[!]*', full_line, re.I):
            # get destination object
            destination_obj = channel_obj
            if destination_obj is None:
                destination_obj = user_obj
            # Return response
            out = self.run(full_line, user_obj, destination_obj)
            return out

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}


class ThoughtForTheDay(Function):
    """
    WH40K Thought for the day.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "thought for the day"  # Name for use in help listing
        # Names which can be used to address the function
        self.names = {"thought for the day", "thoughtfortheday", "thought of the day", "40k quote", "wh40k quote",
                      "quote 40k"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "WH40K Thought for the day. Format: thought_for_the_day"

    def run(self, line, user_obj, destination_obj=None):
        """WH40K Thought for the day. Format: thought_for_the_day"""
        thought_list = Commons.read_file_to_list('store/WH40K_ToTD2.txt')
        rand = Commons.get_random_int(0, len(thought_list) - 1)[0]
        if thought_list[rand][-1] not in ['.', '!', '?']:
            thought_list[rand] += "."
        return '"' + thought_list[rand] + '"'


class Ouija(Function):
    """
    Ouija board function. "Ouija board" is copyright Hasbro.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "ouija"
        # Names which can be used to address the function
        self.names = {"ouija", "ouija board", "random words", "message from the other side"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Ouija board function. Format: ouija <message>"

    def run(self, line, user_obj, destination_obj=None):
        word_list = Commons.read_file_to_list('store/ouija_wordlist.txt')
        rand_list = Commons.get_random_int(0, len(word_list) - 1, 4)
        num_words = (rand_list[0] % 3) + 1
        output_string = "I'm getting a message from the other side..."
        output_string += " ".join([word_list[rand_list[x + 2]] for x in range(num_words)])
        output_string += "."
        return output_string


class Scriptures(Function):
    """
    Amarr scriptures
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "scriptures"
        # Names which can be used to address the function
        self.names = {"scriptures", "amarr scriptures", "amarr"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Recites a passage from the Amarr scriptures. Format: scriptures"
        self.scripture_list = []
        self.load_from_xml()

    def load_from_xml(self):
        doc = minidom.parse("store/scriptures.xml")
        scripture_list_elem = doc.getElementsByTagName("scriptures")[0]
        for scripture_elem in scripture_list_elem.getElementsByTagName("scripture"):
            self.scripture_list.append(scripture_elem.firstChild.data)

    def run(self, line, user_obj, destination_obj=None):
        rand = Commons.get_random_int(0, len(self.scripture_list) - 1)[0]
        return self.scripture_list[rand]


class CatGif(Function):
    """
    Returns a random cat gif
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        help_name = "catgif"
        # Names which can be used to address the function
        names = {"catgif", "cat gif", "random cat", "random cat gif", "random catgif", "cat.gif"}
        # Help documentation, if it's just a single line, can be set here
        help_docs = "Returns a random cat gif Format: cat gif"

    def run(self, line, user_obj, destination_obj=None):
        api_key = user_obj.get_server().get_hallo().get_api_key("thecatapi")
        if api_key is None:
            return "No API key loaded for cat api."
        url = "http://thecatapi.com/api/images/get?format=xml&api_key=" + api_key + "&type=gif"
        xml_string = Commons.load_url_string(url)
        doc = minidom.parseString(xml_string)
        cat_url = doc.getElementsByTagName("url")[0].firstChild.data
        return cat_url


class RandomQuote(Function):
    """
    Returns a random quote
    """

    mScriptureList = []

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random quote"
        # Names which can be used to address the function
        self.names = {"random quote", "randomquote", "quote"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a quote. Format: random quote"

    def run(self, line, user_obj, destination_obj=None):
        api_key = user_obj.get_server().get_hallo().get_api_key("mashape")
        if api_key is None:
            return "No API key loaded for mashape."
        url = "https://andruxnet-random-famous-quotes.p.mashape.com/"
        # Construct headers
        headers = [["X-Mashape-Key", api_key],
                   ["Content-Type", "application/x-www-form-urlencoded"],
                   ["Accept", "application/json"]]
        # Get api response
        json_dict = Commons.load_url_json(url, headers)
        # Construct response
        quote = json_dict['quote']
        author = json_dict['author']
        output = '"' + quote + '" - ' + author
        return output


class NightValeWeather(Function):
    """
    Returns the current weather, in the style of "welcome to night vale"
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "nightvale weather"
        # Names which can be used to address the function
        self.names = {"night vale weather", "nightvale weather", "nightvale"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the current weather in the style of the podcast 'Welcome to Night Vale' " \
                         "Format: nightvale weather"
        self.hallo_obj = None

    def run(self, line, user_obj, destination_obj=None):
        # Get hallo object
        self.hallo_obj = user_obj.get_server().get_hallo()
        # Get playlist data from youtube api
        playlist_data = self.get_youtube_playlist("PL5bFd9WyHshXpZK-VPpH8UPXx6wCOIaQW")
        # Select a video from the playlist
        rand_video = Commons.get_random_choice(playlist_data)[0]
        # Return video information
        return "And now, the weather: http://youtu.be/" + rand_video['video_id'] + " " + rand_video['title']

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        line_clean = full_line.lower().strip()
        # Get hallo's current name
        hallo_name = server_obj.get_nick().lower()
        # Check if message matches specified patterns
        if hallo_name + " with the weather" in line_clean:
            # get destination object
            destination_obj = channel_obj
            if destination_obj is None:
                destination_obj = user_obj
            # Return response
            out = self.run(full_line, user_obj, destination_obj)
            return out

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def get_youtube_playlist(self, playlist_id, page_token=None):
        """Returns a list of video information for a youtube playlist."""
        list_videos = []
        # Get API key
        api_key = self.hallo_obj.get_api_key("youtube")
        if api_key is None:
            return []
        # Find API url
        api_fields = "nextPageToken,items(snippet/title,snippet/resourceId/videoId)"
        api_url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=" + \
                  playlist_id + "&fields=" + urllib.parse.quote(api_fields) + "&key=" + api_key
        if page_token is not None:
            api_url += "&pageToken=" + page_token
        # Load API response (in json).
        api_dict = Commons.load_url_json(api_url)
        for apiItem in api_dict['items']:
            new_video = {'title': apiItem['snippet']['title'], 'video_id': apiItem['snippet']['resourceId']['videoId']}
            list_videos.append(new_video)
        # Check if there's another page to add
        if "nextPageToken" in api_dict:
            list_videos.extend(self.get_youtube_playlist(playlist_id, api_dict['nextPageToken']))
        # Return list
        return list_videos


class RandomPerson(Function):
    """
    Returns a randomly generated person
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random person"
        # Names which can be used to address the function
        self.names = {"random person", "randomperson", "generate person", "generate user"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Generates and returns a random person's details. Specify \"full\" for more details. " \
                         "Format: random person"

    def run(self, line, user_obj, destination_obj=None):
        input_clean = line.strip().lower()
        url = "http://api.randomuser.me/0.6/?nat=gb&format=json"
        # Get api response
        json_dict = Commons.load_url_json(url)
        user_dict = json_dict['results'][0]['user']
        # Construct response
        name = (user_dict['name']['title'] + " " + user_dict['name']['first'] + " " + user_dict['name']['last']).title()
        email = user_dict['email']
        address = user_dict['location']['street'].title() + ", "
        address += user_dict['location']['city'].title() + ", "
        address += user_dict['location']['postcode']
        username = user_dict['username']
        password = user_dict['password']
        date_of_birth = Commons.format_unix_time(int(user_dict['dob']))
        phone_home = user_dict['phone']
        phone_mob = user_dict['cell']
        national_insurance = user_dict['NINO']
        pronoun = "he" if user_dict['gender'] == "male" else "she"
        pronoun_possessive = "his" if user_dict['gender'] == "male" else "her"
        if input_clean not in ["more", "full", "verbose", "all"]:
            output = "I have generated this person: Say hello to " + name + ". "
            output += pronoun.title() + " was born at " + date_of_birth + "."
            return output
        output = "I have generated this person: Say hello to " + name + ". "
        output += pronoun.title() + " was born at " + date_of_birth + " and lives at " + address + ". "
        output += pronoun.title() + " uses the email " + email + ", the username \"" + username + \
            "\" and usually uses the password \"" + password + "\". "
        output += pronoun_possessive.title() + " home number is " + phone_home + " but "
        output += pronoun_possessive + " mobile number is " + phone_mob + ". "
        output += pronoun_possessive + " national insurance number is " + national_insurance + "."
        return output


class NightValeProverb(Function):
    """
    Returns a random night vale proverb
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "nightvale proverb"
        # Names which can be used to address the function
        self.names = {"nightvale proverb", "night vale proverb", "random proverb", "proverb"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random proverb from Welcome to Night Vale. Format: nightvale proverb"
        self.proverb_list = []
        self.load_from_xml()

    def load_from_xml(self):
        doc = minidom.parse("store/proverbs.xml")
        proverb_list_elem = doc.getElementsByTagName("proverbs")[0]
        for proverb_elem in proverb_list_elem.getElementsByTagName("proverb"):
            self.proverb_list.append(proverb_elem.firstChild.data)

    def run(self, line, user_obj, destination_obj=None):
        rand = Commons.get_random_int(0, len(self.proverb_list) - 1)[0]
        return self.proverb_list[rand]


class RandomColour(Function):
    """
    Returns a random colour, hex code and name
    """

    mProverbList = []

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random colour"
        # Names which can be used to address the function
        self.names = {"random colour", "random color", "colour", "color"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random colour. Format: random colour"

    def run(self, line, user_obj, destination_obj=None):
        rgb_list = Commons.get_random_int(0, 256, 3)
        hex_code = (hex(rgb_list[0])[2:] + hex(rgb_list[1])[2:] + hex(rgb_list[2])[2:]).upper()
        url = "http://www.perbang.dk/rgb/" + hex_code + "/"
        url_data = Commons.load_url_string(url)
        colour_match = re.search('<meta name="Description" content="([A-Za-z ]+)#', url_data, re.M)
        if colour_match is None or colour_match.group(1) is None:
            output = "Randomly chosen colour is: #" + hex_code + " or rgb(" + str(rgb_list[0]) + "," + str(
                    rgb_list[1]) + "," + str(rgb_list[2]) + ") " + url
        else:
            colour_name = colour_match.group(1)
            output = "Randomly chosen colour is: " + colour_name + " #" + hex_code + " or rgb(" + str(
                    rgb_list[0]) + "," + str(rgb_list[1]) + "," + str(rgb_list[2]) + ") " + url
        return output
