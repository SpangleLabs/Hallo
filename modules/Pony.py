from Function import Function
from xml.dom import minidom
from inc.commons import Commons


class PonyEpisode(Function):
    """
    Random pony episode function.
    """
    # Name for use in help listing
    help_name = "pony episode"
    # Names which can be used to address the function
    names = {"pony episode", "ponyep", "pony ep", "mlp episode", "episode pony", "random pony episode",
              "random mlp episode"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Chooses a pony episode to watch at random. Format: \"pony_ep\" to pick a random pony episode, " \
                "\"pony_ep song\" to pick a random pony episode which includes a song."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Load XML
        doc = minidom.parse("store/pony/pony_episodes.xml")
        ponyEpisodesListXml = doc.getElementsByTagName("pony_episodes")[0]
        episodeList = []
        songList = []
        # Loop through pony episodes, adding to episodeList (or songList, if there is a song)
        for ponyEpisodeXml in ponyEpisodesListXml.getElementsByTagName("pony_episode"):
            episodeDict = {'name': ponyEpisodeXml.getElementsByTagName("name")[0].firstChild.data,
                           'full_code': ponyEpisodeXml.getElementsByTagName("full_code")[0].firstChild.data}
            if Commons.string_to_bool(ponyEpisodeXml.getElementsByTagName("song")[0].firstChild.data):
                songList.append(episodeDict)
            episodeList.append(episodeDict)
        # If song, get episode from song list, otherwise get one from episode list
        if line.strip().lower() != "song":
            episode = Commons.get_random_choice(episodeList)[0]
        else:
            episode = Commons.get_random_choice(songList)[0]
        # Return output
        return "You should choose: " + episode['full_code'] + " - " + episode['name'] + "."


class BestPony(Function):
    """
    Selects a pony from MLP and declares it bestpony.
    """
    # Name for use in help listing
    help_name = "bestpony"
    # Names which can be used to address the function
    names = {"bestpony", "best pony", "random pony", "pony", "bestpone", "best pone", "pone"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Who is bestpony? Format: bestpony"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Load XML
        doc = minidom.parse("store/pony/ponies.xml")
        ponyListXml = doc.getElementsByTagName("ponies")[0]
        # Use the weighted list of categories to pick a category for the pony
        weightedCategories = ["mane6", "mane6", "mane6", "mane6", "mane6", "princess", "princess", "princess",
                              "princess", "cmc", "cmc", "cmc", "ponyville", "ponyville", "villain", "villain",
                              "wonderbolt", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming",
                              "notapony", "other", "pet"]
        randomCategory = Commons.get_random_choice(weightedCategories)[0]
        ponyList = []
        # Loop through ponies, adding to pony list.
        for ponyEpisodeXml in ponyListXml.getElementsByTagName("pony"):
            ponyDict = {'name': ponyEpisodeXml.getElementsByTagName("name")[0].firstChild.data,
                        'pronoun': ponyEpisodeXml.getElementsByTagName("full_code")[0].firstChild.data,
                        'categories': [categoryXml.firstChild.data for categoryXml in
                                       ponyEpisodeXml.getElementsByTagName("category")]}
            if randomCategory in ponyDict['categories']:
                ponyList.append(ponyDict)
        # Select the two halves of the message to display
        messageHalf1 = ["Obviously {X} is best pony because ", "Well, everyone knows that {X} is bestpony, I mean ",
                        "The best pony is certainly {X}, ", "There's no debate, {X} is bestpony, ",
                        "Bestpony? You must be talking about {X}, "]
        messageHalf2 = ["{Y}'s just such a distinctive character.", "{Y} really just stands out.",
                        "{Y} really makes the show worth watching for me.",
                        "{Y} stands up for what's best for everypony.", "I can really identify with that character.",
                        "I just love the colourscheme I suppose.", "I mean, why not?"]
        randomHalf1 = Commons.get_random_choice(messageHalf1)[0]
        randomHalf2 = Commons.get_random_choice(messageHalf2)[0]
        # Select a random pony, or, if it's eli, select Pinkie Pie
        chosenPony = Commons.get_random_choice(ponyList)[0]
        if user_obj.get_name().endswith("000242"):
            chosenPony = {'name': "Pinkie Pie", 'pronoun': "she", 'categories': ["mane6"]}
        # Assemble and output the message
        outputMessage = randomHalf1.replace("{X}", chosenPony['name']) + randomHalf2.replace("{Y}",
                                                                                             chosenPony['pronoun'])
        return outputMessage

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        cleanFullLine = full_line.lower()
        if "who" in cleanFullLine and ("best pony" in cleanFullLine or "bestpony" in cleanFullLine):
            return self.run(cleanFullLine, user_obj, channel_obj)


class Cupcake(Function):
    """
    Gives out cupcakes
    """
    # Name for use in help listing
    help_name = "cupcake"
    # Names which can be used to address the function
    names = {"cupcake", "give cupcake", "give cupcake to"}
    # Help documentation, if it's just a single line, can be set here
    help_docs = "Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>"""
        if line.strip() == '':
            return "You must specify a recipient for the cupcake."
        # Get some required objects
        serverObject = user_obj.get_server()
        recipientUserName = line.split()[0]
        recipientUserObject = serverObject.get_user_by_name(recipientUserName)
        # If user isn't online, I can't send a cupcake
        if not recipientUserObject.is_online():
            return "No one called " + recipientUserName + " is online."
        # Generate the output message, adding cupcake type if required
        if recipientUserName == line.strip():
            outputMessage = "\x01ACTION gives " + recipientUserName + " a cupcake, from " + user_obj.get_name() + \
                            ".\x01"
        else:
            cupcakeType = line[len(recipientUserName):].strip()
            outputMessage = "\x01ACTION gives " + recipientUserName + " a " + cupcakeType + " cupcake, from " + \
                            user_obj.get_name() + ".\x01"
        # Get both users channel lists, and then the intersection
        userChannelList = user_obj.get_channel_list()
        recipientChannelList = recipientUserObject.get_channel_list()
        intersectionList = userChannelList.intersection(recipientChannelList)
        # If current channel is in the intersection, send there.
        if destination_obj in intersectionList:
            return outputMessage
        # Get list of channels that hallo is in inside that intersection
        validChannels = [chan for chan in intersectionList if chan.is_in_channel()]
        # If length of valid channel list is nonzero, pick a channel and send.
        if len(validChannels) != 0:
            chosenChannel = Commons.get_random_choice(validChannels)[0]
            serverObject.send(outputMessage, chosenChannel, "message")
            return "Cupcake sent."
        # If no valid intersection channels, see if there are any valid recipient channels
        validChannels = [chan for chan in recipientChannelList if chan.is_in_channel()]
        if len(validChannels) != 0:
            chosenChannel = Commons.get_random_choice(validChannels)[0]
            serverObject.send(outputMessage, chosenChannel, "message")
            return "Cupcake sent."
        # Otherwise, use privmsg
        serverObject.send(outputMessage, recipientUserObject, "message")
        return "Cupcake sent."
