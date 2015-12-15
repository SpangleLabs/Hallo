
# TODO: RssFeedList class
class RssFeedList:
    """
    Holds the lists of feeds, for loading and unloading.
    """
    mFeedList = []

    def addList(self,newList):
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
        pass

    @staticmethod
    def fromXml():
        """
        Constructs a new RssFeedList from the XML file
        :return: RssFeedList
        """
        pass


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
        pass

    @staticmethod
    def fromXmlString(xmlString):
        """
        Loads new RssFeed object from XML string
        :param xmlString: string
        :return: RssFeed
        """
        pass

# TODO: FeedCheck Function class
# TODO: FeedAdd Function class
# TODO: FeedUpdate Function class
# TODO: FeedRemove Function class
