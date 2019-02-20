import hashlib
import json
import re
from abc import ABCMeta
from datetime import datetime, timedelta
from threading import Lock
from xml.etree import ElementTree

from Destination import Channel, User
from Events import EventMessageWithPhoto, EventMessage, EventMinute
from Function import Function
from inc.Commons import Commons, ISO8601ParseError


class SubscriptionException(Exception):
    pass


class SubscriptionRepo:
    """
    Holds the lists of subscriptions, for loading and unloading.
    """

    def __init__(self):
        self.sub_list = []
        """ :type : list[Subscription]"""
        self.common_list = []
        """ :type : list[SubscriptionCommon]"""
        self.sub_lock = Lock()
        """ :type : threading.Lock"""

    def add_sub(self, new_sub):
        """
        Adds a new Subscription to the list.
        :param new_sub: New subscription to add
        :type new_sub: Subscription
        """
        self.sub_list.append(new_sub)

    def remove_sub(self, remove_sub):
        """
        Removes a Subscription from the list.
        :param remove_sub: Existing subscription to remove
        :type remove_sub: Subscription
        """
        self.sub_list.remove(remove_sub)

    def get_subs_by_destination(self, destination):
        """
        Returns a list of subscriptions matching a specified destination.
        :param destination: Channel or User which E621Sub is posting to
        :type destination: Destination.Destination
        :return: list of Subscription objects matching destination
        :rtype: list [Subscription]
        """
        matching_subs = []
        for sub in self.sub_list:
            if sub.destination != destination:
                continue
            matching_subs.append(sub)
        return matching_subs

    def get_subs_by_name(self, name, destination):
        """
        Returns a list of subscriptions matching a specified name, be that a type and search, or just a type
        :param name: Search of the Subscription being searched for
        :type name: str
        :param destination: Channel or User which Subscription is posting to
        :type destination: Destination.Destination
        :return: List of matching subscriptions
        :rtype: list [Subscription]
        """
        name_clean = name.lower().strip()
        matching_subs = []
        for sub in self.get_subs_by_destination(destination):
            if sub.matches_name(name_clean):
                matching_subs.append(sub)
        return matching_subs

    def get_common_config_by_type(self, common_type):
        """
        Returns the common configuration object for a given type.
        There should be only 1 common config object of each type.
        :param common_type: The class of the common config object being searched for
        :type common_type: type
        :return: The object, or a new object if none was found.
        :rtype: SubscriptionCommon
        """
        if not issubclass(common_type, SubscriptionCommon):
            raise SubscriptionException("This common type, {}, is not a subclass of SubscriptionCommon"
                                        .format(common_type.__name__))
        matching = [obj for obj in self.common_list if isinstance(obj, common_type)]
        if len(matching) == 0:
            new_common = common_type()
            self.common_list.append(new_common)
            return new_common
        if len(matching) == 1:
            return matching[0]
        raise SubscriptionException("More than one subscription common config exists for the type: {}"
                                    .format(common_type.__name__))

    def save_json(self):
        """
        Saves the whole subscription list to a JSON file
        :return: None
        """
        json_obj = {"subs": []}
        # Add subscriptions
        for sub in self.sub_list:
            json_obj["subs"].append(sub.to_json())
        # Add common configuration
        json_obj["common"] = []
        for common in self.common_list:
            common_json = common.to_json()
            if common_json is not None:
                json_obj["common"].append(common_json)
        # Write json to file
        with open("store/subscriptions.json", "w") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json(hallo):
        """
        Constructs a new SubscriptionRepo from the JSON file
        :return: Newly constructed list of subscriptions
        :rtype: SubscriptionRepo
        """
        new_sub_list = SubscriptionRepo()
        # Try loading json file, otherwise return blank list
        try:
            with open("store/subscriptions.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            return new_sub_list
        # Loop common objects in json file adding them to list.
        # Common config must be loaded first, as subscriptions use it.
        for common_elem in json_obj["common"]:
            new_common_obj = SubscriptionFactory.common_from_json(common_elem)
            new_sub_list.common_list.append(new_common_obj)
        # Loop subs in json file adding them to list
        for sub_elem in json_obj["subs"]:
            new_sub_obj = SubscriptionFactory.from_json(sub_elem, hallo, new_sub_list)
            new_sub_list.add_sub(new_sub_obj)
        return new_sub_list


class Subscription(metaclass=ABCMeta):
    names = []
    """ :type : list[str]"""
    type_name = ""
    """ :type : str"""

    def __init__(self, server, destination, last_check=None, update_frequency=None):
        """
        :type server: Server.Server
        :type destination: Destination.Destination
        :type last_check: datetime
        :type update_frequency: timedelta
        """
        if update_frequency is None:
            update_frequency = Commons.load_time_delta("PT300S")
        self.server = server
        """ :type : Server.Server"""
        self.destination = destination
        """ :type : Destination.Destination"""
        self.last_check = last_check
        """ :type : datetime"""
        self.update_frequency = update_frequency
        """ :type : timedelta"""
        self.last_update = None
        """ :type : datetime | None"""

    @staticmethod
    def create_from_input(input_evt, sub_repo):
        """
        Creates a new subscription object from a user's input line
        :type input_evt: EventMessage
        :type sub_repo: SubscriptionRepo
        :rtype: Subscription
        """
        raise NotImplementedError()

    def matches_name(self, name_clean):
        """
        Returns whether a user input string matches this subscription object
        :type name_clean: str
        :rtype: bool
        """
        raise NotImplementedError()

    def get_name(self):
        """
        Returns a printable name for the subscription
        :rtype: str
        """
        raise NotImplementedError()

    def check(self):
        """
        Checks the subscription, and returns a list of update objects, in whatever format that
        format_item() would like to receive them.
        The list should be ordered from oldest to newest.
        :rtype: list[object]
        """
        raise NotImplementedError()

    def send_item(self, item):
        """
        :type item: object
        :rtype: None
        """
        self.last_update = datetime.now()
        output_evt = self.format_item(item)
        self.server.send(output_evt)

    def format_item(self, item):
        """
        Formats an item, as returned from check(), into an event that can be sent out
        :type item: Any
        :rtype: Events.EventMessage
        """
        raise NotImplementedError()

    def needs_check(self):
        """
        Returns whether a subscription check is overdue.
        :rtype: bool
        """
        if self.last_check is None:
            return True
        if datetime.now() > self.last_check + self.update_frequency:
            return True
        return False

    def to_json(self):
        """
        :rtype: dict
        """
        json_obj = dict()
        json_obj["server_name"] = self.server.name
        if isinstance(self.destination, Channel):
            json_obj["channel_address"] = self.destination.address
        if isinstance(self.destination, User):
            json_obj["user_address"] = self.destination.address
        if self.last_check is not None:
            json_obj["last_check"] = self.last_check.isoformat()
        json_obj["update_frequency"] = Commons.format_time_delta(self.update_frequency)
        if self.last_update is not None:
            json_obj["last_update"] = self.last_update.isoformat()
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo, sub_repo):
        """
        :type json_obj: dict
        :type hallo: Hallo.Hallo
        :type sub_repo: SubscriptionRepo
        :rtype: Subscription
        """
        raise NotImplementedError()


class RssSub(Subscription):
    names = ["rss", "rss feed"]
    """ :type : list[str]"""
    type_name = "rss"
    """ :type : str"""

    def __init__(self, server, destination, url, last_check=None, update_frequency=None,
                 title=None, last_item_hash=None):
        """
        :type server: Server.Server
        :type destination: Destination.Destination
        :type url: str
        :type last_check: datetime | None
        :type update_frequency: timedelta | None
        :type title: str | None
        :param last_item_hash: GUID or md5 of latest item in rss feed
        :type last_item_hash: str | None
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.url = url
        """ :type : str"""
        if title is None:
            rss_data = self.get_rss_data()
            rss_elem = ElementTree.fromstring(rss_data)
            channel_elem = rss_elem.find("channel")
            # Update title
            title_elem = channel_elem.find("title")
            title = title_elem.text
        self.title = title if title is not None else "No title"
        """ :type : str"""
        self.last_item_hash = last_item_hash
        """ :type : str | None"""

    def get_rss_data(self):
        headers = None
        # Tumblr feeds need "GoogleBot" in the URL, or they'll give a GDPR notice
        if "tumblr.com" in self.url:
            headers = [["User-Agent", "Hallo IRCBot hallo@dr-spangle.com (GoogleBot/4.5.1)"]]
        # Actually get the data
        rss_data = Commons.load_url_string(self.url, headers)
        # PHDComics doesn't always escape ampersands correctly
        if "phdcomics" in self.url:
            rss_data = rss_data.replace("& ", "&amp; ")
        # Chainsaw suit has a blank first line
        if "chainsawsuit" in self.url and rss_data.startswith("\r\n"):
            rss_data = rss_data[2:]
        return rss_data

    @staticmethod
    def create_from_input(input_evt, sub_repo):
        server = input_evt.server
        destination = input_evt.channel if input_evt.channel is not None else input_evt.user
        # Get user specified stuff
        feed_url = input_evt.command_args.split()[0]
        feed_period = "PT600S"
        if len(input_evt.command_args.split()) > 1:
            feed_period = input_evt.command_args.split()[1]
        try:
            feed_delta = Commons.load_time_delta(feed_period)
        except ISO8601ParseError:
            feed_delta = Commons.load_time_delta("PT600S")
        try:
            rss_sub = RssSub(server, destination, feed_url, update_frequency=feed_delta)
            rss_sub.check()
        except Exception as e:
            raise SubscriptionException("Failed to create RSS subscription", e)
        return rss_sub

    def matches_name(self, name_clean):
        return name_clean in [self.title.lower().strip(), self.url.lower().strip(), self.get_name().lower().strip()]

    def get_name(self):
        return "{} ({})".format(self.title, self.url)

    def check(self):
        rss_data = self.get_rss_data()
        rss_elem = ElementTree.fromstring(rss_data)
        channel_elem = rss_elem.find("channel")
        new_items = []
        # Update title
        title_elem = channel_elem.find("title")
        title_text = title_elem.text
        self.title = title_text if title_text is not None else "No title"
        # Loop elements, seeing when any match the last item's hash
        latest_hash = None
        for item_elem in channel_elem.findall("item"):
            item_guid_elem = item_elem.find("guid")
            if item_guid_elem is not None:
                item_hash = item_guid_elem.text
            else:
                item_link_elem = item_elem.find("link")
                if item_link_elem is not None:
                    item_hash = item_link_elem.text
                else:
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
        return new_items[::-1]

    def format_item(self, rss_item):
        # Load item xml
        item_title = rss_item.find("title").text
        item_link = rss_item.find("link").text
        # Construct output
        output = "Update on \"{}\" RSS feed. \"{}\" {}".format(self.title, item_title, item_link)
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self):
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["title"] = self.title
        json_obj["url"] = self.url
        json_obj["last_item"] = self.last_item_hash
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo, sub_repo):
        server = hallo.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException("Could not find server with name \"{}\"".format(json_obj["server_name"]))
        # Load channel or user
        if "channel_address" in json_obj:
            destination = server.get_channel_by_address(json_obj["channel_address"])
        else:
            if "user_address" in json_obj:
                destination = server.get_user_by_address(json_obj["user_address"])
            else:
                raise SubscriptionException("Channel or user must be defined.")
        if destination is None:
            raise SubscriptionException("Could not find chanel or user.")
        # Load last check
        last_check = None
        if "last_check" in json_obj:
            last_check = datetime.strptime(json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f")
        # Load update frequency
        update_frequency = Commons.load_time_delta(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f")
        # Type specific loading
        # Load last items
        url = json_obj["url"]
        title = json_obj["title"]
        last_hash = json_obj["last_item"]
        new_sub = RssSub(server, destination, url, last_check, update_frequency, title, last_hash)
        new_sub.last_update = last_update
        return new_sub


class GoogleDocsSub(Subscription):
    pass


class TwitterSub(Subscription):
    pass


class YoutubeSub(Subscription):
    pass


class ImgurSub(Subscription):
    pass


class RedditSub(Subscription):
    names = ["reddit", "subreddit"]
    """ :type : list[str]"""
    type_name = "subreddit"

    def __init__(self, server, destination, subreddit, last_check=None, update_frequency=None, latest_ids=None):
        """
        :type server: Server.Server
        :type destination: Destination.Destination
        :type subreddit: str
        :type last_check: datetime
        :type update_frequency: timedelta
        :type latest_ids: list[str]
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.subreddit = subreddit
        """ :type : str"""
        if latest_ids is None:
            latest_ids = []
        self.latest_ids = latest_ids
        """ :type : list[int]"""

    @staticmethod
    def create_from_input(input_evt, sub_repo):
        # Get event data
        server = input_evt.server
        destination = input_evt.channel if input_evt.channel is not None else input_evt.user
        clean_text = input_evt.command_args.strip().lower()
        text_split = clean_text.split()
        # Subreddit regex
        sub_regex = re.compile("r/([^\s]*)/?")
        if len(text_split) == 1:
            sub_name = clean_text if sub_regex.search(clean_text) is None else sub_regex.search(clean_text).group(1)
            reddit_sub = RedditSub(server, destination, sub_name)
            reddit_sub.check()
            return reddit_sub
        if len(text_split) > 2:
            raise SubscriptionException("Too many arguments. Please give a subreddit, and optionally, a check period.")
        try:
            search_delta = Commons.load_time_delta(text_split[0])
            subreddit = text_split[1]
        except ISO8601ParseError:
            subreddit = text_split[0]
            search_delta = Commons.load_time_delta(text_split[1])
        sub_name = clean_text if sub_regex.search(subreddit) is None else sub_regex.search(subreddit).group(1)
        reddit_sub = RedditSub(server, destination, sub_name, update_frequency=search_delta)
        reddit_sub.check()
        return reddit_sub

    def matches_name(self, name_clean):
        return self.subreddit == name_clean or "r/{}".format(self.subreddit) in name_clean

    def get_name(self):
        return "/r/{}".format(self.subreddit)

    def check(self):
        url = "https://www.reddit.com/r/{}/new.json".format(self.subreddit)
        results = Commons.load_url_json(url)
        return_list = []
        new_last_ten = []
        for result in results["data"]["children"]:
            result_id = result["data"]["name"]
            # If post hasn't been seen in the latest ten, add it to returned list.
            if result_id not in self.latest_ids:
                new_last_ten.append(result_id)
                return_list.append(result)
            else:
                break
        self.latest_ids = (self.latest_ids + new_last_ten[::-1])[-10:]
        # Update check time
        self.last_check = datetime.now()
        return return_list

    def format_item(self, item):
        # Event destination
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        # Item data
        link = "https://reddit.com/r/{}/comments/{}/".format(self.subreddit, item["data"]["id"])
        title = item["data"]["title"]
        author = item["data"]["author"]
        url = item["data"]["url"]
        # Check if link is direct to a media file, if so, add photo to output message
        file_extension = url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif", "mp4", "gifv"]:
            if file_extension == "gifv":
                url = url[:-4]+"mp4"
            # Make output message
            output = "Update on /r/{}/ subreddit. \"{}\" by u/{} {}".format(self.subreddit, title, author, link)
            output_evt = EventMessageWithPhoto(self.server, channel, user, output, url, inbound=False)
            return output_evt
        # Handle gfycat links as photos
        gfycat_regex = re.compile("(?:https?://)?(?:www\.)?gfycat.com/([a-z]+)")
        gfycat_match = gfycat_regex.match(url)
        if gfycat_match is not None:
            direct_url = "https://giant.gfycat.com/{}.mp4".format(gfycat_match.group(1))
            # Make output message
            output = "Update on /r/{}/ subreddit. \"{}\" by u/{} {}".format(self.subreddit, title, author, link)
            output_evt = EventMessageWithPhoto(self.server, channel, user, output, direct_url, inbound=False)
            return output_evt
        # Make output message if the link isn't direct to a media file
        if item["data"]["selftext"] != "":
            output = "Update on /r/{}/ subreddit. \"{}\" by u/{} {}".format(self.subreddit, title, author, link)
        else:
            output = "Update on /r/{}/ subreddit. \"{}\" by u/{} {}\n{}".format(self.subreddit, title, author, url, link)
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self):
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["subreddit"] = self.subreddit
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo, sub_repo):
        server = hallo.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException("Could not find server with name \"{}\"".format(json_obj["server_name"]))
        # Load channel or user
        if "channel_address" in json_obj:
            destination = server.get_channel_by_address(json_obj["channel_address"])
        else:
            if "user_address" in json_obj:
                destination = server.get_user_by_address(json_obj["user_address"])
            else:
                raise SubscriptionException("Channel or user must be defined.")
        if destination is None:
            raise SubscriptionException("Could not find chanel or user.")
        # Load last check
        last_check = None
        if "last_check" in json_obj:
            last_check = datetime.strptime(json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f")
        # Load update frequency
        update_frequency = Commons.load_time_delta(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f")
        # Type specific loading
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        subreddit = json_obj["subreddit"]
        new_sub = RedditSub(server, destination, subreddit, last_check, update_frequency, latest_ids)
        new_sub.last_update = last_update
        return new_sub


class SubscriptionCommon:
    type_name = ""
    """ :type : str"""

    def to_json(self):
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj):
        raise NotImplementedError()


class SubscriptionFactory(object):
    sub_classes = [RssSub, RedditSub]
    """ :type : list[type.Subscription]"""
    common_classes = []
    """ :type : list[type.SubscriptionCommon]"""

    @staticmethod
    def get_names():
        return [name for sub_class in SubscriptionFactory.sub_classes for name in sub_class.names]

    @staticmethod
    def get_class_by_name(name):
        classes = [sub_class for sub_class in SubscriptionFactory.sub_classes if name in sub_class.names]
        if len(classes) != 1:
            raise SubscriptionException("Failed to find a subscription type matching the name {}".format(name))
        return classes[0]

    @staticmethod
    def from_json(sub_json, hallo, sub_repo):
        """
        :type sub_json: dict
        :type hallo: Hallo.Hallo
        :type sub_repo: SubscriptionRepo
        :rtype: Subscription
        """
        sub_type_name = sub_json["sub_type"]
        for sub_class in SubscriptionFactory.sub_classes:
            if sub_class.type_name == sub_type_name:
                return sub_class.from_json(sub_json, hallo, sub_repo)
        raise SubscriptionException("Could not load subscription of type {}".format(sub_type_name))

    @staticmethod
    def common_from_json(common_json):
        """
        :type common_json: dict
        :rtype: SubscriptionCommon
        """
        common_type_name = common_json["common_type"]
        for common_class in SubscriptionFactory.common_classes:
            if common_class.type_name == common_type_name:
                return common_class.from_json(common_json)
        raise SubscriptionException("Could not load common configuration of type {}".format(common_type_name))


class SubscriptionAdd(Function):
    """
    Adds a new subscription, allowing specification of server and channel.
    """
    add_words = ["add"]
    sub_words = ["sub", "subscription"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "add subscription"
        # Names which can be used to address the function
        name_templates = {"{0} {1}", "{1} {0}",
                          "{1} {0} {2}", "{1} {2} {0}", "{2} {0} {1}", "{0} {2} {1}"}
        self.names = set([template.format(name, add, sub)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates
                          for add in self.add_words
                          for sub in self.sub_words])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new subscription to be checked for updates which will be posted to the current " \
                         "location." \
                         " Format: add subscription <sub type> <sub details> <update period?>"

    def run(self, event):
        # Construct type name
        sub_type_name = " ".join([w for w in event.command_name.lower().split()
                                  if w not in self.sub_words + self.add_words]).strip()
        # Get class from sub type name
        sub_class = SubscriptionFactory.get_class_by_name(sub_type_name)
        # Get current RSS feed list
        function_dispatcher = event.server.hallo.function_dispatcher
        sub_check_class = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_class)  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(event.server.hallo)
        # Create new subscription
        sub_obj = sub_class.create_from_input(event, sub_repo)
        # Acquire lock and save sub
        with sub_repo.sub_lock:
            # Add new subscription to list
            sub_repo.add_sub(sub_obj)
            # Save list
            sub_repo.save_json()
        # Send response
        return event.create_response("Created a new {} subscription for {}".format(sub_class.type_name,
                                                                                   sub_obj.get_name()))


class SubscriptionRemove(Function):
    """
    Remove an RSS feed and no longer receive updates from it.
    """
    remove_words = ["remove", "delete"]
    sub_words = ["sub", "subscription"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "remove subscription"
        # Names which can be used to address the function
        name_templates = {"{0} {1}", "{1} {0}", "{1} {2}", "{2} {1}",
                          "{1} {0} {2}", "{1} {2} {0}", "{2} {0} {1}", "{0} {2} {1}"}
        self.names = set([template.format(name, remove, sub)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates
                          for remove in self.remove_words
                          for sub in self.sub_words])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Removes a specified subscription the current location. " \
                         " Format: remove subscription <feed type> <feed title or url>"

    def run(self, event):
        # Handy variables
        server = event.server
        hallo = server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(hallo)
        # Clean up input
        clean_input = event.command_args.strip()
        # Acquire lock
        with sub_repo.sub_lock:
            # Find any feeds with specified title
            test_subs = sub_repo.get_subs_by_name(clean_input.lower(),
                                                  event.user if event.channel is None else event.channel)
            if len(test_subs) == 1:
                del_sub = test_subs[0]
                sub_repo.remove_sub(del_sub)
                return event.create_response(("Removed {} subscription to {}. "
                                             "Updates will no longer be sent to " +
                                              "{}.").format(del_sub.type_name, del_sub.get_name(),
                                                            del_sub.destination.name))
            if len(test_subs) > 1:
                for del_sub in test_subs:
                    sub_repo.remove_sub(del_sub)
                return event.create_response("Removed {} subscriptions.\n{}".
                                             format(len(test_subs),
                                                    "\n".join(
                                                        ["{} - {}".format(del_sub.type_name, del_sub.get_name())
                                                         for del_sub in test_subs]
                                                    )))
        return event.create_response("Error, there are no subscriptions in this channel matching that name.")


class SubscriptionCheck(Function):
    """
    Checks subscriptions for updates and returns them.
    """
    check_words = ["check"]
    sub_words = ["sub", "subs", "subscription", "subscriptions"]

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "check subscription"
        # Names which can be used to address the function
        name_templates = {"{0} {1}", "{1} {0}", "{1} {2}", "{2} {1}",
                          "{1} {0} {2}", "{1} {2} {0}", "{2} {0} {1}", "{0} {2} {1}"}
        self.names = set([template.format(name, check, sub)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates
                          for check in self.check_words
                          for sub in self.sub_words])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Checks a specified feed for updates and returns them. Format: subscription check <feed name>"
        self.subscription_repo = None
        """ :type : SubscriptionRepo | None"""

    def get_sub_repo(self, hallo):
        """
        :type hallo: Hallo.Hallo
        :rtype: SubscriptionRepo
        """
        if self.subscription_repo is None:
            self.subscription_repo = SubscriptionRepo.load_json(hallo)
        return self.subscription_repo

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return SubscriptionCheck()

    def save_function(self):
        """Saves the function, persistent functions only."""
        if self.subscription_repo is not None:
            self.subscription_repo.save_json()

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMinute}

    def run(self, event):
        # Handy variables
        hallo = event.server.hallo
        destination = event.user if event.channel is None else event.channel
        # Clean up input
        clean_input = event.command_args.strip().lower()
        # Acquire lock
        sub_repo = self.get_sub_repo(hallo)
        with sub_repo.sub_lock:
            # Check whether input is asking to update all e621 subscriptions
            if clean_input in self.NAMES_ALL or clean_input == "":
                matching_subs = sub_repo.sub_list
            else:
                # Otherwise see if a search subscription matches the specified one
                matching_subs = sub_repo.get_subs_by_name(clean_input, destination)
            if len(matching_subs) == 0:
                return event.create_response("Error, no subscriptions match that name.")
            found_items = 0
            # Loop through matching search subscriptions, getting updates
            for search_sub in matching_subs:
                try:
                    new_items = search_sub.check()
                    found_items += len(new_items)
                    for search_item in new_items:
                        search_sub.send_item(search_item)
                except Exception as e:
                    print("Failed to check {} subscription, \"{}\". Exception: {}".format(search_sub.type_name,
                                                                                          search_sub.get_name(),
                                                                                          e))
            # Save list
            sub_repo.save_json()
        # Output response to user
        if found_items == 0:
            return event.create_response("There were no updates for specified subscriptions.")
        return event.create_response("{} subscription updates were found.".format(found_items))

    def passive_run(self, event, hallo_obj):
        """
        Replies to an event not directly addressed to the bot.
        :type event: Events.Event
        :type hallo_obj: Hallo.Hallo
        """
        # Check through all feeds to see which need updates
        sub_repo = self.get_sub_repo(hallo_obj)
        with sub_repo.sub_lock:
            for search_sub in sub_repo.sub_list:
                # Only check those which have been too long since last check
                if search_sub.needs_check():
                    # Get new items
                    try:
                        new_items = search_sub.check()
                        # Output all new items
                        for search_item in new_items:
                            search_sub.send_item(search_item)
                    except Exception as e:
                        print("Failed to check {} subscription, \"{}\". Exception: {}".format(search_sub.type_name,
                                                                                              search_sub.get_name(),
                                                                                              e))
            # Save list
            sub_repo.save_json()


class SubscriptionList(Function):
    """
    List the currently active subscriptions.
    """
    list_words = ["list"]
    sub_words = ["sub", "subs", "subscription", "subscriptions"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "list subscription"
        # Names which can be used to address the function
        name_templates = {"{0} {1}", "{1} {0}", "{1} {2}", "{2} {1}",
                          "{1} {0} {2}", "{1} {2} {0}", "{2} {0} {1}", "{0} {2} {1}"}
        self.names = set([template.format(name, list_word, sub)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates
                          for list_word in self.list_words
                          for sub in self.sub_words])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Lists subscriptions for the current channel. Format: list subscription"

    def run(self, event):
        # Handy variables
        server = event.server
        hallo = server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(hallo)
        # Find list of feeds for current channel.
        with sub_repo.sub_lock:
            dest_searches = sub_repo.get_subs_by_destination(event.user
                                                             if event.channel is None
                                                             else event.channel)
        if len(dest_searches) == 0:
            return event.create_response("There are no subscriptions posting to this destination.")
        output_lines = ["Subscriptions posting to this channel:"]
        for search_item in dest_searches:
            new_line = "{} - {}".format(search_item.type_name, search_item.get_name())
            if search_item.last_update is not None:
                new_line += " ({})".format(search_item.last_update.strftime('%Y-%m-%d %H:%M:%S'))
            output_lines.append(new_line)
        return event.create_response("\n".join(output_lines))
