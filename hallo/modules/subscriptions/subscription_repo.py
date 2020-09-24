import json
from threading import Lock
from typing import List, Type, TypeVar

from hallo.destination import Destination
import hallo.modules.subscriptions.subscription_common
import hallo.modules.subscriptions.subscriptions
import hallo.modules.subscriptions.subscription_factory
from hallo.inc.commons import inherits_from

T = TypeVar("T", bound=hallo.modules.subscriptions.subscription_common.SubscriptionCommon)


class SubscriptionRepo:
    """
    Holds the lists of subscriptions, for loading and unloading.
    """

    def __init__(self):
        self.sub_list: List[hallo.modules.subscriptions.subscriptions.Subscription] = []
        self.common_list: List[hallo.modules.subscriptions.subscription_common.SubscriptionCommon] = []
        self.sub_lock: Lock = Lock()

    def add_sub(self, new_sub: hallo.modules.subscriptions.subscriptions.Subscription) -> None:
        """
        Adds a new Subscription to the list.
        :param new_sub: New subscription to add
        """
        self.sub_list.append(new_sub)

    def remove_sub(self, remove_sub: hallo.modules.subscriptions.subscriptions.Subscription) -> None:
        """
        Removes a Subscription from the list.
        :param remove_sub: Existing subscription to remove
        """
        self.sub_list.remove(remove_sub)

    def get_subs_by_destination(
            self, destination: Destination
    ) -> List[hallo.modules.subscriptions.subscriptions.Subscription]:
        """
        Returns a list of subscriptions matching a specified destination.
        :param destination: Channel or User which E621Sub is posting to
        :return: list of Subscription objects matching destination
        """
        matching_subs = []
        for sub in self.sub_list:
            if sub.destination != destination:
                continue
            matching_subs.append(sub)
        return matching_subs

    def get_subs_by_name(
            self, name: str, destination: Destination
    ) -> List[hallo.modules.subscriptions.subscriptions.Subscription]:
        """
        Returns a list of subscriptions matching a specified name, be that a type and search, or just a type
        :param name: Search of the Subscription being searched for
        :param destination: Channel or User which Subscription is posting to
        :return: List of matching subscriptions
        """
        name_clean = name.lower().strip()
        matching_subs = []
        for sub in self.get_subs_by_destination(destination):
            if sub.matches_name(name_clean):
                matching_subs.append(sub)
        return matching_subs

    def get_common_config_by_type(self, common_type: Type[T]) -> T:
        """
        Returns the common configuration object for a given type.
        There should be only 1 common config object of each type.
        :param common_type: The class of the common config object being searched for
        :return: The object, or a new object if none was found.
        """
        if not inherits_from(common_type, "SubscriptionCommon"):
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "This common type, {}, is not a subclass of SubscriptionCommon".format(
                    common_type.__name__
                )
            )
        matching = [obj for obj in self.common_list if isinstance(obj, common_type)]
        if len(matching) == 0:
            new_common = common_type()
            self.common_list.append(new_common)
            return new_common
        if len(matching) == 1:
            return matching[0]
        raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
            "More than one subscription common config exists for the type: {}".format(
                common_type.__name__
            )
        )

    def save_json(self) -> None:
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
    def load_json(hallo_obj) -> 'SubscriptionRepo':
        """
        Constructs a new SubscriptionRepo from the JSON file
        :return: Newly constructed list of subscriptions
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
            new_common_obj = hallo.modules.subscriptions.subscription_factory.SubscriptionFactory.common_from_json(
                common_elem
            )
            new_sub_list.common_list.append(new_common_obj)
        # Loop subs in json file adding them to list
        for sub_elem in json_obj["subs"]:
            new_sub_obj = hallo.modules.subscriptions.subscription_factory.SubscriptionFactory.from_json(
                sub_elem, hallo_obj, new_sub_list
            )
            new_sub_list.add_sub(new_sub_obj)
        return new_sub_list
