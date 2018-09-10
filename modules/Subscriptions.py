import hashlib
import json
import re
import urllib.parse
from abc import ABCMeta
from datetime import datetime
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

    def add_common(self, new_common):
        """
        Adds a new common configuration to the list.
        :param new_common: New common configuration to add
        :type new_common: SubscriptionCommon
        """
        self.common_list.append(new_common)

    def remove_common(self, remove_common):
        """
        Removes a common configuration from the list.
        :param remove_common: Existing common config to remove
        :type remove_common: SubscriptionCommon
        """
        self.common_list.remove(remove_common)

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
            json_obj["common"].append(common.to_json())
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
        # Loop subs in json file adding them to list
        for sub_elem in json_obj["subs"]:
            new_sub_obj = SubscriptionFactory.from_json(sub_elem, hallo)
            new_sub_list.add_sub(new_sub_obj)
        # Loop common objects in json file adding them to list
        for common_elem in json_obj["common"]:
            new_common_obj = SubscriptionFactory.common_from_json(common_elem, hallo)
            new_sub_list.add_common(new_common_obj)
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

    @staticmethod
    def create_from_input(input_evt):
        """
        :type input_evt: EventMessage
        :rtype: Subscription
        """
        raise NotImplementedError()

    def matches_name(self, name_clean):
        """
        :type name_clean: str
        :rtype: bool
        """
        raise NotImplementedError()

    def get_name(self):
        """
        :rtype: str
        """
        raise NotImplementedError()

    def check(self):
        """
        :rtype: list[object]
        """
        raise NotImplementedError()

    def send_item(self, item):
        """
        :type item: object
        :rtype: None
        """
        output_evt = self.format_item(item)
        self.server.send(output_evt)

    def format_item(self, item):
        """
        :type item: object
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
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        """
        :type json_obj: dict
        :type hallo: Hallo.Hallo
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
        :type last_item_hash | None
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.url = url
        """ :type : str"""
        if title is None:
            rss_data = Commons.load_url_string(self.url)
            rss_elem = ElementTree.fromstring(rss_data)
            channel_elem = rss_elem.find("channel")
            # Update title
            title_elem = channel_elem.find("title")
            title = title_elem.text
        self.title = title
        """ :type : str"""
        self.last_item_hash = last_item_hash
        """ :type : str | None"""

    @staticmethod
    def create_from_input(input_evt):
        server = input_evt.server
        destination = input_evt.channel if input_evt.channel is not None else input_evt.user
        # Get user specified stuff
        feed_url = input_evt.command_args.split()[0]
        feed_period = "PT3600S"
        if len(input_evt.command_args.split()) > 1:
            feed_period = input_evt.command_args.split()[1]
        try:
            feed_delta = Commons.load_time_delta(feed_period)
        except ISO8601ParseError:
            feed_delta = Commons.load_time_delta("PT300S")
        try:
            rss_sub = RssSub(server, destination, feed_url, update_frequency=feed_delta)
            rss_sub.check()
        except Exception as e:
            raise SubscriptionException("Failed to create RSS subscription", e)
        return rss_sub

    def matches_name(self, name_clean):
        return name_clean in [self.title, self.url, self.get_name()]

    def get_name(self):
        return "{} ({})".format(self.title, self.url)

    def check(self):
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
    def from_json(json_obj, hallo):
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
        # Type specific loading
        # Load last items
        url = json_obj["url"]
        title = json_obj["title"]
        last_hash = json_obj["last_item"]
        return RssSub(server, destination, url, last_check, update_frequency, title, last_hash)


class E621Sub(Subscription):
    names = ["e621", "e621 search", "search e621"]
    """ :type : list[str]"""
    type_name = "e621"
    """ :type : str"""

    def __init__(self, server, destination, search, last_check=None, update_frequency=None, latest_ids=None):
        """
        :type server: Server.Server
        :type destination: Destination.Destination
        :type search: str
        :type last_check: datetime
        :type update_frequency: timedelta
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.search = search
        """ :type : str"""
        if latest_ids is None:
            latest_ids = []
        self.latest_ids = latest_ids
        """ :type : list[int]"""

    @staticmethod
    def create_from_input(input_evt):
        """
        :type input_evt: Events.EventMessage
        :rtype: E621Sub
        """
        server = input_evt.server
        destination = input_evt.channel if input_evt.channel is not None else input_evt.user
        # See if last argument is check period.
        try:
            try_period = input_evt.command_args.split()[-1]
            search_delta = Commons.load_time_delta(try_period)
            search = input_evt.command_args[:-len(try_period)].strip()
        except ISO8601ParseError:
            search = input_evt.command_args.strip()
            search_delta = Commons.load_time_delta("PT300S")
        # Create e6 subscription object
        e6_sub = E621Sub(server, destination, search, update_frequency=search_delta)
        # Check if it's a valid search
        first_results = e6_sub.check()
        if len(first_results) == 0:
            raise SubscriptionException("This does not appear to be a valid search, or does not have results.")
        return e6_sub

    def matches_name(self, name_clean):
        return name_clean == self.search

    def get_name(self):
        return "search for \"{}\"".format(self.search)

    def check(self):
        search = "{} order:-id".format(self.search)  # Sort by id
        if len(self.latest_ids) > 0:
            oldest_id = min(self.latest_ids)
            search += " id:>{}".format(oldest_id)  # Don't list anything older than the oldest of the last 10
        url = "http://e621.net/post/index.json?tags={}&limit=50".format(urllib.parse.quote(search))
        results = Commons.load_url_json(url)
        return_list = []
        new_last_ten = set(self.latest_ids)
        for result in results:
            result_id = result["id"]
            # Create new list of latest ten results
            new_last_ten.add(result_id)
            # If post hasn't been seen in the latest ten, add it to returned list.
            if result_id not in self.latest_ids:
                return_list.append(result)
        self.latest_ids = sorted(list(new_last_ten))[::-1][:10]
        # Update check time
        self.last_check = datetime.now()
        return return_list

    def format_item(self, e621_result):
        link = "http://e621.net/post/show/{}".format(e621_result['id'])
        # Create rating string
        rating = "(Unknown)"
        rating_dict = {"e": "(Explicit)", "q": "(Questionable)", "s": "(Safe)"}
        if e621_result["rating"] in rating_dict:
            rating = rating_dict[e621_result["rating"]]
        # Construct output
        output = "Update on \"{}\" e621 search. {} {}".format(self.search, link, rating)
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        if e621_result["file_ext"] in ["swf", "webm"]:
            return EventMessage(self.server, channel, user, output, inbound=False)
        image_url = e621_result["file_url"]
        output_evt = EventMessageWithPhoto(self.server, channel, user, output, image_url, inbound=False)
        return output_evt

    def to_json(self):
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["search"] = self.search
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
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
        # Type specific loading
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        search = json_obj["search"]
        return E621Sub(server, destination, search, last_check, update_frequency, latest_ids)


class GoogleDocsSub(Subscription):
    pass


class TwitterSub(Subscription):
    pass


class FASearchSub(Subscription):
    pass


class FAFavSub(Subscription):
    pass


class FANotesSub(Subscription):
    pass


class FASubmissionsSub(Subscription):
    pass


class FAWatchSub(Subscription):
    pass


class FACommentsSub(Subscription):
    pass


class FAFavsSub(Subscription):
    pass


class YoutubeSub(Subscription):
    pass


class ImgurSub(Subscription):
    pass


class SubscriptionCommon:
    type_name = ""
    """ :type : str"""

    def to_json(self):
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj, hallo):
        raise NotImplementedError()


class FAKeysCommon(SubscriptionCommon):
    type_name = "FA_keys"
    """ :type : str"""

    def __init__(self):
        self.list_keys = []
        """ :type : list[FAKey]"""

    def add_key(self, key):
        self.list_keys.append(key)

    def to_json(self):
        json_obj = {"common_type": self.type_name,
                    "key_list": []}
        for key in self.list_keys:
            json_obj["key_list"].append(key.to_json())
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        keys_common = FAKeysCommon()
        for key_dict in json_obj["key_list"]:
            keys_common.add_key(FAKey.from_json(key_dict, hallo))
        return keys_common


class FAKey:

    def __init__(self, user, cookie_a, cookie_b):
        self.user = user
        """ :type : Destination.Destination"""
        self.cookie_a = cookie_a
        """ :type : str"""
        self.cookie_b = cookie_b
        """ :type : str"""
        self.fa_reader = None
        """ :type : FAReader | None"""

    def get_fa_reader(self):
        """
        :rtype: FAKey.FAReader
        """
        if self.fa_reader is None:
            self.fa_reader = FAKey.FAReader(self.cookie_a, self.cookie_b)
        return self.fa_reader

    def to_json(self):
        json_obj = {"server_name": self.user.server.name,
                    "user_address": self.user.address,
                    "cookie_a": self.cookie_a,
                    "cookie_b": self.cookie_b}
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        server = hallo.get_server_by_name(json_obj["server_name"])
        user = server.get_user_by_address(json_obj["user_address"])
        cookie_a = json_obj["cookie_a"]
        cookie_b = json_obj["cookie_b"]
        return FAKey(user, cookie_a, cookie_b)

    class FAReader:
        NOTES_INBOX = "inbox"
        NOTES_OUTBOX = "outbox"

        class FALoginFailedError(Exception):
            pass

        def __init__(self, cookie_a, cookie_b):
            self.a = cookie_a
            self.b = cookie_b

        def check_login(self):
            """
            :rtype: bool
            :raises: FAReader.FALoginFailedError
            """
            raise NotImplementedError()

        def get_notification_page(self):
            """
            :rtype: FAReader.FANotificationsPage
            """
            raise NotImplementedError()

        def get_submissions_page(self):
            """
            :rtype: FAReader.FASubmissionsPage
            """
            raise NotImplementedError()

        def get_notes_page(self, folder):
            """
            :type folder: str
            :return: FAReader.FANotesPage
            """
            if folder not in [self.NOTES_INBOX, self.NOTES_OUTBOX]:
                raise ValueError("Invalid FA note folder.")
            raise NotImplementedError()

        def get_user_page(self, username):
            # Needs shout list, for checking own shouts
            raise NotImplementedError()

        def get_user_fav_page(self, username):
            """
            :type username: str
            :rtype: FAReader.FAUserFavPage
            """
            raise NotImplementedError()

        def get_submission_page(self, submission_id):
            raise NotImplementedError()

        def get_journal_page(self, journal_id):
            raise NotImplementedError()

        class FAPage:
            def __init__(self, url):
                self.url = url
                """ :type : str"""

        class FANotificationsPage(FAPage):
            pass

        class FASubmissionsPage(FAPage):
            pass

        class FANotesPage(FAPage):
            pass

        class FAUserPage(FAPage):
            pass

        class FAUserFavPage(FAPage):
            pass

        class FASubmissionPage(FAPage):
            pass

        class FAJournalPage(FAPage):
            pass


class SubscriptionFactory(object):
    sub_classes = [E621Sub, RssSub]
    common_classes = [FAKeysCommon]

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
    def from_json(sub_json, hallo):
        """
        :type sub_json: dict
        :type hallo: Hallo.Hallo
        :rtype: Subscription
        """
        sub_type_name = sub_json["sub_type"]
        for sub_class in SubscriptionFactory.sub_classes:
            if sub_class.type_name == sub_type_name:
                return sub_class.from_json(sub_json, hallo)
        raise SubscriptionException("Could not load subscription of type {}".format(sub_type_name))

    @staticmethod
    def common_from_json(common_json, hallo):
        """
        :type common_json: dict
        :type hallo: Hallo.Hallo
        :rtype: SubscriptionCommon
        """
        common_type_name = common_json["common_type"]
        for common_class in SubscriptionFactory.common_classes:
            if common_class.type_name == common_type_name:
                return common_class.from_json(common_json, hallo)
        raise SubscriptionException("Could not load common configuration of type {}".format(common_type_name))


class SubscriptionAdd(Function):
    """
    Adds a new subscription, allowing specification of server and channel.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "add subscription"
        # Names which can be used to address the function
        name_templates = {"{} add", "add {}",
                          "add {} sub", "add sub {}", "sub {} add", "{} sub add",
                          "add {} subscription", "add subscription {}", "subscription {} add", "{} subscription add"}
        self.names = set([template.format(name)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Adds a new subscription to be checked for updates which will be posted to the current " \
                         "location." \
                         " Format: add subscription <sub type> <sub details> <update period?>"

    def run(self, event):
        command_name = event.command_name
        sub_type_name = re.sub(r"\b(add|sub|subscription)\b", "", command_name).strip()
        sub_class = SubscriptionFactory.get_class_by_name(sub_type_name)
        # Get current RSS feed list
        function_dispatcher = event.server.hallo.function_dispatcher
        sub_check_class = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_class)  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(event.server.hallo)
        # Create new subscription
        sub_obj = sub_class.create_from_input(event)
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

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "remove subscription"
        # Names which can be used to address the function
        name_templates = {"{} remove", "remove {}",
                          "remove {} sub", "remove sub {}", "sub {} remove", "{} sub remove",
                          "remove sub", "remove sub", "sub remove", "sub remove",
                          "remove {} subscription", "remove subscription {}",
                          "remove subscription", "remove subscription",
                          "subscription {} remove", "{} subscription remove",
                          "subscription remove", "subscription remove"}
        self.names = set([template.format(name)
                         for name in SubscriptionFactory.get_names()
                         for template in name_templates])
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

    NAMES_ALL = ["*", "all"]

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "check subscription"
        # Names which can be used to address the function
        name_templates = {"{} check", "check {}",
                          "check {} sub", "check sub {}", "sub {} check", "{} sub check",
                          "check {} subs", "check subs {}", "subs {} check", "{} subs check",
                          "check subs", "check subs", "subs check", "subs check",
                          "check {} subscription", "check subscription {}",
                          "check {} subscriptions", "check subscriptions {}",
                          "check subscriptions", "check subscriptions",
                          "subscription {} check", "{} subscription check",
                          "subscriptions {} check", "{} subscriptions check",
                          "subscriptions check", "subscriptions check"}
        self.names = set([template.format(name)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates])
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
                new_items = search_sub.check()
                found_items += len(new_items)
                for search_item in new_items:
                    search_sub.send_item(search_item)
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
                    new_items = search_sub.check()
                    # Output all new items
                    for search_item in new_items:
                        search_sub.send_item(search_item)
            # Save list
            sub_repo.save_json()


class SubscriptionList(Function):
    """
    List the currently active subscriptions.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "list subscription"
        # Names which can be used to address the function
        name_templates = {"{} list", "list {}",
                          "list {} sub", "list sub {}", "sub {} list", "{} sub list",
                          "list {} subs", "list subs {}", "subs {} list", "{} subs list",
                          "list subs", "list subs", "subs list", "subs list",
                          "list {} subscription", "list subscription {}",
                          "list {} subscriptions", "list subscriptions {}",
                          "list subscriptions", "list subscriptions",
                          "subscription {} list", "{} subscription list",
                          "subscriptions {} list", "{} subscriptions list",
                          "subscriptions list", "subscriptions list"}
        self.names = set([template.format(name)
                          for name in SubscriptionFactory.get_names()
                          for template in name_templates])
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
            output_lines.append("{} - {}".format(search_item.type_name, search_item.get_name()))
        return event.create_response("\n".join(output_lines))
