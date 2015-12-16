from xml.etree import ElementTree


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
        for rssFeedXml in doc.getElementsByTagName("rss_feed"):
            newFeed = RssFeed.fromXmlString(ElementTree.toString(rssFeedXml))
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
    mLastItem = None
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
        title = ElementTree.SubElement(root,"title")
        title.text = self.mTitle
        # Create url element
        url = ElementTree.SubElement(root,"url")
        url.text = self.mUrl
        # Create server name element
        server = ElementTree.SubElement(root,"server")
        server.text = self.mServerName
        # Create channel name element, if applicable
        if self.mChannelName is not None:
            channel = ElementTree.SubElement(root,"channel")
            channel.text = self.mChannelName
        # Create user name element, if applicable
        if self.mUserName is not None:
            user = ElementTree.SubElement(root,"user")
            user.text = self.mUserName
        # Create last item element
        if self.mLastItem is not None:
            lastItem = ElementTree.SubElement(root,"last_item")
            lastItem.text = self.mLastItem
        # Create last check element
        if self.mLastCheck is not None:
            lastCheck = ElementTree.SubElement(root,"last_check")
            lastCheck.text = self.mLastCheck
        # Create update frequency element
        updateFrequency = ElementTree.SubElement(root,"update_frequency")
        updateFrequency.text = self.mUpdateFrequency
        # Return xml string
        return ElementTree.tostring(root)

    @staticmethod
    def fromXmlString(xmlString):
        """
        Loads new RssFeed object from XML string
        :param xmlString: string
        :return: RssFeed
        """
        # TODO
        return RssFeed()

# TODO: FeedCheck Function class
# TODO: FeedAdd Function class
# TODO: FeedUpdate Function class
# TODO: FeedRemove Function class
