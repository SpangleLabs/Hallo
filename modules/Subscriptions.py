import json
from abc import ABCMeta
from threading import Lock

from Destination import Channel, User
from Function import Function


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
            if destination.server.name != sub.server_name:
                continue
            if isinstance(destination, Channel) and destination.address != sub.channel_address:
                continue
            if isinstance(destination, User) and destination.address != sub.user_address:
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
    def __init__(self):
        self.channel_address = None
        self.server_name = None
        self.user_address = None

    pass

    def matches_name(self, name_clean):
        pass


class SubscriptionFactory(object):

    @staticmethod
    def from_json(e621_sub_elem):
        return Subscription()  # TODO
        pass


class RssSub(Subscription):
    pass


class E621Sub(Subscription):
    pass


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


class SubscriptionAdd(Function):
    pass


class SubscriptionRemove(Function):
    pass


class SubscriptionCheck(Function):
    pass


class SubscriptionList(Function):
    pass
