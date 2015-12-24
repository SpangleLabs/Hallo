from xml.etree import ElementTree
from datetime import datetime
from inc.commons import Commons
import hashlib
from Function import Function


class RssFeedList:
    """
    Holds the lists of feeds, for loading and unloading.
    """
    mFeedList = []

    def addFeed(self, newFeed):
        """
        Adds a new RSS feed to the list.
        :param newFeed: RssFeed
        :return:
        """
        self.mFeedList.append(newFeed)

    def getFeedList(self):
        """
        Returns the full list of RSS feeds
        :return: array
        """
        return self.mFeedList

    def getFeedsByTitle(self, title):
        """
        Returns a list of feeds matching a specified title
        :param title: string
        :return: list<RssFeed>
        """
        titleClean = title.lower().strip()
        matchingFeeds = []
        for rssFeed in self.mFeedList:
            if titleClean == rssFeed.mTitle.lower().strip():
                matchingFeeds.append(rssFeed)
        return matchingFeeds

    def toXml(self):
        """
        Saves the whole feed list to XML file
        :return:
        """
        # Create root element
        rootElement = ElementTree.Element("rss_feeds")
        # Add all feed elements
        for rssFeed in self.mFeedList:
            newFeedElement = rssFeed.toXmlString()
            rootElement.append(newFeedElement)
        # Write xml to file
        ElementTree.ElementTree(rootElement).write("store/rss_feeds.xml")

    @staticmethod
    def fromXml():
        """
        Constructs a new RssFeedList from the XML file
        :return: RssFeedList
        """
        newFeedList = RssFeedList()
        # Try loading xml file, otherwise return blank list
        try:
            doc = ElementTree.parse("store/rss_feeds.xml")
        except (OSError, IOError):
            return newFeedList
        # Loop feeds in xml file adding them to list
        root = doc.getroot()
        for rssFeedXml in root.findall("rss_feed"):
            newFeed = RssFeed.fromXmlString(ElementTree.tostring(rssFeedXml))
            newFeedList.addFeed(newFeed)
        return newFeedList


class RssFeed:
    """
    Class representing an rss feed in config.
    """
    mTitle = ""
    mUrl = None
    mServerName = None
    mChannelName = None
    mUserName = None
    mLastItemHash = None
    mLastCheck = None
    mUpdateFrequency = None

    def checkFeed(self):
        """
        Checks the feed for any updates
        """
        rssData = Commons.loadUrlString(self.mUrl)
        rssXml = ElementTree.fromstring(rssData)
        rssElement = rssXml.getroot()
        channelElement = rssElement.find("channel")
        newItems = []
        # Loop elements, seeing when any match the last item's hash
        for itemElement in channelElement.findall("item"):
            itemXml = ElementTree.tostring(itemElement)
            itemHash = hashlib.md5(itemXml.encode("utf-8")).hexdigest()
            newItems.append(itemElement)
            if itemHash == self.mLastItemHash:
                break
        # Return new items
        return newItems

    def outputItem(self, rssItem, hallo, server=None, destination=None):
        """
        Outputs an item to a given server and destination, or the feed default.
        :param rssItem: string
        :param hallo: Hallo
        :param server: Server
        :param destination: Destination
        """
        # Get server
        if server is None:
            server = hallo.getServerByName(self.mServerName)
            if server is None:
                return "Invalid server."
        # Get destination
        if destination is None:
            if self.mChannelName is not None:
                destination = server.getChannelByName(self.mChannelName)
            if self.mUserName is not None:
                destination = server.getUserByName(self.mUserName)
            if destination is None:
                return "Invalid destination."
        # Construct output
        output = self.formatItem(rssItem)
        destination.send(output)
        return output

    def formatItem(self, rssItem):
        """
        Formats an rss feed item for output.
        :param rssItem: string
        :return: string
        """
        # Load item xml
        itemXml = ElementTree.fromstring(rssItem)
        itemTitle = itemXml.find("title")
        itemLink = itemXml.find("link")
        # Construct output
        output = "Update on \"" + self.mTitle + "\" RSS feed. \"" + itemTitle + "\" " + itemLink
        return output

    def needsCheck(self):
        """
        Returns whether an rssfeed check is overdue.
        :return: bool
        """
        if self.mLastCheck is None:
            return True
        if datetime.now() > self.mLastCheck + self.mUpdateFrequency:
            return True
        return False

    def toXmlString(self):
        """
        Saves this RssFeed
        :return: string
        """
        # Create root element
        root = ElementTree.Element("rss_feed")
        # Create title element
        title = ElementTree.SubElement(root, "title")
        title.text = self.mTitle
        # Create url element
        url = ElementTree.SubElement(root, "url")
        url.text = self.mUrl
        # Create server name element
        server = ElementTree.SubElement(root, "server")
        server.text = self.mServerName
        # Create channel name element, if applicable
        if self.mChannelName is not None:
            channel = ElementTree.SubElement(root, "channel")
            channel.text = self.mChannelName
        # Create user name element, if applicable
        if self.mUserName is not None:
            user = ElementTree.SubElement(root, "user")
            user.text = self.mUserName
        # Create last item element
        if self.mLastItemHash is not None:
            lastItem = ElementTree.SubElement(root, "last_item")
            lastItem.text = self.mLastItemHash
        # Create last check element
        if self.mLastCheck is not None:
            lastCheck = ElementTree.SubElement(root, "last_check")
            lastCheck.text = self.mLastCheck.isoformat()
        # Create update frequency element
        updateFrequency = ElementTree.SubElement(root, "update_frequency")
        updateFrequency.text = Commons.formatTimeDelta(self.mUpdateFrequency)
        # Return xml string
        return ElementTree.tostring(root)

    @staticmethod
    def fromXmlString(xmlString):
        """
        Loads new RssFeed object from XML string
        :param xmlString: string
        :return: RssFeed
        """
        # Create blank feed
        newFeed = RssFeed()
        # Load xml
        feedXml = ElementTree.fromstring(xmlString)
        # Load title, url, server
        newFeed.mTitle = feedXml.find("title").text
        newFeed.mUrl = feedXml.find("url").text
        newFeed.mServerName = feedXml.find("server").text
        # Load channel or user
        if feedXml.find("channel") is not None:
            newFeed.mChannelName = feedXml.find("channel").text
        else:
            if feedXml.find("user") is not None:
                newFeed.mUserName = feedXml.find("user").text
            else:
                raise Exception("Channel or user must be defined")
        # Load last item
        if feedXml.find("last_item") is not None:
            newFeed.mLastItemHash = feedXml.find("last_item").text
        # Load last check
        if feedXml.find("last_check") is not None:
            newFeed.mLastCheck = datetime.strptime(feedXml.find("last_check").text, "%Y-%m-%dT%H:%M:%S")
        # Load update frequency
        newFeed.mUpdateFrequency = Commons.loadTimeDelta(feedXml.find("update_frequency").text)
        # Return new feed
        return newFeed


class FeedCheck(Function):
    """
    Checks a specified feed for updates and returns them.
    """
    # Name for use in help listing
    mHelpName = "rss check"
    # Names which can be used to address the function
    mNames = {"rss check", "check rss", "check rss feed", "rss feed check", "check feed", "feed check"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Checks a specified feed for updates and returns them. Format: rss check <feed name>"

    mRssFeedList = None

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        self.mRssFeedList = RssFeedList.fromXml()

    @staticmethod
    def isPersistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def loadFunction():
        """Loads the function, persistent functions only."""
        return FeedCheck()

    def saveFunction(self):
        """Saves the function, persistent functions only."""
        self.mRssFeedList.toXml()

    def getPassiveEvents(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_PING}

    def run(self, line, userObject, destinationObject=None):
        # Handy variables
        server = userObject.getServer()
        hallo = server.getHallo()
        # Clean up input
        cleanInput = line.strip().lower()
        # Check whether input is asking to update all feeds
        if cleanInput in self.NAMES_ALL:
            outputLines = []
            for rssFeed in self.mRssFeedList.getFeedList():
                newItems = rssFeed.checkFeed()
                for rssItem in newItems:
                    outputLines.append(rssFeed.outputItem(rssItem, hallo))
            # Remove duplicate entries from outputLines
            outputLines = list(set(outputLines))
            # Output response to user
            if len(outputLines) == 0:
                return "There were no feed updates."
            return "The following feed updates were found:\n" + "\n".join(outputLines)
        # Otherwise see if a feed title matches the specified one
        matchingFeeds = self.mRssFeedList.getFeedsByTitle(cleanInput)
        if len(matchingFeeds) == 0:
            return "No Rss Feeds match that name. If you're adding a new feed, use \"rss add\" with your link."
        outputLines = []
        # Loop through matching rss feeds, getting updates
        for rssFeed in matchingFeeds:
            newItems = rssFeed.checkFeed()
            for rssItem in newItems:
                outputLines.append(rssFeed.outputItem(rssItem, hallo))
        # Remove duplicate entries from outputLines
        outputLines = list(set(outputLines))
        # Output response to user
        if len(outputLines) == 0:
            return "There were no updates for \"" + line + "\" RSS feed."
        return "The following feed updates were found:\n" + "\n".join(outputLines)

    def passiveRun(self, event, fullLine, serverObject, userObject=None, channelObject=None):
        """
        Replies to an event not directly addressed to the bot.
        :param event: string
        :param fullLine: string
        :param serverObject: Server
        :param userObject: User
        :param channelObject: Channel
        """
        hallo = serverObject.getHallo()
        # Check through all feeds to see which need updates
        for rssFeed in self.mRssFeedList.getFeedList():
            # Only check those which have been too long since last check
            if rssFeed.needsCheck():
                # Get new items
                newItems = rssFeed.checkFeed()
                # Output all new items
                for rssItem in newItems:
                    rssFeed.outputItem(rssItem, hallo)


# TODO: FeedAdd Function class
class FeedAdd(Function):
    """
    Adds a new RSS feed from a link, allowing specification of server and channel.
    """
    # Name for use in help listing
    mHelpName = "rss add"
    # Names which can be used to address the function
    mNames = {"rss add", "add rss", "add rss feed", "rss feed add", "add feed", "feed add"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Adds a new RSS feed to be tracked in the current or specified channel. Format: rss all <feed url>"

    mRssFeedList = None

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, userObject, destinationObject=None):
        # Handy variables
        server = userObject.getServer()
        hallo = server.getHallo()
        # Clean up input
        cleanInput = line.strip()
        inputList = cleanInput.split()
        url = inputList[0]
        # Find server name and channel name
        serverName = server.getName()
        channelName = None
        if len(inputList) > 2:
            testServer = hallo.getServerByName(inputLine[1])
            if testServer is None:
                return "Invalid server name."
            serverName = testServer.getName()
            testChannel = testServer.getChannelByName(inputList[2])
            if testChannel is None:
                return "Invalid channel name."
            channelName = testChannel.getName()
        if len(inputList) == 2:
            testChannel = server.getChannelByName(inputList[1])
            if testChannel is None:
                return "Invalid channel name."
            channelName = testChannel.getName()
        # If no server and channel is specified, use current channel or user
        if channelName is None and destinationObject is not None and destinationObject.isChannel():
            channelName = destinationObject.getName()
        userName = userObject.getName()
        # Create RssFeed object
        newFeed = RssFeed()
        newFeed.mUrl = url
        newFeed.mServerName = serverName
        if channelName is None:
            newFeed.mUserName = userName
        else:
            newFeed.mChannelName = channelName
        newFeed.mUpdateFrequency = Commons.loadTimeDelta("PT30M")
        # Test new RssFeed
        try:
            newFeed.checkFeed()
        except Exception as e:
            return "This RSS feed does not appear to be valid. It failed with error: " + str(e)
        # Get RssFeedList
        # Add RssFeedList
        # Send response to user

# TODO: FeedRemove Function class
# TODO: FeedList Function class
