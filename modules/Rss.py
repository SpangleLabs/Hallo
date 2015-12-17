from xml.etree import ElementTree
from datetime import datetime
from inc.commons import Commons

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
        # TODO
        pass

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


# TODO: FeedCheck Function class
# TODO: FeedAdd Function class
# TODO: FeedUpdate Function class
# TODO: FeedRemove Function class
