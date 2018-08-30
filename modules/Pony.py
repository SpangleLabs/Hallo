from Events import EventMessage, EventCTCP
from Function import Function
from xml.dom import minidom

from inc.Commons import Commons


class PonyEpisode(Function):
    """
    Random pony episode function.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "pony episode"
        # Names which can be used to address the function
        self.names = {"pony episode", "ponyep", "pony ep", "mlp episode", "episode pony", "random pony episode",
                      "random mlp episode"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Chooses a pony episode to watch at random. Format: \"pony_ep\" to pick a random pony " \
                         "episode, \"pony_ep song\" to pick a random pony episode which includes a song."

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/pony/pony_episodes.xml")
        pony_episodes_list_elem = doc.getElementsByTagName("pony_episodes")[0]
        episode_list = []
        song_list = []
        # Loop through pony episodes, adding to episode_list (or song_list, if there is a song)
        for pony_episode_elem in pony_episodes_list_elem.getElementsByTagName("pony_episode"):
            episode_dict = {'name': pony_episode_elem.getElementsByTagName("name")[0].firstChild.data,
                            'full_code': pony_episode_elem.getElementsByTagName("full_code")[0].firstChild.data}
            if Commons.string_to_bool(pony_episode_elem.getElementsByTagName("song")[0].firstChild.data):
                song_list.append(episode_dict)
            episode_list.append(episode_dict)
        # If song, get episode from song list, otherwise get one from episode list
        if event.command_args.strip().lower() != "song":
            episode = Commons.get_random_choice(episode_list)[0]
        else:
            episode = Commons.get_random_choice(song_list)[0]
        # Return output
        return event.create_response("You should choose: {} - {}.".format(episode['full_code'], episode['name']))


class BestPony(Function):
    """
    Selects a pony from MLP and declares it bestpony.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "bestpony"
        # Names which can be used to address the function
        self.names = {"bestpony", "best pony", "random pony", "pony", "bestpone", "best pone", "pone"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Who is bestpony? Format: bestpony"

    def run(self, event):
        # Load XML
        doc = minidom.parse("store/pony/ponies.xml")
        pony_list_elem = doc.getElementsByTagName("ponies")[0]
        # Use the weighted list of categories to pick a category for the pony
        weighted_categories = ["mane6", "mane6", "mane6", "mane6", "mane6", "princess", "princess", "princess",
                               "princess", "cmc", "cmc", "cmc", "ponyville", "ponyville", "villain", "villain",
                               "wonderbolt", "wonderbolt", "canterlot", "cloudsdale", "foal", "hearthswarming",
                               "notapony", "other", "pet"]
        random_category = Commons.get_random_choice(weighted_categories)[0]
        pony_list = []
        # Loop through ponies, adding to pony list.
        for pony_episode_elem in pony_list_elem.getElementsByTagName("pony"):
            pony_dict = {'name': pony_episode_elem.getElementsByTagName("name")[0].firstChild.data,
                         'pronoun': pony_episode_elem.getElementsByTagName("full_code")[0].firstChild.data,
                         'categories': [category_elem.firstChild.data for category_elem in
                                        pony_episode_elem.getElementsByTagName("category")]}
            if random_category in pony_dict['categories']:
                pony_list.append(pony_dict)
        # Select the two halves of the message to display
        message_half_1 = ["Obviously {X} is best pony because ", "Well, everyone knows that {X} is bestpony, I mean ",
                          "The best pony is certainly {X}, ", "There's no debate, {X} is bestpony, ",
                          "Bestpony? You must be talking about {X}, "]
        message_half_2 = ["{Y}'s just such a distinctive character.", "{Y} really just stands out.",
                          "{Y} really makes the show worth watching for me.",
                          "{Y} stands up for what's best for everypony.", "I can really identify with that character.",
                          "I just love the colourscheme I suppose.", "I mean, why not?"]
        random_half_1 = Commons.get_random_choice(message_half_1)[0]
        random_half_2 = Commons.get_random_choice(message_half_2)[0]
        # Select a random pony, or, if it's eli, select Pinkie Pie
        chosen_pony = Commons.get_random_choice(pony_list)[0]
        if event.user.name.endswith("000242"):
            chosen_pony = {'name': "Pinkie Pie", 'pronoun': "she", 'categories': ["mane6"]}
        # Assemble and output the message
        output_message = random_half_1.replace("{X}",
                                               chosen_pony['name']) + random_half_2.replace("{Y}",
                                                                                            chosen_pony['pronoun'])
        return event.create_response(output_message)

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        clean_line = event.text.lower()
        if "who" in clean_line and ("best pony" in clean_line or "bestpony" in clean_line):
            event.split_command_text("", clean_line)
            return self.run(event)


class Cupcake(Function):
    """
    Gives out cupcakes
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "cupcake"
        # Names which can be used to address the function
        self.names = {"cupcake", "give cupcake", "give cupcake to"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>"

    def run(self, event):
        """
        Gives out cupcakes (much better than muffins.) Format: cupcake <username> <type>
        """
        if event.command_args.strip() == '':
            return event.create_response("You must specify a recipient for the cupcake.")
        # Get some required objects
        server_obj = event.server
        recipient_user_name = event.command_args.split()[0]
        recipient_user_obj = server_obj.get_user_by_name(recipient_user_name)
        # If user isn't online, I can't send a cupcake
        if not recipient_user_obj.online:
            return event.create_response("No one called {} is online.".format(recipient_user_name))
        # Generate the output message, adding cupcake type if required
        if recipient_user_name == event.command_args.strip():
            output_message = "ACTION gives {} a cupcake, from {}.".format(recipient_user_name, event.user.name)
        else:
            cupcake_type = event.command_args[len(recipient_user_name):].strip()
            output_message = "ACTION gives {} a {} cupcake, from {}.".format(recipient_user_name, cupcake_type,
                                                                                     event.user.name)
        # Get both users channel lists, and then the intersection
        user_channel_list = event.user.get_channel_list()
        recipient_channel_list = recipient_user_obj.get_channel_list()
        intersection_list = user_channel_list.intersection(recipient_channel_list)
        # If current channel is in the intersection, send there.
        if event.channel in intersection_list:
            return event.create_response(output_message)
        # Get list of channels that hallo is in inside that intersection
        valid_channels = [chan for chan in intersection_list if chan.in_channel]
        # If length of valid channel list is nonzero, pick a channel and send.
        if len(valid_channels) != 0:
            chosen_channel = Commons.get_random_choice(valid_channels)[0]
            server_obj.send(EventCTCP(server_obj, chosen_channel, None, output_message, inbound=False))
            return event.create_response("Cupcake sent.")
        # If no valid intersection channels, see if there are any valid recipient channels
        valid_channels = [chan for chan in recipient_channel_list if chan.in_channel]
        if len(valid_channels) != 0:
            chosen_channel = Commons.get_random_choice(valid_channels)[0]
            server_obj.send(EventCTCP(server_obj, chosen_channel, None, output_message, inbound=False))
            return event.create_response("Cupcake sent.")
        # Otherwise, use privmsg
        server_obj.send(EventCTCP(server_obj, None, recipient_user_obj, output_message, inbound=False))
        return event.create_response("Cupcake sent.")
