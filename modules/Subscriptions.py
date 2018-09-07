import json
import urllib.parse
from abc import ABCMeta
from datetime import datetime
from threading import Lock

from Destination import Channel, User
from Events import EventMessageWithPhoto
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

    def save_json(self):
        """
        Saves the whole subscription list to a JSON file
        :return: None
        """
        json_obj = {}
        # Add subscriptions
        json_obj["subs"] = []
        for sub in self.sub_list:
            json_obj["subs"].append(sub.to_json())
        # Add common configuration
        json_obj["common"] = []
        # TODO
        # Write json to file
        with open("store/subscriptions.json", "w") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json():
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
            new_sub_obj = SubscriptionFactory.from_json(sub_elem)
            new_sub_list.add_sub(new_sub_obj)
        # TODO: add common data
        return new_sub_list


class Subscription(metaclass=ABCMeta):
    names = []
    """ :type : list[str]"""

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
        raise NotImplementedError()  # TODO

    def matches_name(self, name_clean):
        """
        :type name_clean: str
        :rtype: bool
        """
        raise NotImplementedError()  # TODO

    def check(self):
        """
        :rtype: list[object]
        """
        raise NotImplementedError()  # TODO

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
        raise NotImplementedError()  # TODO

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
            json_obj["channel_name"] = self.destination.name
        if isinstance(self.destination, User):
            json_obj["user_name"] = self.destination.name
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
        raise NotImplementedError()  # TODO


class RssSub(Subscription):
    pass


class E621Sub(Subscription):
    names = ["e621"]
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
        e6Sub = E621Sub(server, destination, search, update_frequency=search_delta)
        # Check if it's a valid search
        first_results = e6Sub.check()
        if len(first_results) == 0:
            raise SubscriptionException("This does not appear to be a valid search, or does not have results.")
        return e6Sub

    def matches_name(self, name_clean):
        raise NotImplementedError()  # TODO

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
        image_url = e621_result["file_url"]
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
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


class SubscriptionFactory(object):
    sub_classes = [E621Sub]

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


class SubscriptionAdd(Function):
    pass


class SubscriptionRemove(Function):
    pass


class SubscriptionCheck(Function):
    pass


class SubscriptionList(Function):
    pass
