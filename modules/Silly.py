from Function import Function
from inc.Commons import Commons
import time
import re
from xml.dom import minidom


class Is(Function):
    """
    A fun function which makes hallo respond to any message starting "hallo is..."
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "is"
        # Names which can be used to address the function
        self.names = {"is"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Placeholder. Format: is"

    def run(self, line, user_obj, destination_obj=None):
        return "I am?"


class Blank(Function):
    """
    Blank function which makes hallo respond to all messages of the format "hallo"
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = ""
        # Names which can be used to address the function
        self.names = {""}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "I wonder if this works. Format: "

    def run(self, line, user_obj, destination_obj=None):
        return "Yes?"


class Alarm(Function):
    """
    Alarm function, responds with a wooo wooo alarm.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "alarm"
        # Names which can be used to address the function
        self.names = {"alarm"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Alarm. Format: alarm <subject>"

    def run(self, line, user_obj, destination_obj=None):
        return 'woo woooooo woooooo ' + line + ' wooo wooo!'


class SlowClap(Function):
    """
    Makes hallo do a slow clap in the current or specified channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        help_name = "slowclap"
        # Names which can be used to address the function
        names = {"slowclap", "slow clap"}
        # Help documentation, if it's just a single line, can be set here
        help_docs = "Slowclap. Format: slowclap"

    def run(self, line, user_obj, destination_obj=None):
        line_clean = line.strip().lower()
        server_obj = user_obj.get_server()
        if line_clean == "":
            if destination_obj is not None:
                server_obj.send("*clap*", destination_obj)
                time.sleep(0.5)
                server_obj.send("*clap*", destination_obj)
                time.sleep(2)
                return '*clap.*'
            else:
                return "You want me to slowclap yourself?"
        channel_obj = server_obj.get_channel_by_name(line_clean)
        if not channel_obj.is_in_channel():
            return "I'm not in that channel."
        server_obj.send("*clap*", channel_obj)
        time.sleep(0.5)
        server_obj.send("*clap*", channel_obj)
        time.sleep(2)
        server_obj.send("*clap.*", channel_obj)
        return "done. :)"


class Boop(Function):
    """
    Boops people. Probably on the nose.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "boop"
        # Names which can be used to address the function
        self.names = {"boop", "noseboop", "nose boop"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Boops people. Format: boop <name>"

    def run(self, line, user_obj, destination_obj=None):
        """Boops people. Format: boop <name>"""
        line_clean = line.strip().lower()
        if line_clean == '':
            return "Error, this function boops people, as such you need to specify a person for me to boop, " \
                   "in the form 'Hallo boop <name>' but without the <> brackets."
        # Get useful objects
        server_obj = user_obj.get_server()
        # Split arguments, see how many there are.
        line_split = line_clean.split()
        # If one argument, check that the user is in the current channel.
        if len(line_split) == 1:
            dest_user_obj = server_obj.get_user_by_name(line_clean)
            if not dest_user_obj.online or dest_user_obj not in destination_obj.user_list:
                return "Error, No one by that name is online or in channel."
            server_obj.send("\x01ACTION boops " + dest_user_obj.get_name() + ".\x01", destination_obj)
            return "Done."
        # If two arguments, see if one is a channel and the other a user.
        channel_test_1 = server_obj.get_channel_by_name(line_split[0])
        if channel_test_1.is_in_channel():
            dest_channel = channel_test_1
            dest_user = server_obj.get_user_by_name(line_split[1])
        else:
            channel_test_2 = server_obj.get_channel_by_name(line_split[1])
            if channel_test_2.is_in_channel():
                dest_channel = channel_test_2
                dest_user = server_obj.get_user_by_name(line_split[0])
            else:
                return "Error, I'm not in any channel by that name."
        # If user by that name is not online, return a message saying that.
        if not dest_user.online or dest_user not in dest_channel.user_list:
            return "Error, No user by that name is online."
        # Send boop, then return done.
        server_obj.send("\x01ACTION boops " + dest_user.get_name() + ".\x01", dest_channel)
        return "Done."


class ReplyMessage:
    """
    Helper class for a reply message object.
    """

    def __init__(self, prompt):
        self.prompt = re.compile(prompt, re.IGNORECASE)
        self.response_list = []
        self.blacklist = {}
        self.whitelist = {}

    def check_destination(self, destination_obj):
        """Checks if a given destination should be responded to."""
        server_name = destination_obj.get_server().get_name().lower()
        channel_name = destination_obj.get_name().lower()
        # If a whitelist is set, check that
        if len(self.whitelist) != 0:
            if server_name in self.whitelist and channel_name in self.whitelist[server_name]:
                return True
            return False
        # Otherwise check blacklist
        if server_name in self.blacklist and channel_name in self.blacklist[server_name]:
            return False
        return True

    def check_response(self, input_line, user_obj, destination_obj):
        """Checks if this reply message will respond, and which response to use."""
        if self.prompt.search(input_line):
            # Pick a response
            response = Commons.get_random_choice(self.response_list)[0]
            response = response.replace("{USER}", user_obj.get_name())
            response = response.replace("{CHANNEL}", destination_obj.get_name())
            response = response.replace("{SERVER}", user_obj.get_server().get_name())
            return response
        return None

    def add_response(self, response):
        """Adds a new response to the list."""
        self.response_list.append(response)

    def add_blacklist(self, server_name, channel_name):
        """Adds a new server/channel pair to blacklist."""
        if server_name not in self.blacklist:
            self.blacklist[server_name] = set()
        self.blacklist[server_name].add(channel_name)

    def add_whitelist(self, server_name, channel_name):
        """Adds a new server/channel pair to whitelist."""
        if server_name not in self.whitelist:
            self.whitelist[server_name] = set()
        self.whitelist[server_name].add(channel_name)

    def to_xml(self):
        """Writes ReplyMessage object as XML"""
        # Create document
        doc = minidom.Document()
        # Create root element
        root = doc.createElement("reply")
        doc.appendChild(root)
        # Add prompt element
        prompt_elem = doc.createElement("prompt")
        prompt_elem.appendChild(doc.createTextNode(self.prompt.pattern))
        root.appendChild(prompt_elem)
        # Add all response elements
        for response in self.response_list:
            response_elem = doc.createElement("response")
            response_elem.appendChild(doc.createTextNode(response))
            root.appendChild(response_elem)
        # Add blacklist elements
        for server_name in self.blacklist:
            for channel_name in self.blacklist[server_name]:
                blacklist_elem = doc.createElement("blacklist")
                server_elem = doc.createElement("server")
                server_elem.appendChild(doc.createTextNode(server_name))
                blacklist_elem.appendChild(server_elem)
                channel_elem = doc.createElement("channel")
                channel_elem.appendChild(doc.createTextNode(channel_name))
                blacklist_elem.appendChild(channel_elem)
                root.appendChild(blacklist_elem)
        # Add whitelist elements
        for server_name in self.whitelist:
            for channel_name in self.whitelist[server_name]:
                whitelist_elem = doc.createElement("whitelist")
                server_elem = doc.createElement("server")
                server_elem.appendChild(doc.createTextNode(server_name))
                whitelist_elem.appendChild(server_elem)
                channel_elem = doc.createElement("channel")
                channel_elem.appendChild(doc.createTextNode(channel_name))
                whitelist_elem.appendChild(channel_elem)
                root.appendChild(whitelist_elem)
        # Output XML
        return doc.toxml()

    @staticmethod
    def from_xml(xml_string):
        """Loads a new ReplyMessage object from XML"""
        # Load document
        doc = minidom.parseString(xml_string)
        # Get prompt and create ReplyMessage object
        new_prompt = doc.getElementsByTagName("prompt")[0].firstChild.data
        new_reply_message = ReplyMessage(new_prompt)
        # Get responses
        for response_elem in doc.getElementsByTagName("response"):
            response_obj = response_elem.firstChild.data
            new_reply_message.add_response(response_obj)
        # Get blacklists
        blacklist_elem_list = doc.getElementsByTagName("blacklist")
        for blacklist_elem in blacklist_elem_list:
            new_server = blacklist_elem.getElementsByTagName("server")[0].firstChild.data
            new_channel = blacklist_elem.getElementsByTagName("channel")[0].firstChild.data
            new_reply_message.add_blacklist(new_server, new_channel)
        # Get whitelists
        whitelist_elem_list = doc.getElementsByTagName("whitelist")
        for whitelist_elem in whitelist_elem_list:
            new_server = whitelist_elem.getElementsByTagName("server")[0].firstChild.data
            new_channel = whitelist_elem.getElementsByTagName("channel")[0].firstChild.data
            new_reply_message.add_whitelist(new_server, new_channel)
        # Returned the newly built ReplyMessage
        return new_reply_message


class ReplyMessageList:
    """
    Stores and handles the list of ReplyMessage objects.
    """

    def __init__(self):
        self.reply_message_list = set()

    def add_reply_message(self, reply_message):
        self.reply_message_list.add(reply_message)

    def get_response(self, full_line, user_obj, channel_obj):
        """Check ReplyMessage objects to see which response to give. Or NULL if none apply."""
        response = None
        for reply_message in self.reply_message_list:
            if not reply_message.check_destination(channel_obj):
                continue
            response = response or reply_message.check_response(full_line, user_obj, channel_obj)
        return response

    @staticmethod
    def load_from_xml():
        """Loads ReplyMessageList from XML."""
        doc = minidom.parse("store/reply_list.xml")
        # Create new object
        new_reply_message_list = ReplyMessageList()
        # Loop through reply messages
        for reply_elem in doc.getElementsByTagName("reply"):
            reply_message = ReplyMessage.from_xml(reply_elem.toxml())
            new_reply_message_list.add_reply_message(reply_message)
        # Return new repo object
        return new_reply_message_list

    def save_to_xml(self):
        """Saves ReplyMessageList to XML."""
        # Create document, with DTD
        doc_imp = minidom.DOMImplementation()
        doc_type = doc_imp.createDocumentType(
            qualifiedName='reply_list',
            publicId='',
            systemId='reply_list.dtd',
        )
        doc = doc_imp.createDocument(None, 'reply_list', doc_type)
        # get root element
        root = doc.getElementsByTagName("reply_list")[0]
        # Add reply message objects
        for reply_obj in self.reply_message_list:
            reply_elem = minidom.parseString(reply_obj.to_xml()).firstChild
            root.appendChild(reply_elem)
        # save XML
        doc.writexml(open("store/reply_list.xml", "w"), addindent="\t", newl="\n")


class Reply(Function):
    """
    Function to make hallo reply to detected phrases with a specified response
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "reply"
        # Names which can be used to address the function
        self.names = {"reply"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Make hallo reply to a detected phrase with a specified response."

    def run(self, line, user_obj, destination_obj=None):
        return "Not yet handled."
        pass

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        reply_message_list = ReplyMessageList.load_from_xml()
        response = reply_message_list.get_response(full_line, user_obj, channel_obj)
        return response
