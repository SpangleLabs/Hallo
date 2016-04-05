from Function import Function
from inc.commons import Commons
import time
import re
from xml.dom import minidom


class Is(Function):
    """
    A fun function which makes hallo respond to any message starting "hallo is..."
    """
    # Name for use in help listing
    mHelpName = "is"
    # Names which can be used to address the function
    mNames = {"is"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Placeholder. Format: is"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        return "I am?"


class Blank(Function):
    """
    Blank function which makes hallo respond to all messages of the format "hallo"
    """
    # Name for use in help listing
    mHelpName = ""
    # Names which can be used to address the function
    mNames = {""}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "I wonder if this works. Format: "

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        return "Yes?"


class Alarm(Function):
    """
    Alarm function, responds with a wooo wooo alarm.
    """
    # Name for use in help listing
    mHelpName = "alarm"
    # Names which can be used to address the function
    mNames = {"alarm"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Alarm. Format: alarm <subject>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        return 'woo woooooo woooooo ' + line + ' wooo wooo!'


class ArcticTerns(Function):
    """
    Posts a link to a random image of an arctic tern.
    """
    # Name for use in help listing
    mHelpName = "arctic tern"
    # Names which can be used to address the function
    mNames = {"arctic tern", "arctic terns", "mods asleep", "arctictern", "arcticterns", "mods"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Alarm. Format: alarm <subject>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        lineClean = line.strip().lower()
        if lineClean in ['nap', 'napping', 'plush']:
            number = Commons.get_random_int(0, 1)
            link = 'http://dr-spangle.com/AT/N0' + str(number) + '.JPG'
            return 'Plush arctic terns! ' + link
        number = Commons.get_random_int(0, 61)
        link = 'http://dr-spangle.com/AT/' + str(number).zfill(2) + '.JPG'
        return 'Arctic terns!! ' + link


class SlowClap(Function):
    """
    Makes hallo do a slow clap in the current or specified channel.
    """
    # Name for use in help listing
    mHelpName = "slowclap"
    # Names which can be used to address the function
    mNames = {"slowclap", "slow clap"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Slowclap. Format: slowclap"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        lineClean = line.strip().lower()
        serverObject = user_obj.get_server()
        if lineClean == "":
            if destination_obj is not None:
                serverObject.send("*clap*", destination_obj)
                time.sleep(0.5)
                serverObject.send("*clap*", destination_obj)
                time.sleep(2)
                return '*clap.*'
            else:
                return "You want me to slowclap yourself?"
        channelObject = serverObject.get_channel_by_name(lineClean)
        if not channelObject.is_in_channel():
            return "I'm not in that channel."
        serverObject.send("*clap*", channelObject)
        time.sleep(0.5)
        serverObject.send("*clap*", channelObject)
        time.sleep(2)
        serverObject.send("*clap.*", channelObject)
        return "done. :)"


class Boop(Function):
    """
    Boops people. Probably on the nose.
    """
    # Name for use in help listing
    mHelpName = "boop"
    # Names which can be used to address the function
    mNames = {"boop", "noseboop", "nose boop"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Boops people. Format: boop <name>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        """Boops people. Format: boop <name>"""
        lineClean = line.strip().lower()
        if lineClean == '':
            return "This function boops people, as such you need to specify a person for me to boop, " \
                   "in the form 'Hallo boop <name>' but without the <> brackets."
        # Get useful objects
        serverObject = user_obj.get_server()
        # Split arguments, see how many there are.
        lineSplit = lineClean.split()
        # If one argument, check that the user is in the current channel.
        if len(lineSplit) == 1:
            destUserObject = serverObject.get_user_by_name(lineClean)
            if destUserObject is None or not destUserObject.is_online():
                return "No one by that name is online."
            serverObject.send("\x01ACTION boops " + destUserObject.get_name() + ".\x01", destination_obj)
            return "Done."
        # If two arguments, see if one is a channel and the other a user.
        channelTest1 = serverObject.get_channel_by_name(lineSplit[0])
        if channelTest1.is_in_channel():
            destChannel = channelTest1
            destUser = serverObject.get_user_by_name(lineSplit[1])
        else:
            channelTest2 = serverObject.get_channel_by_name(lineSplit[1])
            if channelTest2.is_in_channel():
                destChannel = channelTest2
                destUser = serverObject.get_user_by_name(lineSplit[0])
            else:
                return "I'm not in any channel by that name."
        # If user by that name is not online, return a message saying that.
        if not destUser.is_online():
            return "No user by that name is online."
        # Send boop, then return done.
        serverObject.send("\x01ACTION boops " + destUser.get_name() + ".\x01", destChannel)
        return "Done."


class ReplyMessage:
    """
    Helper class for a reply message object.
    """
    mPrompt = None
    mResponseList = None
    mBlacklist = None
    mWhitelist = None

    def __init__(self, prompt):
        self.mPrompt = re.compile(prompt, re.IGNORECASE)
        self.mResponseList = []
        self.mBlacklist = {}
        self.mWhitelist = {}

    def checkDestination(self, destinationObject):
        """Checks if a given destination should be responded to."""
        serverName = destinationObject.get_server().get_name().lower()
        channelName = destinationObject.get_name().lower()
        # If a whitelist is set, check that
        if len(self.mWhitelist) != 0:
            if serverName in self.mWhitelist and channelName in self.mWhitelist[serverName]:
                return True
            return False
        # Otherwise check blacklist
        if serverName in self.mBlacklist and channelName in self.mBlacklist[serverName]:
            return False
        return True

    def checkResponse(self, inputLine, userObject, destinationObject):
        """Checks if this reply message will respond, and which response to use."""
        if self.mPrompt.search(inputLine):
            # Pick a response
            response = Commons.get_random_choice(self.mResponseList)[0]
            response = response.replace("{USER}", userObject.get_name())
            response = response.replace("{CHANNEL}", destinationObject.get_name())
            response = response.replace("{SERVER}", userObject.get_server().get_name())
            return response
        return None

    def addResponse(self, response):
        """Adds a new response to the list."""
        self.mResponseList.append(response)

    def addBlacklist(self, serverName, channelName):
        """Adds a new server/channel pair to blacklist."""
        if serverName not in self.mBlacklist:
            self.mBlacklist[serverName] = set()
        self.mBlacklist[serverName].add(channelName)

    def addWhitelist(self, serverName, channelName):
        """Adds a new server/channel pair to whitelist."""
        if serverName not in self.mWhitelist:
            self.mWhitelist[serverName] = set()
        self.mWhitelist[serverName].add(channelName)

    def toXml(self):
        """Writes ReplyMessage object as XML"""
        # Create document
        doc = minidom.Document()
        # Create root element
        root = doc.createElement("reply")
        doc.appendChild(root)
        # Add prompt element
        promptElement = doc.createElement("prompt")
        promptElement.appendChild(doc.createTextNode(self.mPrompt.pattern))
        root.appendChild(promptElement)
        # Add all response elements
        for response in self.mResponseList:
            responseElement = doc.createElement("response")
            responseElement.appendChild(doc.createTextNode(response))
            root.appendChild(responseElement)
        # Add blacklist elements
        for serverName in self.mBlacklist:
            for channelName in self.mBlacklist[serverName]:
                blacklistElement = doc.createElement("blacklist")
                serverElement = doc.createElement("server")
                serverElement.appendChild(doc.createTextNode(serverName))
                blacklistElement.appendChild(serverElement)
                channelElement = doc.createElement("channel")
                channelElement.appendChild(doc.createTextNode(channelName))
                blacklistElement.appendChild(channelElement)
                root.appendChild(blacklistElement)
        # Add whitelist elements
        for serverName in self.mWhitelist:
            for channelName in self.mWhitelist[serverName]:
                whitelistElement = doc.createElement("whitelist")
                serverElement = doc.createElement("server")
                serverElement.appendChild(doc.createTextNode(serverName))
                whitelistElement.appendChild(serverElement)
                channelElement = doc.createElement("channel")
                channelElement.appendChild(doc.createTextNode(channelName))
                whitelistElement.appendChild(channelElement)
                root.appendChild(whitelistElement)
        # Output XML
        return doc.toxml()

    @staticmethod
    def fromXml(xmlString):
        """Loads a new ReplyMessage object from XML"""
        # Load document
        doc = minidom.parseString(xmlString)
        # Get prompt and create ReplyMessage object
        newPrompt = doc.getElementsByTagName("prompt")[0].firstChild.data
        newReplyMessage = ReplyMessage(newPrompt)
        # Get responses
        for responseXml in doc.getElementsByTagName("response"):
            newResponse = responseXml.firstChild.data
            newReplyMessage.addResponse(newResponse)
        # Get blacklists
        blacklistXmlList = doc.getElementsByTagName("blacklist")
        for blacklistXml in blacklistXmlList:
            newServer = blacklistXml.getElementsByTagName("server")[0].firstChild.data
            newChannel = blacklistXml.getElementsByTagName("channel")[0].firstChild.data
            newReplyMessage.addBlacklist(newServer, newChannel)
        # Get whitelists
        whitelistXmlList = doc.getElementsByTagName("whitelist")
        for whitelistXml in whitelistXmlList:
            newServer = whitelistXml.getElementsByTagName("server")[0].firstChild.data
            newChannel = whitelistXml.getElementsByTagName("channel")[0].firstChild.data
            newReplyMessage.addWhitelist(newServer, newChannel)
        # Returned the newly built ReplyMessage
        return newReplyMessage


class ReplyMessageList:
    """
    Stores and handles the list of ReplyMessage objects.
    """
    mReplyMessageList = None

    def __init__(self):
        self.mReplyMessageList = set()

    def addReplyMessage(self, replyMessage):
        self.mReplyMessageList.add(replyMessage)

    def getResponse(self, fullLine, userObject, channelObject):
        """Check ReplyMessage objects to see which response to give. Or NULL if none apply."""
        response = None
        for replyMessage in self.mReplyMessageList:
            if not replyMessage.checkDestination(channelObject):
                continue
            response = response or replyMessage.checkResponse(fullLine, userObject, channelObject)
        return response

    @staticmethod
    def loadFromXml():
        """Loads ReplyMessageList from XML."""
        doc = minidom.parse("store/reply_list.xml")
        # Create new object
        newReplyMessageList = ReplyMessageList()
        # Loop through reply messages
        for replyXml in doc.getElementsByTagName("reply"):
            replyMessage = ReplyMessage.fromXml(replyXml.toxml())
            newReplyMessageList.addReplyMessage(replyMessage)
        # Return new repo object
        return newReplyMessageList

    def saveToXml(self):
        """Saves ReplyMessageList to XML."""
        # Create document, with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='reply_list',
            publicId='',
            systemId='reply_list.dtd',
        )
        doc = docimp.createDocument(None, 'reply_list', doctype)
        # get root element
        root = doc.getElementsByTagName("reply_list")[0]
        # Add reply message objects
        for replyMessage in self.mReplyMessageList:
            replyElement = minidom.parseString(replyMessage.to_xml()).firstChild
            root.appendChild(replyElement)
        # save XML
        doc.writexml(open("store/reply_list.xml", "w"), addindent="\t", newl="\n")


class Reply(Function):
    """
    Function to make hallo reply to detected phrases with a specified response
    """
    # Name for use in help listing
    mHelpName = "reply"
    # Names which can be used to address the function
    mNames = {"reply"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Make hallo reply to a detected phrase with a specified response."

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        return "Not yet handled."
        pass

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MESSAGE}

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """Replies to an event not directly addressed to the bot."""
        replyMessageList = ReplyMessageList.loadFromXml()
        response = replyMessageList.getResponse(full_line, user_obj, channel_obj)
        return response
