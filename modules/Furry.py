import json
from threading import Lock

from Function import Function
from inc.Commons import Commons, ISO8601ParseError
import urllib.parse
from datetime import datetime
from xml.etree import ElementTree


class E621(Function):
    """
    Returns a random image from e621
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "e621"
        # Names which can be used to address the function
        self.names = {"e621"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random e621 result using the search you specify. Format: e621 <tags>"

    def run(self, line, user_obj, destination_obj=None):
        search_result = self.get_random_link_result(line)
        if search_result is None:
            return "No results."
        else:
            link = "http://e621.net/post/show/{}".format(search_result['id'])
            if search_result['rating'] == 'e':
                rating = "(Explicit)"
            elif search_result['rating'] == "q":
                rating = "(Questionable)"
            elif search_result['rating'] == "s":
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            line_response = line.strip()
            return "e621 search for \"{}\" returned: {} {}".format(line_response, link, rating)

    def get_random_link_result(self, search):
        """Gets a random link from the e621 api."""
        line_clean = search.replace(' ', '%20')
        url = "https://e621.net/post/index.json?tags=order:random%20score:%3E0%20{}%20&limit=1".format(line_clean)
        return_list = Commons.load_url_json(url)
        if len(return_list) == 0:
            return None
        else:
            result = return_list[0]
            return result


class RandomPorn(Function):
    """
    Returns a random explicit image from e621
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random porn"
        # Names which can be used to address the function
        self.names = {"random porn", "randomporn"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random explicit e621 result using the search you specify. " \
                         "Format: random porn <tags>"

    def run(self, line, user_obj, destination_obj=None):
        line_unclean = "{} -rating:s".format(line.strip())
        function_dispatcher = user_obj.server.hallo.function_dispatcher
        e621_class = function_dispatcher.get_function_by_name("e621")
        e621_obj = function_dispatcher.get_function_object(e621_class)  # type: E621
        search_result = e621_obj.get_random_link_result(line_unclean)
        if search_result is None:
            return "No results."
        else:
            link = "http://e621.net/post/show/{}".format(search_result['id'])
            if search_result['rating'] == 'e':
                rating = "(Explicit)"
            elif search_result['rating'] == "q":
                rating = "(Questionable)"
            elif search_result['rating'] == "s":
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            line_response = line.strip()
            return "e621 search for \"{}\" returned: {} {}".format(line_response, link, rating)


class Butts(Function):
    """
    Returns a random butt from e621
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "butts"
        # Names which can be used to address the function
        self.names = {"random butt", "butts", "butts!", "butts."}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random image from e621 for the search \"butt\". Format: butts"

    def run(self, line, user_obj, destination_obj=None):
        function_dispatcher = user_obj.server.hallo.function_dispatcher
        e621_class = function_dispatcher.get_function_by_name("e621")
        e621_obj = function_dispatcher.get_function_object(e621_class)  # type: E621
        search_result = e621_obj.get_random_link_result("butt")
        if search_result is None:
            return "No results."
        else:
            link = "http://e621.net/post/show/{}".format(search_result['id'])
            if search_result['rating'] == 'e':
                rating = "(Explicit)"
            elif search_result['rating'] == "q":
                rating = "(Questionable)"
            elif search_result['rating'] == "s":
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            return "e621 search for \"butt\" returned: {} {}".format(link, rating)


class Fursona(Function):
    """
    Generates a random fursona
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "fursona"
        # Names which can be used to address the function
        self.names = {"fursona", "sona", "random fursona", "random sona"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Generates your new fursona. Format: fursona"

    def run(self, line, user_obj, destination_obj=None):
        adjective = ["eldritch", "neon green", "angelic", "ghostly", "scene", "emo", "hipster", "alien", "sweaty",
                     "OBSCENELY BRIGHT YELLOW", "spotted", "hairy", "glowing", "pastel pink", "glittering blue",
                     "golden", "shimmering red", "robotic", "black", "goth", "elegant", "white", "divine", "striped",
                     "radioactive", "red and green", "slimy", "slime", "garbage", "albino", "skeleton", "petite",
                     "swamp", "aquatic", "vampire", "bright pink and yellow", "mossy", "stone", "gray", "fairy",
                     "zombie", "pastel", "mint green", "giant", "big pink", "tiny pink", "big white", "tiny white",
                     "tiny black", "translucent", "glistening", "glittering black", "shimmering white", "iridescent",
                     "glass", "silver", "jewel-encrusted", "fuschia", "purple", "tiny purple", "lilac", "lavender",
                     "shimmering lilac", "sparkling purple", "tiny blue", "heavenly", "gilded", "holy",
                     "blue and white striped", "black and orange spotted", "black and red", "black and orange",
                     "ancient", "green", "purple and blue", "pink and blue", "candy", "abyssal", "floral", "candle",
                     "melanistic", "punk", "ethereal", "unholy", "celestial", "cyan", "cream", "cream and pink",
                     "cream and brown", "yellow", "black and pink", "magenta", "speckled", "tiger-striped", "chocolate",
                     "pastel goth", "vintage", "glossy black", "glossy white", "glossy gray", "glossy blue",
                     "glossy pink", "shimmery gray", "glossy yellow", "magma", "plastic", "leucistic", "piebald"]
        animal = ["kestrel.", "goat.", "sheep.", "dragon.", "platypus.", "blobfish.", "hydra.", "wolf.", "fox.",
                  "sparkledog.", "cow.", "bull.", "cat.", "tiger.", "panther.", "hellhound.", "spider.", "beagle.",
                  "pomeranian.", "whale.", "hammerhead shark.", "snake.", "hyena.", "lamb.", "pony.", "horse.", "pup.",
                  "swan.", "pigeon.", "dove.", "fennec fox.", "fish.", "rat.", "possum.", "hamster.", "deer.", "elk.",
                  "reindeer.", "cheetah.", "ferret.", "bear.", "panda.", "koala.", "kangaroo.", "skink.", "lizard.",
                  "iguana.", "cerberus.", "turtle.", "raven.", "cardinal.", "bluejay.", "antelope.", "buffalo.",
                  "rabbit.", "bunny.", "frog.", "newt.", "salamander.", "cobra.", "coyote.", "jellyfish.", "bee.",
                  "wasp.", "dinosaur.", "bat.", "worm.", "chicken.", "eel.", "tiger.", "sloth.", "seal.", "vulture.",
                  "barghest.", "hedgehog.", "peacock.", "anglerfish.", "dolphin.", "liger.", "llama.", "alpaca.",
                  "walrus.", "mantis.", "ladybug.", "penguin.", "flamingo.", "civet.", "pudu.", "crab.", "maine coon.",
                  "fawn.", "siamese.", "amoeba.", "owl.", "unicorn.", "crocodile.", "alligator.", "chihuahua.",
                  "great dane.", "dachshund.", "corgi.", "rooster.", "sparrow.", "wyrm.", "slug.", "snail.", "seagull.",
                  "badger.", "gargoyle.", "scorpion.", "boa.", "axolotl."]
        description1 = ["it constantly drips with a tar-like black substance.",
                        "it enjoys performing occult rituals with friends.", "it is a communist.",
                        "a golden halo floats above its head.",
                        "it wears a mcdonalds uniform because it works at mcdonalds.", "it carries a nail bat.",
                        "it wears louboutin heels.", "it has two heads.", "it has an unknowable amount of eyes.",
                        "it drools constantly.", "its tongue is bright green.", "it has numerous piercings.",
                        "it is a cheerleader.", "it is a farmhand.",
                        "when you see it you are filled with an ancient fear.", "it wears a toga.",
                        "it is made of jelly.", "it has incredibly long and luxurious fur.",
                        "it uses reddit but won't admit it.",
                        "it glows softly and gently- evidence of a heavenly being.", "it is a ghost.",
                        "it dresses like a greaser.", "crystals grow from its flesh.", "it rides motorcycles.",
                        "it wears incredibly large and impractical sunglasses.", "it instagrams its starbucks drinks.",
                        "it is a hired killer.", "where its tail should be is just another head.",
                        "it dwells in a bog.", "it is wet and dripping with algae.",
                        "it runs a blog dedicated to different types of planes throughout history.",
                        "it worships the moon.", "it comes from a long line of royalty.",
                        "it frolics in flowery meadows.", "it wears a ballerina's outfit.",
                        "it wears a neutral milk hotel t-shirt with red fishnets and nothing else.",
                        "it wears a lot of eye makeup.", "it won't stop sweating.",
                        "it has far too many teeth and they are all sharp.", "it is a tattoo artist.", "it is shaking.",
                        "it is a witch.", "it wears scarves all the time.",
                        "to look into its eyes is to peer into a distant abyss.", "mushrooms grow from its skin.",
                        "its face is actually an electronic screen.",
                        "it loves to wear combat boots with cute stickers all over them.", "it comes from space.",
                        "it is a knife collector.", "it flickers in and out of this plane of reality.",
                        "it wishes it were a butt.", "its eyes are red.",
                        "it is the most beautiful thing you have ever seen.", "it loves strawberry milkshakes.",
                        "it cries all the time and can't really do much about it.",
                        "it lives alone in a dense forgotten wilderness.",
                        "it wears big christmas sweaters year-round.", "it floats about a foot off of the ground.",
                        "it loves trash.", "it has demonic wings.", "it has a cutie mark of a bar of soap.",
                        "it is melting.", "it wears opulent jewelry of gold and gemstones.", "it has a hoard of bones.",
                        "it has ram horns.", "it has a forked tongue.", "it wears frilly dresses.", "it has antlers.",
                        "it is a nature spirit.", "its back is covered in candles which flicker ominously.",
                        "it wears a leather jacket with lots of patches.", "it wears a snapback.",
                        "it has a tattoo that says 'yolo'.", "electricity flickers through the air surrounding it.",
                        "it is a fire elemental.", "it consumes only blood.", "it works at an adorable tiny bakery.",
                        "it is a professional wrestler.", "instead of eyes there are just more ears.",
                        "it speaks a forgotten and ancient language both disturbing and enchanting to mortal ears.",
                        "it works out.", "it wishes it were a tree.", "it is always blushing.",
                        "it uses ancient and powerful magic.", "it loves raw meat.", "it is always smiling.",
                        "it can fire lasers from its eyes.", "a small rainbutt follows it everywhere.",
                        "it is made of glass.", "fireflies circle it constantly.",
                        "it is always accompanied by glowing orbs of light.", "it has human legs.",
                        "water drips from it constantly.", "it has golden horns.", "it loves gore.",
                        "it lives in a cave with its parents.", "its purse costs more than most people's cars.",
                        "it always shivers even when it's not cold.", "it has tentacles.", "it never blinks.",
                        "it only listens to metal.", "it wears a golden crown.", "it wears a white sundress.",
                        "it has green hair pulled up into two buns.",
                        "its body is covered in occult sigils and runes which pulse ominously.",
                        "it loves to devour the rotting plant matter covering the forest floor.",
                        "it wears a plain white mask.", "its eyes flash multiple colors rapidly.",
                        "it loves to wear nail polish but applies it messily.", "it runs a jimmy carter fanblog.",
                        "it is a surfer.", "it only wears hawaiian shirts.",
                        "everything it wears is made out of denim.", "it has long braided hair.",
                        "it calls everybody comrade.", "it lures men to their deaths with its beautiful voice.",
                        "it has braces.", "it has full sleeve tattoos.", "it dresses like a grandpa.",
                        "smoke pours from its mouth.", "it is a makeup artist.", "it dresses like a pinup girl.",
                        "it has only one large eye.", "it plays the harp.",
                        "it has very long hair with many flowers in it.", "it has a cyan buzzcut.",
                        "it is a garden spirit.", "it has fangs capable of injecting venom.",
                        "numerous eyeballs float around it. watching. waiting.", "it loves to play in the mud.",
                        "it wears a surgical mask.",
                        "its eyes are pitch black and cause those who look directly into them for too long to "
                        "slowly grow older.",
                        "it wears numerous cute hairclips.", "it has a very large tattoo of the 'blockbuster' logo.",
                        "it is constantly covered in honey that drips on everything and pools beneath it.",
                        "it wears a cherry-themed outfit.", "it has heterochromia.", "it is heavily scarred.",
                        "in place of a head it has a floating cube that glows and pulses softly.",
                        "it seems to be glitching.", "it does not have organs- instead it is full of flowers.",
                        "its insides are glowing.", "it is a skateboarder.", "it is a superwholock blogger.",
                        "it is a skilled glass-blower.", "it has a pet of the same species as itself.",
                        "it is the leader of an association of villains.", "it wears a black leather outfit.",
                        "its pupils are slits.", "it wears a crop top with the word OATMEAL in all caps.",
                        "it only wears crop tops and high waisted shorts.",
                        "it is always giving everyone a suspicious look.", "it has a septum piercing.",
                        "instead of talking it just says numbers.", "it is an internet famous scene queen.",
                        "its eyes are way too big to be normal.", "it has super obvious tan lines.",
                        "it wears a maid outfit.", "it is an emissary from hell.",
                        "its eyes have multiple pupils in them.", "it has an impractically large sword.",
                        "it is a magical girl.", "it has a scorpion tail.",
                        "it is a biologist specializing in marine invertebrates.", "it runs. everywhere. all the time.",
                        "it is an esteemed fashion designer for beings with 6 or more limbs.",
                        "it wears short shorts that say CLAM.", "it can't stop knitting.",
                        "it is always coated in glitter.", "it worships powerful dolphin deities.",
                        "it has slicked back hair.", "it has a thick beard.",
                        "it has a long braided beard plaited with ribbons.", "it is a viking.", "it wears a parka.",
                        "its outfit is completely holographic.", "it wears an oversized pearl necklace.",
                        "it has stubble.", "it carries a cellphone with a ridiculous amount of charms and keychains.",
                        "it wears crocs.", "it has a hoard of gems and gold that was pillaged from innocent villagers.",
                        "it robs banks.", "its facial features are constantly shifting.",
                        "it works as a librarian in hell.", "it wears a fedora."]
        description2 = ["it constantly drips with a tar-like black substance.",
                        "it enjoys performing occult rituals with friends.", "it is a communist.",
                        "a golden halo floats above its head.",
                        "it wears a mcdonalds uniform because it works at mcdonalds.", "it carries a nail bat.",
                        "it wears louboutin heels.", "it has two heads.", "it has an unknowable amount of eyes.",
                        "it drools constantly.", "its tongue is bright green.", "it has numerous piercings.",
                        "it is a cheerleader.", "it is a farmhand.",
                        "when you see it you are filled with an ancient fear.", "it wears a toga.",
                        "it is made of jelly.", "it has incredibly long and luxurious fur.",
                        "it uses reddit but won't admit it.",
                        "it glows softly and gently- evidence of a heavenly being.", "it is a ghost.",
                        "it dresses like a greaser.", "crystals grow from its flesh.", "it rides motorcycles.",
                        "it wears incredibly large and impractical sunglasses.", "it instagrams its starbucks drinks.",
                        "it is a hired killer.", "where its tail should be is just another head.",
                        "it dwells in a bog.", "it is wet and dripping with algae.",
                        "it runs a blog dedicated to different types of planes throughout history.",
                        "it worships the moon.", "it comes from a long line of royalty.",
                        "it frolics in flowery meadows.", "it wears a ballerina's outfit.",
                        "it wears a neutral milk hotel t-shirt with red fishnets and nothing else.",
                        "it wears a lot of eye makeup.", "it won't stop sweating.",
                        "it has far too many teeth and they are all sharp.", "it is a tattoo artist.", "it is shaking.",
                        "it is a witch.", "it wears scarves all the time.",
                        "to look into its eyes is to peer into a distant abyss.", "mushrooms grow from its skin.",
                        "its face is actually an electronic screen.",
                        "it loves to wear combat boots with cute stickers all over them.", "it comes from space.",
                        "it is a knife collector.", "it flickers in and out of this plane of reality.",
                        "it wishes it were a butt.", "its eyes are red.",
                        "it is the most beautiful thing you have ever seen.", "it loves strawberry milkshakes.",
                        "it cries all the time and can't really do much about it.",
                        "it lives alone in a dense forgotten wilderness.",
                        "it wears big christmas sweaters year-round.", "it floats about a foot off of the ground.",
                        "it loves trash.", "it has demonic wings.", "it has a cutie mark of a bar of soap.",
                        "it is melting.", "it wears opulent jewelry of gold and gemstones.", "it has a hoard of bones.",
                        "it has ram horns.", "it has a forked tongue.", "it wears frilly dresses.", "it has antlers.",
                        "it is a nature spirit.", "its back is covered in candles which flicker ominously.",
                        "it wears a leather jacket with lots of patches.", "it wears a snapback.",
                        "it has a tattoo that says 'yolo'.", "electricity flickers through the air surrounding it.",
                        "it is a fire elemental.", "it consumes only blood.", "it works at an adorable tiny bakery.",
                        "it is a professional wrestler.", "instead of eyes there are just more ears.",
                        "it speaks a forgotten and ancient language both disturbing and enchanting to mortal ears.",
                        "it works out.", "it wishes it were a tree.", "it is always blushing.",
                        "it uses ancient and powerful magic.", "it loves raw meat.", "it is always smiling.",
                        "it can fire lasers from its eyes.", "a small rainbutt follows it everywhere.",
                        "it is made of glass.", "fireflies circle it constantly.",
                        "it is always accompanied by glowing orbs of light.", "it has human legs.",
                        "water drips from it constantly.", "it has golden horns.", "why is it always covered in blood?",
                        "it loves gore.", "it lives in a cave with its parents.",
                        "its purse costs more than most people's cars.", "it always shivers even when it's not cold.",
                        "it has tentacles.", "it never blinks.", "it only listens to metal.",
                        "it wears a golden crown.", "it wears a white sundress.",
                        "it has green hair pulled up into two buns.",
                        "its body is covered in occult sigils and runes which pulse ominously.",
                        "it loves to devour the rotting plant matter covering the forest floor.",
                        "it wears a plain white mask.", "its eyes flash multiple colors rapidly.", "you are afraid.",
                        "it loves to wear nail polish but applies it messily.", "it runs a jimmy carter fanblog.",
                        "it is a surfer.", "it only wears hawaiian shirts.",
                        "everything it wears is made out of denim.", "it has long braided hair.",
                        "it calls everybody comrade.", "it lures men to their deaths with its beautiful voice.",
                        "it has braces.", "it has full sleeve tattoos.", "it dresses like a grandpa.",
                        "smoke pours from its mouth.", "it is a makeup artist.", "it dresses like a pinup girl.",
                        "it has only one large eye.", "it plays the harp.",
                        "it has very long hair with many flowers in it.", "it has a cyan buzzcut.",
                        "it is a garden spirit.", "it has fangs capable of injecting venom.",
                        "numerous eyeballs float around it. watching. waiting.", "it loves to play in the mud.",
                        "it wears a surgical mask.",
                        "its eyes are pitch black and cause those who look directly into them for too long to "
                        "slowly grow older.",
                        "it wears numerous cute hairclips.", "it has a very large tattoo of the 'blockbuster' logo.",
                        "it is constantly covered in honey that drips on everything and pools beneath it.",
                        "it wears a cherry-themed outfit.", "it has heterochromia.", "it is heavily scarred.",
                        "in place of a head it has a floating cube that glows and pulses softly.",
                        "it seems to be glitching.", "its insides are glowing.",
                        "it does not have organs- instead it is full of flowers.", "it is a skateboarder.",
                        "it is a superwholock blogger.", "it is a skilled glass-blower.",
                        "it has a pet of the same species as itself.",
                        "it is the leader of an association of villains.", "it wears a black leather outfit.",
                        "its pupils are slits..", "it wears a crop top with the word OATMEAL in all caps.",
                        "it only wears crop tops and high waisted shorts.",
                        "it is always giving everyone a suspicious look.", "it has a septum piercing.",
                        "its hair is beehive style. not an actual beehive.", "instead of talking it just says numbers.",
                        "it has a halo. over its ass.", "it is an internet famous scene queen.",
                        "its eyes are way too big to be normal.", "it has super obvious tan lines.",
                        "it wears a maid outfit.", "it is an emissary from hell.",
                        "its eyes have multiple pupils in them.", "there are scorpions everywhere.",
                        "it has an impractically large sword.", "it is a magical girl.", "it has a scorpion tail.",
                        "it is a biologist specializing in marine invertebrates.", "it runs. everywhere. all the time.",
                        "it is an esteemed fashion designer for beings with 6 or more limbs.",
                        "it wears short shorts that say CLAM.", "it can't stop knitting.",
                        "it is always coated in glitter.", "it worships powerful dolphin deities.",
                        "it has slicked back hair.", "it has a thick beard.",
                        "it has a long braided beard plaited with ribbons.", "it is a viking.", "it wears a parka.",
                        "its outfit is completely holographic.", "it wears an oversized pearl necklace.",
                        "it has stubble.", "it carries a cellphone with a ridiculous amount of charms and keychains.",
                        "Welcome to Hell! Welcome to Hell!", "it wears crocs.",
                        "it has a hoard of gems and gold that was pillaged from innocent villagers.",
                        "it robs banks and its partner in crime is the next fursona you generate.",
                        "its facial features are constantly shifting.", "it works as a librarian in hell.",
                        "it wears a fedora."]
        result = "Your new fursona is: {} {} {} {}".format(Commons.get_random_choice(adjective)[0],
                                                           Commons.get_random_choice(animal)[0],
                                                           Commons.get_random_choice(description1)[0],
                                                           Commons.get_random_choice(description2)[0])
        return result


class E621Sub:
    """
    Class representing a subscription to an E621 Search
    """

    def __init__(self):
        self.search = ""
        self.server_name = None
        self.channel_address = None
        self.user_address = None
        self.latest_ten_ids = []
        self.last_check = None
        self.update_frequency = None

    def check_subscription(self):
        """
        Checks the search for any updates
        :return: List of new results
        """
        search = "{} order:-id".format(self.search)  # Sort by id
        if len(self.latest_ten_ids) > 0:
            oldest_id = min(self.latest_ten_ids)
            search += " id:>{}".format(oldest_id)  # Don't list anything older than the oldest of the last 10
        url = "http://e621.net/post/index.json?tags={}&limit=50".format(urllib.parse.quote(search))
        results = Commons.load_url_json(url)
        return_list = []
        new_last_ten = set(self.latest_ten_ids)
        for result in results:
            result_id = result["id"]
            # Create new list of latest ten results
            new_last_ten.add(result_id)
            # If post hasn't been seen in the latest ten, add it to returned list.
            if result_id not in self.latest_ten_ids:
                return_list.append(result)
        self.latest_ten_ids = sorted(list(new_last_ten))[::-1][:10]
        # Update check time
        self.last_check = datetime.now()
        return return_list

    def output_item(self, e621_result, hallo, server=None, destination=None):
        """
        Outputs an item to a given server and destination, or the feed default.
        :param e621_result: dict e621 JSON result to output
        :param hallo: Hallo
        :param server: Server
        :param destination: Destination
        """
        # Get server
        if server is None:
            server = hallo.get_server_by_name(self.server_name)
            if server is None:
                return "Error, invalid server."
        # Get destination
        if destination is None:
            if self.channel_address is not None:
                destination = server.get_channel_by_address(self.channel_address, None)
            if self.user_address is not None:
                destination = server.get_user_by_address(self.user_address, None)
            if destination is None:
                return "Error, invalid destination."
        # Construct output
        output = self.format_item(e621_result)
        server.send(output, destination)
        return output

    def format_item(self, e621_result):
        """
        Formats an e621 result for output.
        :param e621_result: e621 result to format
        :type e621_result: dict
        :return: Readable format of the result
        :rtype: str
        """
        link = "http://e621.net/post/show/{}".format(e621_result['id'])
        # Create rating string
        if e621_result['rating'] == 'e':
            rating = "(Explicit)"
        elif e621_result['rating'] == "q":
            rating = "(Questionable)"
        elif e621_result['rating'] == "s":
            rating = "(Safe)"
        else:
            rating = "(Unknown)"
        # Construct output
        output = "Update on \"{}\" e621 search. {} {}".format(self.search, link, rating)
        return output

    def needs_check(self):
        """
        Returns whether an e621 subscription check is overdue.
        :return: bool
        """
        if self.last_check is None:
            return True
        if datetime.now() > self.last_check + self.update_frequency:
            return True
        return False

    def to_xml_string(self):
        """
        Saves this E621 subscription
        :rtype: str
        """
        # Create root element
        root = ElementTree.Element("e621_sub")
        # Create search element
        search = ElementTree.SubElement(root, "search")
        search.text = self.search
        # Create server name element
        server = ElementTree.SubElement(root, "server")
        server.text = self.server_name
        # Create channel name element, if applicable
        if self.channel_address is not None:
            channel = ElementTree.SubElement(root, "channel")
            channel.text = self.channel_address
        # Create user name element, if applicable
        if self.user_address is not None:
            user = ElementTree.SubElement(root, "user")
            user.text = self.user_address
        # Create latest id elements
        for latest_id in self.latest_ten_ids:
            latest_id_elem = ElementTree.SubElement(root, "latest_id")
            latest_id_elem.text = str(latest_id)
        # Create last check element
        if self.last_check is not None:
            last_check = ElementTree.SubElement(root, "last_check")
            last_check.text = self.last_check.isoformat()
        # Create update frequency element
        update_frequency = ElementTree.SubElement(root, "update_frequency")
        update_frequency.text = Commons.format_time_delta(self.update_frequency)
        # Return xml string
        return ElementTree.tostring(root)

    @staticmethod
    def from_xml_string(xml_string):
        """
        Loads new E621Sub object from XML string
        :param xml_string: string
        :return: E621Sub
        """
        # Create blank subscription
        new_sub = E621Sub()
        # Load xml
        sub_xml = ElementTree.fromstring(xml_string)
        # Load title, url, server
        new_sub.search = sub_xml.find("search").text
        new_sub.server_name = sub_xml.find("server").text
        # Load channel or user
        if sub_xml.find("channel") is not None:
            new_sub.channel_address = sub_xml.find("channel").text
        else:
            if sub_xml.find("user") is not None:
                new_sub.user_address = sub_xml.find("user").text
            else:
                raise Exception("Channel or user must be defined")
        # Load last item
        for latest_id in sub_xml.findall("latest_id"):
            new_sub.latest_ten_ids.append(int(latest_id.text))
        # Load last check
        if sub_xml.find("last_check") is not None:
            new_sub.last_check = datetime.strptime(sub_xml.find("last_check").text, "%Y-%m-%dT%H:%M:%S.%f")
        # Load update frequency
        new_sub.update_frequency = Commons.load_time_delta(sub_xml.find("update_frequency").text)
        # Return new feed
        return new_sub

    def to_json(self):
        # Create root element
        json_obj = {}
        # Create search element
        json_obj["search"] = self.search
        # Create server name element
        json_obj["server_name"] = self.server_name
        # Create channel name element, if applicable
        if self.channel_address is not None:
            json_obj["channel_address"] = self.channel_address
        # Create user name element, if applicable
        if self.user_address is not None:
            json_obj["user_address"] = self.user_address
        # Create latest id elements
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ten_ids:
            json_obj["latest_ids"].append(latest_id)
        # Create last check element
        if self.last_check is not None:
            json_obj["last_check"] = self.last_check.isoformat()
        # Create update frequency element
        json_obj["update_frequency"] = Commons.format_time_delta(self.update_frequency)
        # Return xml string
        return json_obj

    @staticmethod
    def from_json(json_obj):
        """
        Loads new E621Sub object from JSON object
        :param json_obj: object
        :return: E621Sub
        """
        # Create blank subscription
        new_sub = E621Sub()
        # Load search, server
        new_sub.search = json_obj["search"]
        new_sub.server_name = json_obj["server_name"]
        # Load channel or user
        if "channel_address" in json_obj:
            new_sub.channel_address = json_obj["channel_address"]
        else:
            if "user_address" in json_obj:
                new_sub.user_address = json_obj["user_address"]
            else:
                raise Exception("Channel or user must be defined")
        # Load last item
        for latest_id in json_obj["latest_ids"]:
            new_sub.latest_ten_ids.append(latest_id)
        # Load last check
        if "last_check" in json_obj:
            new_sub.last_check = datetime.strptime(json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f")
        # Load update frequency
        new_sub.update_frequency = Commons.load_time_delta(json_obj["update_frequency"])
        # Return new feed
        return new_sub


class E621SubList:
    """
    Holds the lists of E621 subscriptions, for loading and unloading.
    """

    def __init__(self):
        self.sub_list = []  # type: list [E621Sub]
        self.sub_lock = Lock()

    def add_sub(self, new_sub):
        """
        Adds a new E621 subscription to the list.
        :param new_sub: New subscription to add
        :type new_sub: E621Sub
        """
        self.sub_list.append(new_sub)

    def remove_sub(self, remove_sub):
        """
        Removes an E621 subscription from the list.
        :param remove_sub: Existing subscription to remove
        :type remove_sub: E621Sub
        """
        self.sub_list.remove(remove_sub)

    def get_subs_by_destination(self, destination):
        """
        Returns a list of subscriptions matching a specified destination.
        :param destination: Channel or User which E621Sub is posting to
        :type destination: Destination.Destination
        :return: list of E621Sub objects matching destination
        :rtype: list [E621Sub]
        """
        matching_subs = []
        for e621_sub in self.sub_list:
            if destination.server.name != e621_sub.server_name:
                continue
            if destination.is_channel() and destination.address != e621_sub.channel_address:
                continue
            if destination.is_user() and destination.address != e621_sub.user_address:
                continue
            matching_subs.append(e621_sub)
        return matching_subs

    def get_subs_by_search(self, search, destination):
        """
        Returns a list of subscriptions matching a specified search
        :param search: Search of the E621Search being searched for
        :type search: str
        :param destination: Channel or User which RssFeed is posting to
        :type destination: Destination.Destination
        :return: List of matching subscriptions
        :rtype: list [E621Sub]
        """
        search_clean = search.lower().strip()
        matching_feeds = []
        for e621_sub in self.get_subs_by_destination(destination):
            if search_clean == e621_sub.search.lower().strip():
                matching_feeds.append(e621_sub)
        return matching_feeds

    def to_xml(self):
        """
        Saves the whole subscription list to XML file
        :return: Nothing
        """
        # Create root element
        root_elem = ElementTree.Element("e621_subscriptions")
        # Add all feed elements
        for e621_sub_obj in self.sub_list:
            new_feed_elem = ElementTree.fromstring(e621_sub_obj.to_xml_string())
            root_elem.append(new_feed_elem)
        # Write xml to file
        ElementTree.ElementTree(root_elem).write("store/e621_subscriptions.xml")

    @staticmethod
    def from_xml():
        """
        Constructs a new E621SubList from the XML file
        :return: Newly constructed list of subscriptions
        :rtype: E621SubList
        """
        new_sub_list = E621SubList()
        # Try loading xml file, otherwise return blank list
        try:
            doc = ElementTree.parse("store/e621_subscriptions.xml")
        except (OSError, IOError):
            return new_sub_list
        # Loop feeds in xml file adding them to list
        root = doc.getroot()
        for e621_sub_elem in root.findall("e621_sub"):
            new_sub_obj = E621Sub.from_xml_string(ElementTree.tostring(e621_sub_elem))
            new_sub_list.add_sub(new_sub_obj)
        return new_sub_list

    def save_json(self):
        """
        Saves the whole subscription list to a JSON file
        :return: None
        """
        json_obj = {}
        json_obj["e621_subs"] = []
        for e621_sub in self.sub_list:
            json_obj["e621_subs"].append(e621_sub.to_json())
        # Write json to file
        with open("store/e621_subscriptions.json", "w") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json():
        """
        Constructs a new E621SubList from the JSON file
        :return: Newly constructed list of subscriptions
        :rtype: E621SubList
        """
        new_sub_list = E621SubList()
        # Try loading json file, otherwise return blank list
        try:
            with open("store/e621_subscriptions.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            return new_sub_list
        # Loop subs in json file adding them to list
        for e621_sub_elem in json_obj["e621_subs"]:
            new_sub_obj = E621Sub.from_json(e621_sub_elem)
            new_sub_list.add_sub(new_sub_obj)
        return new_sub_list


class SubE621Add(Function):
    """
    Adds a e621 search subscription for a given search, allowing specification of server and channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "e621 sub add"
        # Names which can be used to address the function
        self.names = {"e621 sub add", "add e621 sub", "sub e621 add", "add sub e621", "e621 subscription add",
                      "add e621 subscription", "subscription e621 add", "add subscription e621", "e621 search add",
                      "add e621 search", "search e621 add", "add search e621"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a e621 search to be checked for updates which will be posted to the current location." \
                         " Format: e621 sub add <search> <update period?>"

    def run(self, line, user_obj, destination_obj):
        # See if last argument is check period.
        try:
            try_period = line.split()[-1]
            search_delta = Commons.load_time_delta(try_period)
            search = line[:-len(try_period)]
        except ISO8601ParseError:
            search = line
            search_delta = Commons.load_time_delta("PT300S")
        search = search.strip()
        # Get current RSS feed list
        function_dispatcher = user_obj.server.hallo.function_dispatcher
        sub_check_class = function_dispatcher.get_function_by_name("e621 sub check")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_class)  # type: SubE621Check
        e621_sub_list = sub_check_obj.e621_sub_list  # type: E621SubList
        # Create new e621 search subscription
        e621_sub = E621Sub()
        e621_sub.server_name = user_obj.server.name
        e621_sub.search = search
        e621_sub.update_frequency = search_delta
        if destination_obj.is_channel():
            e621_sub.channel_address = destination_obj.address
        else:
            e621_sub.user_address = destination_obj.address
        # Update feed
        first_results = e621_sub.check_subscription()
        # If no results, this is an invalid search subscription
        if len(first_results) == 0:
            return "Error, this does not appear to be a valid search, or does not have results."
        # Locking
        with e621_sub_list.sub_lock:
            # Add new rss feed to list
            e621_sub_list.add_sub(e621_sub)
            # Save list
            e621_sub_list.save_json()
        # Return output
        return "I have added new e621 subscription for the search \"{}\"".format(e621_sub.search)


class SubE621Check(Function):
    """
    Checks a specified e621 search subscription for updates and returns them.
    """

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "e621 sub check"
        # Names which can be used to address the function
        self.names = {"e621 sub check", "check e621 sub", "sub e621 check", "check sub e621", "e621 subscription check",
                      "check e621 subscription", "subscription e621 check", "check subscription e621",
                      "e621 search check", "check e621 search", "search e621 check", "check search e621", "e621 check",
                      "check e621"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Checks a specified feed for updates and returns them. Format: e621 sub check <feed name>"
        self.e621_sub_list = E621SubList.load_json()

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return SubE621Check()

    def save_function(self):
        """Saves the function, persistent functions only."""
        self.e621_sub_list.save_json()

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MINUTE}

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        hallo = user_obj.server.hallo
        # Clean up input
        clean_input = line.strip().lower()
        # Check whether input is asking to update all e621 subscriptions
        if clean_input in self.NAMES_ALL:
            return self.run_all(hallo)
        # Acquire lock
        with self.e621_sub_list.sub_lock:
            # Otherwise see if a search subscription matches the specified one
            matching_subs = self.e621_sub_list.get_subs_by_search(clean_input, destination_obj)
            if len(matching_subs) == 0:
                return "Error, no e621 search subscriptions match that name. If you're adding a new search " \
                       "subscription, use \"e621 sub add\" with your search."
            output_lines = []
            # Loop through matching search subscriptions, getting updates
            for search_sub in matching_subs:
                new_items = search_sub.check_subscription()
                for search_item in new_items:
                    output_lines.append(search_sub.format_item(search_item))
            # Remove duplicate entries from output_lines
            output_lines = list(set(output_lines))
            # Save list
            self.e621_sub_list.save_json()
        # Output response to user
        if len(output_lines) == 0:
            return "There were no updates for \"{}\" e621 search.".format(line)
        return "The following search updates were found:\n" + "\n".join(output_lines)

    def run_all(self, hallo):
        output_lines = []
        with self.e621_sub_list.sub_lock:
            for search_sub in self.e621_sub_list.sub_list:
                new_items = search_sub.check_subscription()
                for search_item in new_items:
                    output_lines.append(search_sub.output_item(search_item, hallo))
            # Remove duplicate entries from output_lines
            output_lines = list(set(output_lines))
            # Save list
            self.e621_sub_list.save_json()
        # Output response to user
        if len(output_lines) == 0:
            return "There were no e621 search subscription updates."
        return "The following search updates were found and posted to their registered destinations:\n" + \
               "\n".join(output_lines)

    def passive_run(self, event, full_line, hallo_obj, server_obj=None, user_obj=None, channel_obj=None):
        """
        Replies to an event not directly addressed to the bot.
        :param event: string
        :param full_line: string
        :param hallo_obj: Hallo
        :param server_obj: Server
        :param user_obj: User
        :param channel_obj: Channel
        """
        # Check through all feeds to see which need updates
        with self.e621_sub_list.sub_lock:
            for search_sub in self.e621_sub_list.sub_list:
                # Only check those which have been too long since last check
                if search_sub.needs_check():
                    # Get new items
                    new_items = search_sub.check_subscription()
                    # Output all new items
                    for search_item in new_items:
                        search_sub.output_item(search_item, hallo_obj)
            # Save list
            self.e621_sub_list.save_json()


class SubE621List(Function):
    """
    List the currently active e621 search subscriptions.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "e621 sub list"
        # Names which can be used to address the function
        self.names = {"e621 sub list", "list e621 sub", "sub e621 list", "list sub e621", "e621 subscription list",
                      "list e621 subscription", "subscription e621 list", "list subscription e621", "e621 search list",
                      "list e621 search", "search e621 list", "list search e621"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Lists e621 search subscriptions for the current channel. Format: e621 sub list"

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.server
        hallo = server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("e621 sub check")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: SubE621Check
        e621_sub_list = sub_check_obj.e621_sub_list  # type: E621SubList
        # Find list of feeds for current channel.
        with e621_sub_list.sub_lock:
            dest_searches = e621_sub_list.get_subs_by_destination(destination_obj)
        if len(dest_searches) == 0:
            return "There are no e621 search subscriptions posting to this destination."
        output_lines = ["E621 search subscriptions posting to this channel:"]
        for search_item in dest_searches:
            output_lines.append(" - \"{}\"".format(search_item.search))
        return "\n".join(output_lines)


class SubE621Remove(Function):
    """
    Remove an E621 search subscription and no longer receive updates from it.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "e621 sub remove"
        # Names which can be used to address the function
        self.names = {"e621 sub remove", "remove e621 sub", "sub e621 remove", "remove sub e621",
                      "e621 subscription remove", "remove e621 subscription", "subscription e621 remove",
                      "remove subscription e621", "e621 search remove", "remove e621 search", "search e621 remove",
                      "remove search e621", "e621 sub delete", "delete e621 sub", "sub e621 delete", "delete sub e621",
                      "e621 subscription delete", "delete e621 subscription", "subscription e621 delete",
                      "delete subscription e621", "e621 search delete", "delete e621 search", "search e621 delete",
                      "delete search e621"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a specified e621 search subscription from the current or specified channel. " \
                         " Format: e621 sub remove <search>"

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.server
        hallo = server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("e621 sub check")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: SubE621Check
        e621_sub_list = sub_check_obj.e621_sub_list  # type: E621SubList
        # Clean up input
        clean_input = line.strip()
        # Find any feeds with specified search
        with e621_sub_list.sub_lock:
            test_feeds = e621_sub_list.get_subs_by_search(clean_input.lower(), destination_obj)
            if len(test_feeds) > 0:
                for del_sub in test_feeds:
                    e621_sub_list.remove_sub(del_sub)
                return "Removed \"{}\" e621 search subscription. Updates will no longer be " \
                       "sent to .".format(test_feeds[0].search,
                                          (test_feeds[0].channel_address or test_feeds[0].user_address))
        return "Error, there are no e621 search subscriptions in this channel matching that search."
