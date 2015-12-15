
# TODO: RssFeedList class


class RssFeed:
    """
    Class representing an rss feed in config
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

    def toXml(self):
        """
        Saves this RssFeed
        :return: string
        """
        pass

    @staticmethod
    def fromXml(xmlString):
        """
        Loads new RssFeed object from XML string
        :param xmlString: string
        :return: RssFeed
        """


# TODO: FeedCheck Function class
# TODO: FeedAdd Function class
# TODO: FeedUpdate Function class
# TODO: FeedRemove Function class
