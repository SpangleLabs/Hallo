from xml.etree.ElementTree import ParseError
from xml.etree import ElementTree
from datetime import datetime
from inc.commons import Commons
import hashlib
from Function import Function
import urllib.error
from inc.commons import ISO8601ParseError


class RssFeedList:
    """
    Holds the lists of feeds, for loading and unloading.
    """
    mFeedList = []

    def addFeed(self, newFeed):
        """
        Adds a new RSS feed to the list.
        :param newFeed: RssFeed
        """
        self.mFeedList.append(newFeed)

    def removeFeed(self, removeFeed):
        """
        Removes an RSS feed from the list.
        :param removeFeed: RssFeed
        """
        self.mFeedList.remove(removeFeed)

    def getFeedList(self):
        """
        Returns the full list of RSS feeds
        :return: array
        """
        return self.mFeedList

    def getFeedsByDestination(self, server, destination):
        """
        Returns a list of feeds matching a specified destination.
        :param server: Server that the RssFeed is posting to
        :param destination: Channel or User which RssFeed is posting to
        :return: list<RssFeed> list of RssFeeds matching destination
        """
        matchingFeeds = []
        for rssFeed in self.mFeedList:
            if server.get_name() != rssFeed.mServerName.lower():
                continue
            if destination.is_channel() and destination.get_name() != rssFeed.mChannelName:
                continue
            if destination.is_user() and destination.get_name() != rssFeed.mUserName:
                continue
            matchingFeeds.append(rssFeed)
        return matchingFeeds

    def getFeedsByTitle(self, title, server, destination):
        """
        Returns a list of feeds matching a specified title
        :param title: Title of the RssFeed being searched for
        :param server: Server that the RssFeed is posting to
        :param destination: Channel or User which RssFeed is posting to
        :return: list<RssFeed>
        """
        titleClean = title.lower().strip()
        matchingFeeds = []
        for rssFeed in self.getFeedsByDestination(server, destination):
            if titleClean == rssFeed.mTitle.lower().strip():
                matchingFeeds.append(rssFeed)
        return matchingFeeds

    def getFeedsByURL(self, url, server, destination):
        """
        Returns a list of feeds matching a specified title
        :param url: URL of RSS feed to search for
        :param server: Server that the RssFeed is posting to
        :param destination: Channel or User which RssFeed is posting to
        :return: list<RssFeed> List of RSS feeds matching specified URL
        """
        urlClean = url.strip()
        matchingFeeds = []
        for rssFeed in self.getFeedsByDestination(server, destination):
            if urlClean == rssFeed.mUrl.strip():
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
        :return: list of ElementTree XML elements
        """
        rssData = Commons.load_url_string(self.mUrl)
        rssXml = ElementTree.fromstring(rssData)
        rssElement = rssXml.getroot()
        channelElement = rssElement.find("channel")
        newItems = []
        # Update title
        titleElement = channelElement.find("title")
        self.mTitle = titleElement.text
        # Loop elements, seeing when any match the last item's hash
        firstHash = None
        for itemElement in channelElement.findall("item"):
            itemXml = ElementTree.tostring(itemElement)
            itemHash = hashlib.md5(itemXml.encode("utf-8")).hexdigest()
            if firstHash is None:
                firstHash = itemHash
            if itemHash == self.mLastItemHash:
                break
            newItems.append(itemElement)
        # Update last item hash
        self.mLastItemHash = firstHash
        # Return new items
        return newItems

    def outputItem(self, rssItem, hallo, server=None, destination=None):
        """
        Outputs an item to a given server and destination, or the feed default.
        :param rssItem: ElementTree.Element rss item xml element which wants outputting
        :param hallo: Hallo
        :param server: Server
        :param destination: Destination
        """
        # Get server
        if server is None:
            server = hallo.get_server_by_name(self.mServerName)
            if server is None:
                return "Invalid server."
        # Get destination
        if destination is None:
            if self.mChannelName is not None:
                destination = server.get_channel_by_name(self.mChannelName)
            if self.mUserName is not None:
                destination = server.get_user_by_name(self.mUserName)
            if destination is None:
                return "Invalid destination."
        # Construct output
        output = self.formatItem(rssItem)
        destination.send(output)
        return output

    def formatItem(self, rssItem):
        """
        Formats an rss feed item for output.
        :param rssItem: ElementTree.Element rss item xml element to format
        :return: string
        """
        # Load item xml
        itemTitle = rssItem.find("title").text
        itemLink = rssItem.find("link").text
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
        updateFrequency.text = Commons.format_time_delta(self.mUpdateFrequency)
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
        newFeed.mUpdateFrequency = Commons.load_time_delta(feedXml.find("update_frequency").text)
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
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return FeedCheck()

    def save_function(self):
        """Saves the function, persistent functions only."""
        self.mRssFeedList.toXml()

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_PING}

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.get_server()
        hallo = server.get_hallo()
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
        matchingFeeds = self.mRssFeedList.getFeedsByTitle(cleanInput, server, destination_obj)
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

    def passive_run(self, event, full_line, server_obj, user_obj=None, channel_obj=None):
        """
        Replies to an event not directly addressed to the bot.
        :param event: string
        :param full_line: string
        :param server_obj: Server
        :param user_obj: User
        :param channel_obj: Channel
        """
        hallo = server_obj.get_hallo()
        # Check through all feeds to see which need updates
        for rssFeed in self.mRssFeedList.getFeedList():
            # Only check those which have been too long since last check
            if rssFeed.needsCheck():
                # Get new items
                newItems = rssFeed.checkFeed()
                # Output all new items
                for rssItem in newItems:
                    rssFeed.outputItem(rssItem, hallo)


class FeedAdd(Function):
    """
    Adds a new RSS feed from a link, allowing specification of server and channel.
    """
    # Name for use in help listing
    mHelpName = "rss add"
    # Names which can be used to address the function
    mNames = {"rss add", "add rss", "add rss feed", "rss feed add", "add feed", "feed add"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Adds a new feed to be checked for updates which will be posted to the current location." \
                " Format: rss add <feed name> <update period?>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj):
        # Get input
        feedUrl = line.split()[0]
        feedPeriod = "PT3600S"
        if len(line.split()) > 0:
            feedPeriod = line.split()[1]
        # Get current RSS feed list
        functionDispatcher = user_obj.get_server().get_hallo().get_function_dispatcher()
        feedCheckClass = functionDispatcher.get_function_by_name("rss check")
        feedCheckObject = functionDispatcher.get_function_object(feedCheckClass)
        feedList = feedCheckObject.mRssFeedList
        # Check link works
        try:
            Commons.load_url_string(feedUrl, [])
        except urllib.error.URLError:
            return "Could not load link."
        # Check period is valid
        try:
            feedDelta = Commons.load_time_delta(feedPeriod)
        except ISO8601ParseError:
            return "Invalid time period."
        # Create new rss feed
        rssFeed = RssFeed()
        rssFeed.mServerName = user_obj.get_server().get_name()
        rssFeed.mUrl = feedUrl
        rssFeed.mUpdateFrequency = feedDelta
        if destination_obj == user_obj:
            rssFeed.mChannelName = destination_obj.get_name()
        else:
            rssFeed.mUserName = user_obj.get_name()
        # Update feed
        try:
            rssFeed.checkFeed()
        except ParseError:
            return "RSS feed could not be parsed."
        # Add new rss feed to list
        feedList.addFeed(rssFeed)
        # Save list
        feedList.to_xml()
        # Return output
        return "I have added new RSS feed titled \"" + rssFeed.mTitle + "\""


class FeedRemove(Function):
    """
    Remove an RSS feed and no longer receive updates from it.
    """
    # Name for use in help listing
    mHelpName = "rss remove"
    # Names which can be used to address the function
    mNames = {"rss remove", "rss delete", "remove rss", "delete rss", "remove rss feed", "delete rss feed",
              "rss feed remove", "rss feed delete", "remove feed", "delete feed", "feed remove", "feed delete"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Removes a specified RSS feed from the current or specified channel. " \
                " Format: rss remove <feed title or url>"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.get_server()
        hallo = server.get_hallo()
        functionDispatcher = hallo.get_function_dispatcher()
        feedCheckFunction = functionDispatcher.get_function_by_name("rss check")
        rssFeedList = feedCheckFunction.mRssFeedList
        # Clean up input
        cleanInput = line.strip()
        # Find any feeds with specified title
        testFeeds = rssFeedList.getFeedsByTitle(cleanInput.lower(), server, destination_obj)
        if len(testFeeds) == 1:
            rssFeedList.remove(testFeeds[0])
            return "Removed \"" + testFeeds[0].mTitle + "\" RSS feed. Updates will no longer be sent to " \
                   + next(testFeeds[0].mChannelName, testFeeds[0].mUserName) + "."
        if len(testFeeds) > 1:
            return "There is more than 1 rss feed in this channel by that name. Try specifying by URL."
        # Otherwise, zero results, so try hunting by url
        testFeeds = rssFeedList.getFeedsByURL(cleanInput, server, destination_obj)
        if len(testFeeds) == 0:
            return "There are no RSS feeds in this channel matching that name or URL."
        for testFeed in testFeeds:
            rssFeedList.remove(testFeed)
        return "Removed subscriptions to RSS feed."


class FeedList(Function):
    """
    Remove an RSS feed and no longer receive updates from it.
    """
    # Name for use in help listing
    mHelpName = "rss list"
    # Names which can be used to address the function
    mNames = {"rss list", "list rss", "list rss feed", "list rss feeds", "rss feed list", "rss feeds list",
              "list feed", "list feeds", "feed list", "feeds list"}
    # Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Lists RSS feeds for the current channel. Format: rss list"

    def __init__(self):
        """
        Constructor
        """
        pass

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.get_server()
        hallo = server.get_hallo()
        functionDispatcher = hallo.get_function_dispatcher()
        feedCheckFunction = functionDispatcher.get_function_by_name("rss check")
        rssFeedList = feedCheckFunction.mRssFeedList
        # Find list of feeds for current channel.
        destFeeds = rssFeedList.getFeedsByDestination(server, destination_obj)
        if len(destination_obj) == 0:
            return "There are no RSS feeds posting to this destination."
        outputLines = ["RSS feeds posting to this channel:"]
        for rssFeed in destFeeds:
            outputLines.append("\""+rssFeed.mTitle+"\" url: "+rssFeed.mUrl)
        return "".join(outputLines)
