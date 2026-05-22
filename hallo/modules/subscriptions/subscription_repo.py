import asyncio
import json
from typing import Type, TypeVar, TYPE_CHECKING

from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_common import SubscriptionCommon
from hallo.modules.subscriptions.subscription_exception import SubscriptionException
from hallo.modules.subscriptions.subscription_factory import SubscriptionFactory
from hallo.modules.subscriptions.source_e621_tagging import E621TaggingMenu
from hallo.modules.subscriptions.source_e621_backlog import E621BacklogTaggingMenu
from hallo.destination import Destination
from hallo.inc.commons import inherits_from, subscription_count, subscription_menu_count
from hallo.inc.menus import MenuCache, MenuFactory

if TYPE_CHECKING:
    from hallo.events import EventMenuCallback
    from hallo.hallo import Hallo


CommonType = TypeVar("CommonType", bound=SubscriptionCommon)


class SubscriptionRepo:
    """
    Holds the lists of subscriptions, for loading and unloading.
    """
    STORE_FILE = "store/subscriptions.json"
    MENU_STORE_FILE = "store/menus/subscriptions.json"

    def __init__(self, hallo_obj: 'Hallo') -> None:
        self.hallo: 'Hallo' = hallo_obj
        self.sub_list: list[Subscription] = []
        self.common_list: list[SubscriptionCommon] = []
        self.sub_lock: asyncio.Lock = asyncio.Lock()
        self.menu_cache: MenuCache | None = None
        for sub_class in SubscriptionFactory.sub_sources:
            subscription_count.labels(source_type=sub_class.__name__).set_function(
                lambda sc=sub_class: len([s for s in self.sub_list if s.source.__class__.__name__ == sc.__name__])
            )
        subscription_menu_count.set_function(lambda: self.menu_cache.count_menus() if self.menu_cache else 0)

    def add_sub(self, new_sub: Subscription) -> None:
        """
        Adds a new Subscription to the list.
        :param new_sub: New subscription to add
        """
        self.sub_list.append(new_sub)

    def remove_sub(self, remove_sub: Subscription) -> None:
        """
        Removes a Subscription from the list.
        :param remove_sub: Existing subscription to remove
        """
        self.sub_list.remove(remove_sub)

    def get_subs_by_destination(self, destination: Destination) -> list[Subscription]:
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

    def get_subs_by_name(self, name: str, destination: Destination) -> list[Subscription]:
        """
        Returns a list of subscriptions matching a specified name, be that a type and search, or just a type
        :param name: Search of the Subscription being searched for
        :param destination: Channel or User which Subscription is posting to
        :return: List of matching subscriptions
        """
        name_clean = name.lower().strip()
        matching_subs = []
        for sub in self.get_subs_by_destination(destination):
            if sub.source.matches_name(name_clean):
                matching_subs.append(sub)
        return matching_subs

    def get_common_config_by_type(self, common_type: Type[CommonType]) -> CommonType:
        """
        Returns the common configuration object for a given type.
        There should be only 1 common config object of each type.
        :param common_type: The class of the common config object being searched for
        :return: The object, or a new object if none was found.
        """
        if not inherits_from(common_type, "SubscriptionCommon"):
            raise SubscriptionException(
                f"This common type, {common_type.__name__}, is not a subclass of SubscriptionCommon"
            )
        matching = [obj for obj in self.common_list if isinstance(obj, common_type)]
        if len(matching) == 0:
            new_common = common_type(self.hallo)
            self.common_list.append(new_common)
            return new_common
        if len(matching) == 1:
            return matching[0]
        raise SubscriptionException(
            f"More than one subscription common config exists for the type: {common_type.__name__}"
        )

    async def handle_menu_callback(self, event: 'EventMenuCallback') -> None:
        menu = self.menu_cache.get_menu_by_callback_event(event)
        if menu:
            await menu.handle_callback(event)

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
        with open(self.STORE_FILE, "w") as f:
            json.dump(json_obj, f, indent=2)

    @classmethod
    async def load_json(cls, hallo_obj: 'Hallo') -> 'SubscriptionRepo':
        """
        Constructs a new SubscriptionRepo from the JSON file
        :return: Newly constructed list of subscriptions
        """
        # Create repo
        new_repo = cls(hallo_obj)
        # Try loading json file, otherwise return blank list
        try:
            with open(cls.STORE_FILE, "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            return new_repo
        # Loop common objects in json file adding them to list.
        # Common config must be loaded first, as subscriptions use it.
        for common_elem in json_obj["common"]:
            new_common_obj = SubscriptionFactory.common_from_json(common_elem, hallo_obj)
            new_repo.common_list.append(new_common_obj)
        # Loop subs in json file adding them to list
        for sub_elem in json_obj["subs"]:
            # TODO(async): Use asyncio.gather or something here
            new_sub_obj = await Subscription.from_json(sub_elem, hallo_obj, new_repo)
            new_repo.add_sub(new_sub_obj)
        return new_repo

    def load_menu_cache(self, hallo_obj: 'Hallo') -> None:
        menu_factory = MenuFactory([E621TaggingMenu, E621BacklogTaggingMenu], hallo_obj)
        self.menu_cache = MenuCache.load_from_json(self.MENU_STORE_FILE, menu_factory)
