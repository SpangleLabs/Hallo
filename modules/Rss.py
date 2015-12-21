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
    mTitle = None
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
        # Output true if there are new items, false otherwise
        return len(newItems) > 0

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
        return {Function.EVENT_MINUTE}

    def run(self, line, userObject, destinationObject=None):
        # Clean up input
        # Check whether input is asking to update all feeds
        # Otherwise see if a feed title matches the specified one
        raise NotImplementedError

    def passiveRun(self, event, fullLine, serverObject, userObject=None, channelObject=None):
        """
        Replies to an event not directly addressed to the bot.
        :param event: string
        :param fullLine: string
        :param serverObject: Server
        :param userObject: User
        :param channelObject: Channel
        """
        # TODO: Check all feeds, see which need checking and which have been updated.
        pass

# TODO: FeedAdd Function class
# TODO: FeedUpdate Function class
# TODO: FeedRemove Function class
