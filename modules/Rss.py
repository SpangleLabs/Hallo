from xml.etree.ElementTree import ParseError
from xml.etree import ElementTree
from datetime import datetime
from inc.Commons import Commons
import hashlib
from Function import Function
import urllib.error
from inc.Commons import ISO8601ParseError


class RssFeedList:
    """
    Holds the lists of feeds, for loading and unloading.
    """

    def __init__(self):
        self.feed_list = []

    def add_feed(self, new_feed):
        """
        Adds a new RSS feed to the list.
        :param new_feed: RssFeed to add
        :type new_feed: RssFeed
        """
        self.feed_list.append(new_feed)

    def remove_feed(self, remove_feed):
        """
        Removes an RSS feed from the list.
        :param remove_feed: RssFeed to remove
        :type remove_feed: RssFeed
        """
        self.feed_list.remove(remove_feed)

    def get_feeds_by_destination(self, destination):
        """
        Returns a list of feeds matching a specified destination.
        :param destination: Channel or User which RssFeed is posting to
        :type destination: Destination.Destination
        :return: list<RssFeed> list of RssFeeds matching destination
        """
        matching_feeds = []
        for rss_feed in self.feed_list:
            if destination.server.name != rss_feed.server_name.lower():
                continue
            if destination.is_channel() and destination.name != rss_feed.channel_name:
                continue
            if destination.is_user() and destination.name != rss_feed.user_name:
                continue
            matching_feeds.append(rss_feed)
        return matching_feeds

    def get_feeds_by_title(self, title, destination):
        """
        Returns a list of feeds matching a specified title
        :param title: Title of the RssFeed being searched for
        :type title: str
        :param destination: Channel or User which RssFeed is posting to
        :type destination: Destination.Destination
        :return: list<RssFeed>
        """
        title_clean = title.lower().strip()
        matching_feeds = []
        for rss_feed in self.get_feeds_by_destination(destination):
            if title_clean == rss_feed.title.lower().strip():
                matching_feeds.append(rss_feed)
        return matching_feeds

    def get_feeds_by_url(self, url, destination):
        """
        Returns a list of feeds matching a specified title
        :param url: URL of RSS feed to search for
        :param destination: Channel or User which RssFeed is posting to
        :return: list<RssFeed> List of RSS feeds matching specified URL
        """
        url_clean = url.strip()
        matching_feeds = []
        for rss_feed in self.get_feeds_by_destination(destination):
            if url_clean == rss_feed.url.strip():
                matching_feeds.append(rss_feed)
        return matching_feeds

    def to_xml(self):
        """
        Saves the whole feed list to XML file
        :return:
        """
        # Create root element
        root_elem = ElementTree.Element("rss_feeds")
        # Add all feed elements
        for rss_feed_obj in self.feed_list:
            new_feed_elem = ElementTree.fromstring(rss_feed_obj.to_xml_string())
            root_elem.append(new_feed_elem)
        # Write xml to file
        ElementTree.ElementTree(root_elem).write("store/rss_feeds.xml")

    @staticmethod
    def from_xml():
        """
        Constructs a new RssFeedList from the XML file
        :return: RssFeedList
        """
        new_feed_list = RssFeedList()
        # Try loading xml file, otherwise return blank list
        try:
            doc = ElementTree.parse("store/rss_feeds.xml")
        except (OSError, IOError):
            return new_feed_list
        # Loop feeds in xml file adding them to list
        root = doc.getroot()
        for rss_feed_elem in root.findall("rss_feed"):
            new_feed_obj = RssFeed.from_xml_string(ElementTree.tostring(rss_feed_elem))
            new_feed_list.add_feed(new_feed_obj)
        return new_feed_list


class RssFeed:
    """
    Class representing an rss feed in config.
    """

    def __init__(self):
        self.title = ""
        self.url = None
        self.server_name = None
        self.channel_name = None
        self.user_name = None
        self.last_item_hash = None
        self.last_check = None
        self.update_frequency = None

    def check_feed(self):
        """
        Checks the feed for any updates
        :return: list of ElementTree XML elements
        """
        rss_data = Commons.load_url_string(self.url)
        rss_elem = ElementTree.fromstring(rss_data)
        channel_elem = rss_elem.find("channel")
        new_items = []
        # Update title
        title_elem = channel_elem.find("title")
        self.title = title_elem.text
        # Loop elements, seeing when any match the last item's hash
        latest_hash = None
        for item_elem in channel_elem.findall("item"):
            item_xml = ElementTree.tostring(item_elem)
            item_hash = hashlib.md5(item_xml).hexdigest()
            if latest_hash is None:
                latest_hash = item_hash
            if item_hash == self.last_item_hash:
                break
            new_items.append(item_elem)
        # Update last item hash
        self.last_item_hash = latest_hash
        self.last_check = datetime.now()
        # Return new items
        return new_items

    def output_item(self, rss_item, hallo, server=None, destination=None):
        """
        Outputs an item to a given server and destination, or the feed default.
        :param rss_item: ElementTree.Element rss item xml element which wants outputting
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
            if self.channel_name is not None:
                destination = server.get_channel_by_name(self.channel_name)
            if self.user_name is not None:
                destination = server.get_user_by_name(self.user_name)
            if destination is None:
                return "Error, invalid destination."
        # Construct output
        output = self.format_item(rss_item)
        server.send(output, destination)
        return output

    def format_item(self, rss_item):
        """
        Formats an rss feed item for output.
        :param rss_item: ElementTree.Element rss item xml element to format
        :return: string
        """
        # Load item xml
        item_title = rss_item.find("title").text
        item_link = rss_item.find("link").text
        # Construct output
        output = "Update on \"" + self.title + "\" RSS feed. \"" + item_title + "\" " + item_link
        return output

    def needs_check(self):
        """
        Returns whether an rssfeed check is overdue.
        :return: bool
        """
        if self.last_check is None:
            return True
        if datetime.now() > self.last_check + self.update_frequency:
            return True
        return False

    def to_xml_string(self):
        """
        Saves this RssFeed
        :return: string
        """
        # Create root element
        root = ElementTree.Element("rss_feed")
        # Create title element
        title = ElementTree.SubElement(root, "title")
        title.text = self.title
        # Create url element
        url = ElementTree.SubElement(root, "url")
        url.text = self.url
        # Create server name element
        server = ElementTree.SubElement(root, "server")
        server.text = self.server_name
        # Create channel name element, if applicable
        if self.channel_name is not None:
            channel = ElementTree.SubElement(root, "channel")
            channel.text = self.channel_name
        # Create user name element, if applicable
        if self.user_name is not None:
            user = ElementTree.SubElement(root, "user")
            user.text = self.user_name
        # Create last item element
        if self.last_item_hash is not None:
            last_item = ElementTree.SubElement(root, "last_item")
            last_item.text = self.last_item_hash
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
        Loads new RssFeed object from XML string
        :param xml_string: string
        :return: RssFeed
        """
        # Create blank feed
        new_feed = RssFeed()
        # Load xml
        feed_xml = ElementTree.fromstring(xml_string)
        # Load title, url, server
        new_feed.title = feed_xml.find("title").text
        new_feed.url = feed_xml.find("url").text
        new_feed.server_name = feed_xml.find("server").text
        # Load channel or user
        if feed_xml.find("channel") is not None:
            new_feed.channel_name = feed_xml.find("channel").text
        else:
            if feed_xml.find("user") is not None:
                new_feed.user_name = feed_xml.find("user").text
            else:
                raise Exception("Channel or user must be defined")
        # Load last item
        if feed_xml.find("last_item") is not None:
            new_feed.last_item_hash = feed_xml.find("last_item").text
        # Load last check
        if feed_xml.find("last_check") is not None:
            new_feed.last_check = datetime.strptime(feed_xml.find("last_check").text, "%Y-%m-%dT%H:%M:%S.%f")
        # Load update frequency
        new_feed.update_frequency = Commons.load_time_delta(feed_xml.find("update_frequency").text)
        # Return new feed
        return new_feed


class FeedCheck(Function):
    """
    Checks a specified feed for updates and returns them.
    """

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "rss check"
        # Names which can be used to address the function
        self.names = {"rss check", "check rss", "check rss feed", "rss feed check", "check feed", "feed check"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Checks a specified feed for updates and returns them. Format: rss check <feed name>"
        self.rss_feed_list = RssFeedList.from_xml()

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
        self.rss_feed_list.to_xml()

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {Function.EVENT_MINUTE}

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        hallo = user_obj.server.hallo
        # Clean up input
        clean_input = line.strip().lower()
        # Check whether input is asking to update all feeds
        if clean_input in self.NAMES_ALL:
            return self.run_all(hallo)
        # Otherwise see if a feed title matches the specified one
        matching_feeds = self.rss_feed_list.get_feeds_by_title(clean_input, destination_obj)
        if len(matching_feeds) == 0:
            return "Error, no Rss Feeds match that name. If you're adding a new feed, use \"rss add\" with your link."
        output_lines = []
        # Loop through matching rss feeds, getting updates
        for rss_feed in matching_feeds:
            new_items = rss_feed.check_feed()
            for rss_item in new_items:
                output_lines.append(rss_feed.format_item(rss_item))
        # Remove duplicate entries from output_lines
        output_lines = list(set(output_lines))
        # Output response to user
        if len(output_lines) == 0:
            return "There were no updates for \"" + line + "\" RSS feed."
        return "The following feed updates were found:\n" + "\n".join(output_lines)

    def run_all(self, hallo):
        output_lines = []
        for rss_feed in self.rss_feed_list.feed_list:
            new_items = rss_feed.check_feed()
            for rss_item in new_items:
                output_lines.append(rss_feed.output_item(rss_item, hallo))
        # Remove duplicate entries from output_lines
        output_lines = list(set(output_lines))
        # Output response to user
        if len(output_lines) == 0:
            return "There were no feed updates."
        return "The following feed updates were found and posted to their registered destinations:\n" + \
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
        for rss_feed in self.rss_feed_list.feed_list:
            # Only check those which have been too long since last check
            if rss_feed.needs_check():
                # Get new items
                new_items = rss_feed.check_feed()
                # Output all new items
                for rss_item in new_items:
                    rss_feed.output_item(rss_item, hallo_obj)


class FeedAdd(Function):
    """
    Adds a new RSS feed from a link, allowing specification of server and channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "rss add"
        # Names which can be used to address the function
        self.names = {"rss add", "add rss", "add rss feed", "rss feed add", "add feed", "feed add"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new feed to be checked for updates which will be posted to the current location." \
                         " Format: rss add <feed name> <update period?>"

    def run(self, line, user_obj, destination_obj):
        # Get input
        feed_url = line.split()[0]
        feed_period = "PT3600S"
        if len(line.split()) > 1:
            feed_period = line.split()[1]
        # Get current RSS feed list
        function_dispatcher = user_obj.server.hallo.function_dispatcher
        feed_check_class = function_dispatcher.get_function_by_name("rss check")
        feed_check_obj = function_dispatcher.get_function_object(feed_check_class)
        feed_list = feed_check_obj.rss_feed_list
        # Check link works
        try:
            Commons.load_url_string(feed_url, [])
        except urllib.error.URLError:
            return "Error, could not load link."
        # Check period is valid
        try:
            feed_delta = Commons.load_time_delta(feed_period)
        except ISO8601ParseError:
            return "Error, invalid time period."
        # Create new rss feed
        rss_feed = RssFeed()
        rss_feed.server_name = user_obj.server.name
        rss_feed.url = feed_url
        rss_feed.update_frequency = feed_delta
        if destination_obj.is_channel():
            rss_feed.channel_name = destination_obj.name
        else:
            rss_feed.user_name = destination_obj.name
        # Update feed
        try:
            rss_feed.check_feed()
        except ParseError:
            return "Error, RSS feed could not be parsed."
        # Add new rss feed to list
        feed_list.add_feed(rss_feed)
        # Save list
        feed_list.to_xml()
        # Return output
        return "I have added new RSS feed titled \"" + rss_feed.title + "\""


class FeedRemove(Function):
    """
    Remove an RSS feed and no longer receive updates from it.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "rss remove"
        # Names which can be used to address the function
        self.names = {"rss remove", "rss delete", "remove rss", "delete rss", "remove rss feed", "delete rss feed",
                      "rss feed remove", "rss feed delete", "remove feed", "delete feed", "feed remove", "feed delete"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a specified RSS feed from the current or specified channel. " \
                         " Format: rss remove <feed title or url>"

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.get_server()
        hallo = server.get_hallo()
        function_dispatcher = hallo.get_function_dispatcher()
        feed_check_function = function_dispatcher.get_function_by_name("rss check")
        feed_check_obj = function_dispatcher.get_function_object(feed_check_function)
        rss_feed_list = feed_check_obj.rss_feed_list
        # Clean up input
        clean_input = line.strip()
        # Find any feeds with specified title
        test_feeds = rss_feed_list.get_feeds_by_title(clean_input.lower(), destination_obj)
        if len(test_feeds) == 1:
            rss_feed_list.remove_feed(test_feeds[0])
            return "Removed \"" + test_feeds[0].title + "\" RSS feed. Updates will no longer be sent to " \
                   + (test_feeds[0].channel_name or test_feeds[0].user_name) + "."
        if len(test_feeds) > 1:
            return "Error, there is more than 1 rss feed in this channel by that name. Try specifying by URL."
        # Otherwise, zero results, so try hunting by url
        test_feeds = rss_feed_list.get_feeds_by_url(clean_input, destination_obj)
        if len(test_feeds) == 0:
            return "Error, there are no RSS feeds in this channel matching that name or URL."
        for test_feed in test_feeds:
            rss_feed_list.remove_feed(test_feed)
        return "Removed subscriptions to RSS feed."


class FeedList(Function):
    """
    Lists the currently active RSS feed subscriptions
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "rss list"
        # Names which can be used to address the function
        self.names = {"rss list", "list rss", "list rss feed", "list rss feeds", "rss feed list", "rss feeds list",
                      "list feed", "list feeds", "feed list", "feeds list"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Lists RSS feeds for the current channel. Format: rss list"

    def run(self, line, user_obj, destination_obj=None):
        # Handy variables
        server = user_obj.get_server()
        hallo = server.get_hallo()
        function_dispatcher = hallo.get_function_dispatcher()
        feed_check_function = function_dispatcher.get_function_by_name("rss check")
        feed_check_obj = function_dispatcher.get_function_object(feed_check_function)
        rss_feed_list = feed_check_obj.rss_feed_list
        # Find list of feeds for current channel.
        dest_feeds = rss_feed_list.get_feeds_by_destination(destination_obj)
        if len(dest_feeds) == 0:
            return "There are no RSS feeds posting to this destination."
        output_lines = ["RSS feeds posting to this channel:"]
        for rss_feed in dest_feeds:
            output_lines.append("\""+rss_feed.title + "\" url: " + rss_feed.url)
        return "\n".join(output_lines)
