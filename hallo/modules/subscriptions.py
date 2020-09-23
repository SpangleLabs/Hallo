import hashlib
import json
import logging
import os
import re
import urllib.parse
from abc import ABC
from datetime import datetime, timedelta
from threading import Lock
from typing import List, Type, Generic, TypeVar, Dict, Optional, Union, Callable, Set
from urllib.error import HTTPError
from xml.etree import ElementTree

import dateutil.parser
import isodate
from bs4 import BeautifulSoup

from hallo.destination import Channel, User, Destination
from hallo.errors import SubscriptionCheckError
from hallo.events import EventMessageWithPhoto, EventMessage, EventMinute, Event, ServerEvent
from hallo.function import Function
from hallo.hallo import Hallo
from hallo.inc.commons import Commons, CachedObject
from hallo.inc.input_parser import InputParser
import hallo.modules.user_data
from hallo.server import Server

logger = logging.getLogger(__name__)
T = TypeVar("T")
# TODO: Subscriptions inheriting from Subscription[Dict] could do with actual classes or types


def is_valid_iso8601_period(try_period: str) -> bool:
    try:
        isodate.parse_duration(try_period)
        return True
    except isodate.isoerror.ISO8601Error:
        return False


class SubscriptionException(Exception):
    pass


class SubscriptionRepo:
    """
    Holds the lists of subscriptions, for loading and unloading.
    """

    def __init__(self):
        self.sub_list: List[Subscription] = []
        self.common_list: List[SubscriptionCommon] = []
        self.sub_lock: Lock = Lock()

    def add_sub(self, new_sub: 'Subscription') -> None:
        """
        Adds a new Subscription to the list.
        :param new_sub: New subscription to add
        """
        self.sub_list.append(new_sub)

    def remove_sub(self, remove_sub: 'Subscription') -> None:
        """
        Removes a Subscription from the list.
        :param remove_sub: Existing subscription to remove
        """
        self.sub_list.remove(remove_sub)

    def get_subs_by_destination(self, destination: Destination) -> List['Subscription']:
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

    def get_subs_by_name(self, name: str, destination: Destination) -> List['Subscription']:
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

    def get_common_config_by_type(self, common_type: Type) -> 'SubscriptionCommon':
        """
        Returns the common configuration object for a given type.
        There should be only 1 common config object of each type.
        :param common_type: The class of the common config object being searched for
        :return: The object, or a new object if none was found.
        """
        if not issubclass(common_type, SubscriptionCommon):
            raise SubscriptionException(
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
        raise SubscriptionException(
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
            new_common_obj = SubscriptionFactory.common_from_json(common_elem)
            new_sub_list.common_list.append(new_common_obj)
        # Loop subs in json file adding them to list
        for sub_elem in json_obj["subs"]:
            new_sub_obj = SubscriptionFactory.from_json(sub_elem, hallo_obj, new_sub_list)
            new_sub_list.add_sub(new_sub_obj)
        return new_sub_list


class Subscription(Generic[T], ABC):
    names: List[str] = []
    type_name: str = ""

    def __init__(
            self,
            server: Server,
            destination: Destination,
            last_check: datetime = None,
            update_frequency: timedelta = None
    ) -> None:
        if update_frequency is None:
            update_frequency = isodate.parse_duration("PT5M")
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
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'Subscription':
        """
        Creates a new subscription object from a user's input line
        """
        raise NotImplementedError()

    def matches_name(self, name_clean: str) -> bool:
        """
        Returns whether a user input string matches this subscription object
        """
        raise NotImplementedError()

    def get_name(self) -> None:
        """
        Returns a printable name for the subscription
        :rtype: str
        """
        raise NotImplementedError()

    def check(self, *, ignore_result: bool = False) -> List[T]:
        """
        Checks the subscription, and returns a list of update objects, in whatever format that
        format_item() would like to receive them.
        The list should be ordered from oldest to newest.
        :param ignore_result: Whether the items returned will be formatted an used.
        """
        raise NotImplementedError()

    def send_item(self, item: T) -> None:
        self.last_update = datetime.now()
        output_evt = self.format_item(item)
        self.server.send(output_evt)

    def format_item(self, item: T) -> EventMessage:
        """
        Formats an item, as returned from check(), into an event that can be sent out
        """
        raise NotImplementedError()

    def needs_check(self) -> bool:
        """
        Returns whether a subscription check is overdue.
        """
        if self.last_check is None:
            return True
        if datetime.now() > self.last_check + self.update_frequency:
            return True
        return False

    def to_json(self) -> Dict:
        json_obj = dict()
        json_obj["server_name"] = self.server.name
        if isinstance(self.destination, Channel):
            json_obj["channel_address"] = self.destination.address
        if isinstance(self.destination, User):
            json_obj["user_address"] = self.destination.address
        if self.last_check is not None:
            json_obj["last_check"] = self.last_check.isoformat()
        json_obj["update_frequency"] = isodate.duration_isoformat(self.update_frequency)
        if self.last_update is not None:
            json_obj["last_update"] = self.last_update.isoformat()
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'Subscription':
        raise NotImplementedError()


class RssSub(Subscription[ElementTree.Element]):
    names: List[str] = ["rss", "rss feed"]
    type_name: str = "rss"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        url: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        title: Optional[str] = None,
        last_item_hash: Optional[str] = None,
    ):
        """
        :param last_item_hash: GUID or md5 of latest item in rss feed
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.url: str = url
        if title is None:
            title = self._get_feed_title()
        self.title: str = title
        self.last_item_hash: Optional[str] = last_item_hash

    def _get_feed_title(self) -> str:
        rss_data = self.get_rss_data()
        rss_elem = ElementTree.fromstring(rss_data)
        channel_elem = rss_elem.find("channel")
        title = None
        if channel_elem is not None:
            # Update title
            title_elem = channel_elem.find("title")
        else:
            title_elem = rss_elem.find("{http://www.w3.org/2005/Atom}title")
        if title_elem is not None:
            title = title_elem.text
        return title if title is not None else "No title"

    def get_rss_data(self) -> str:
        headers = None
        # Tumblr feeds need "GoogleBot" in the URL, or they'll give a GDPR notice
        if "tumblr.com" in self.url:
            headers = [
                ["User-Agent", "Hallo IRCBot hallo@dr-spangle.com (GoogleBot/4.5.1)"]
            ]
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
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'RssSub':
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # Get user specified stuff
        feed_url = input_evt.command_args.split()[0]
        feed_period = "PT600S"
        if len(input_evt.command_args.split()) > 1:
            feed_period = input_evt.command_args.split()[1]
        try:
            feed_delta = isodate.parse_duration(feed_period)
        except isodate.isoerror.ISO8601Error:
            feed_delta = isodate.parse_duration("PT10M")
        try:
            rss_sub = RssSub(server, destination, feed_url, update_frequency=feed_delta)
            rss_sub.check()
        except Exception as e:
            raise SubscriptionException("Failed to create RSS subscription", e)
        return rss_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [
            self.title.lower().strip(),
            self.url.lower().strip(),
            self.get_name().lower().strip(),
        ]

    def get_name(self) -> str:
        return "{} ({})".format(self.title, self.url)

    def _get_item_hash(self, feed_item) -> str:
        item_guid_elem = feed_item.find("guid")
        if item_guid_elem is not None:
            item_hash = item_guid_elem.text
        else:
            item_link_elem = feed_item.find("link")
            if item_link_elem is not None:
                item_hash = item_link_elem.text
            else:
                item_xml = ElementTree.tostring(feed_item)
                item_hash = hashlib.md5(item_xml).hexdigest()
        return item_hash

    def _get_feed_items(self, rss_elem: ElementTree.Element) -> List[ElementTree.Element]:
        channel_elem = rss_elem.find("channel")
        if channel_elem is not None:
            return channel_elem.findall("item")
        else:
            return rss_elem.findall("{http://www.w3.org/2005/Atom}entry")

    def check(self, *, ignore_result: bool = False) -> List[ElementTree.Element]:
        rss_data = self.get_rss_data()
        rss_elem = ElementTree.fromstring(rss_data)
        new_items = []
        # Update title
        self.title = self._get_feed_title()
        # Loop elements, seeing when any match the last item's hash
        latest_hash = None
        for item_elem in self._get_feed_items(rss_elem):
            item_hash = self._get_item_hash(item_elem)
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

    def _get_item_title(self, feed_item: ElementTree.Element) -> str:
        title_elem = feed_item.find("title")
        if title_elem is not None:
            return title_elem.text
        return feed_item.find("{http://www.w3.org/2005/Atom}title").text

    def _get_item_link(self, feed_item: ElementTree.Element) -> str:
        link_elem = feed_item.find("link")
        if link_elem is not None:
            return link_elem.text
        return feed_item.find("{http://www.w3.org/2005/Atom}link").get("href")

    def format_item(self, rss_item: ElementTree.Element) -> EventMessage:
        # Check custom formatting
        custom_evt = self._format_custom_sites(rss_item)
        if custom_evt is not None:
            return custom_evt
        # Load item xml
        item_title = self._get_item_title(rss_item)
        item_link = self._get_item_link(rss_item)
        # Construct output
        output = 'Update on "{}" RSS feed. "{}" {}'.format(
            self.title, item_title, item_link
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def _format_custom_sites(self, rss_item: ElementTree.Element) -> Optional[EventMessage]:
        if "xkcd.com" in self.url:
            item_title = rss_item.find("title").text
            item_link = rss_item.find("link").text
            comic_number = item_link.strip("/").split("/")[-1]
            json_link = "https://xkcd.com/{}/info.0.json".format(comic_number)
            comic_json = Commons.load_url_json(json_link)
            alt_text = comic_json["alt"]
            output = 'Update on "{}" RSS feed. "{}" {}\nAlt text: {}'.format(
                self.title, item_title, item_link, alt_text
            )
            channel = (
                self.destination if isinstance(self.destination, Channel) else None
            )
            user = self.destination if isinstance(self.destination, User) else None
            return EventMessage(self.server, channel, user, output, inbound=False)
        if "awoocomic" in self.title:
            item_title = rss_item.find("title").text
            if " - " in item_title:
                item_title = item_title.split(" - ")[0]
            item_link = rss_item.find("link").text
            output = 'Update on "{}" RSS feed. "{}" {}'.format(
                self.title, item_title, item_link
            )
            channel = (
                self.destination if isinstance(self.destination, Channel) else None
            )
            user = self.destination if isinstance(self.destination, User) else None
            return EventMessage(self.server, channel, user, output, inbound=False)
        if "smbc-comics.com" in self.url:
            item_title = rss_item.find("title").text
            item_link = rss_item.find("link").text
            page_code = Commons.load_url_string(item_link)
            soup = BeautifulSoup(page_code, "html.parser")
            comic_img = soup.select_one("img#cc-comic")
            alt_text = comic_img["title"]
            after_comic_img = soup.select_one("#aftercomic img")
            channel = (
                self.destination if isinstance(self.destination, Channel) else None
            )
            user = self.destination if isinstance(self.destination, User) else None
            return EventMessageWithPhoto(
                self.server,
                channel,
                user,
                'Update on "{}" RSS feed. "{}" {}\nAlt text: {}'.format(
                    self.title, item_title, item_link, alt_text
                ),
                [comic_img["src"], after_comic_img["src"]],
            )
        if "rss.app" in self.url:
            item_title = self._get_item_title(rss_item)
            item_link = self._get_item_link(rss_item)
            page_code = Commons.load_url_string(item_link)
            soup = BeautifulSoup(page_code, "html.parser")
            head_script = soup.select_one("head script")
            if head_script is None:
                return None
            url_regex = re.compile(r"var url = \"([^\"]+)\";", re.IGNORECASE)
            url_result = url_regex.search(head_script.text)
            if url_result is None:
                return None
            output = 'Update on "{}" RSS feed. "{}" {}'.format(
                self.title, item_title, url_result.group(1)
            )
            channel = self.destination if isinstance(self.destination, Channel) else None
            user = self.destination if isinstance(self.destination, User) else None
            return EventMessage(self.server, channel, user, output, inbound=False)
        return None

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["title"] = self.title
        json_obj["url"] = self.url
        json_obj["last_item"] = self.last_item_hash
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'RssSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load last items
        url = json_obj["url"]
        title = json_obj["title"]
        last_hash = json_obj["last_item"]
        new_sub = RssSub(
            server, destination, url, last_check, update_frequency, title, last_hash
        )
        new_sub.last_update = last_update
        return new_sub


class E621Sub(Subscription[Dict]):
    names: List[str] = ["e621", "e621 search", "search e621"]
    type_name: str = "e621"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        search: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_ids: Optional[List[int]] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.search: str = search
        if latest_ids is None:
            latest_ids = []
        self.latest_ids: List[int] = latest_ids

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'E621Sub':
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if last argument is check period.
        try:
            try_period = input_evt.command_args.split()[-1]
            search_delta = isodate.parse_duration(try_period)
            search = input_evt.command_args[: -len(try_period)].strip()
        except isodate.isoerror.ISO8601Error:
            search = input_evt.command_args.strip()
            search_delta = isodate.parse_duration("PT300S")
        # Create e6 subscription object
        e6_sub = E621Sub(server, destination, search, update_frequency=search_delta)
        # Check if it's a valid search
        first_results = e6_sub.check()
        if len(first_results) == 0:
            raise SubscriptionException(
                "This does not appear to be a valid search, or does not have results."
            )
        return e6_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.search.lower().strip()

    def get_name(self) -> str:
        return 'search for "{}"'.format(self.search)

    def check(self, *, ignore_result: bool = False) -> List[Dict]:
        search = "{} order:-id".format(self.search)  # Sort by id
        if len(self.latest_ids) > 0:
            oldest_id = min(self.latest_ids)
            search += " id:>{}".format(
                oldest_id
            )  # Don't list anything older than the oldest of the last 10
        url = "https://e621.net/posts.json?tags={}&limit=50".format(
            urllib.parse.quote(search)
        )
        results = Commons.load_url_json(url)
        return_list = []
        new_last_ten = set(self.latest_ids)
        for result in results["posts"]:
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

    def format_item(self, e621_result: Dict) -> EventMessage:
        link = "https://e621.net/posts/{}".format(e621_result["id"])
        # Create rating string
        rating_dict = {"e": "(Explicit)", "q": "(Questionable)", "s": "(Safe)"}
        rating = rating_dict.get(e621_result["rating"], "(Unknown)")
        # Construct output
        output = 'Update on "{}" e621 search. {} {}'.format(self.search, link, rating)
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        if e621_result["file"]["ext"] in ["swf", "webm"]:
            return EventMessage(self.server, channel, user, output, inbound=False)
        image_url = e621_result["file"]["url"]
        if image_url is None:
            return EventMessage(
                self.server, channel, user, output, inbound=False
            )
        return EventMessageWithPhoto(
            self.server, channel, user, output, image_url, inbound=False
        )

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["search"] = self.search
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'E621Sub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        search = json_obj["search"]
        new_sub = E621Sub(
            server, destination, search, last_check, update_frequency, latest_ids
        )
        new_sub.last_update = last_update
        return new_sub


class E621TaggingSub(E621Sub):
    names: List[str] = ["e621 tagging", "e621 tagging search", "tagging e621"]
    type_name: str = "e621-tagging"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        search: str,
        tags: List[str],
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_ids: Optional[List[int]] = None,
    ):
        super().__init__(
            server,
            destination,
            search,
            last_check=last_check,
            update_frequency=update_frequency,
            latest_ids=latest_ids,
        )
        self.tags: List[str] = tags

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'E621TaggingSub':
        """
        :type input_evt: Events.EventMessage
        :type sub_repo: SubscriptionRepo
        :rtype: E621Sub
        """
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # Parsed
        parsed = InputParser(input_evt.command_args)
        # See if check period is specified
        period_arg = parsed.get_arg_by_names(
            ["period", "update_period", "update period"]
        )
        if period_arg is not None:
            search_delta = isodate.parse_duration(period_arg)
        else:
            try_period = parsed.split_remaining_into_two(
                lambda x, y: is_valid_iso8601_period(x)
            )
            if len(try_period) == 1:
                search_delta = try_period[0][0]
                parsed = InputParser(try_period[0][1])
            else:
                search_delta = isodate.parse_duration("PT300S")
        # See if tags are specified
        tags_arg = parsed.get_arg_by_names(
            ["tags", "watched_tags", "to_tag", "watched tags", "to tag", "watch"]
        )
        search_arg = parsed.get_arg_by_names(
            [
                "search",
                "query",
                "search_query",
                "search query",
                "subscription",
                "sub",
                "search_term",
                "search term",
            ]
        )
        if tags_arg is not None:
            tags = tags_arg.split()
            if search_arg is not None:
                search = search_arg
            else:
                search = parsed.remaining_text
        else:
            if search_arg is not None:
                search = search_arg
                tags = parsed.remaining_text.split()
            else:
                raise SubscriptionException(
                    'You need to specify a search term with search="search term" and '
                    'tags to watch with tags="tags to watch"'
                )
        # Create e6 subscription object
        e6_sub = E621TaggingSub(
            server, destination, search, tags, update_frequency=search_delta
        )
        # Check if it's a valid search
        first_results = e6_sub.check()
        if len(first_results) == 0:
            raise SubscriptionException(
                "This does not appear to be a valid search, or does not have results."
            )
        return e6_sub

    def get_name(self) -> str:
        return 'search for "{}" to apply tags {}'.format(self.search, self.tags)

    def format_item(self, e621_result: Dict) -> EventMessage:
        link = "https://e621.net/posts/{}".format(e621_result["id"])
        # Create rating string
        rating_dict = {"e": "(Explicit)", "q": "(Questionable)", "s": "(Safe)"}
        rating = rating_dict.get(e621_result["rating"], "(Unknown)")
        # Check tags
        post_tags = [tag for tag_list in e621_result["tags"].values() for tag in tag_list]
        tag_results = {tag: tag in post_tags for tag in self.tags}
        tag_output = ["{}: {}".format(tag, val) for tag, val in tag_results.items()]
        # Construct output
        output = 'Update on "{}" tagging e621 search. {} {}.\nWatched tags: {}'.format(
            self.search, link, rating, tag_output
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        if e621_result["file"]["ext"] in ["swf", "webm"]:
            return EventMessage(self.server, channel, user, output, inbound=False)
        image_url = e621_result["file"]["url"]
        if image_url is None:
            return EventMessage(self.server, channel, user, output, inbound=False)
        return EventMessageWithPhoto(
            self.server, channel, user, output, image_url, inbound=False
        )

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["search"] = self.search
        json_obj["tags"] = self.tags
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'E621TaggingSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        search = json_obj["search"]
        tags = json_obj["tags"]
        new_sub = E621TaggingSub(
            server, destination, search, tags, last_check, update_frequency, latest_ids
        )
        new_sub.last_update = last_update
        return new_sub


class FANotificationNotesSub(Subscription[Dict]):
    names: List[str] = ["fa notes notifications", "fa notes", "furaffinity notes"]
    type_name: str = "fa_notif_notes"

    NEW_INBOX_NOTE = "new_note"
    READ_OUTBOX_NOTE = "note_read"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        inbox_note_ids: Optional[List[str]] = None,
        outbox_note_ids: Optional[List[str]] = None,
    ):
        """
        :param inbox_note_ids: List of id strings of notes in the inbox
        :param outbox_note_ids: List of id strings of unread notes in the outbox
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: FAKey = fa_key
        self.inbox_note_ids: List[str] = [] if inbox_note_ids is None else inbox_note_ids
        self.outbox_note_ids: List[str] = [] if outbox_note_ids is None else outbox_note_ids

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'FANotificationNotesSub':
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Cannot create FA note notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` "
                "and your cookie values."
            )
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        notes_sub = FANotificationNotesSub(
            server, destination, fa_key, update_frequency=search_delta
        )
        notes_sub.check()
        return notes_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["notes"]]

    def get_name(self) -> str:
        return "FA notes for {}".format(self.fa_key.user.name)

    def check(self, *, ignore_result: bool = False) -> List[Dict]:
        fa_reader = self.fa_key.get_fa_reader()
        results = []
        # Check inbox and outbox
        inbox_notes_page = fa_reader.get_notes_page(FAKey.FAReader.NOTES_INBOX)
        outbox_notes_page = fa_reader.get_notes_page(FAKey.FAReader.NOTES_OUTBOX)
        # Check for newly received notes in inbox
        for inbox_note in inbox_notes_page.notes:
            note_id = inbox_note.note_id
            if note_id not in self.inbox_note_ids and (
                len(self.inbox_note_ids) == 0
                or int(note_id) > int(self.inbox_note_ids[-1])
            ):
                # New note
                results.append({"type": self.NEW_INBOX_NOTE, "note": inbox_note})
        # Check for newly read notes in outbox
        for outbox_note in outbox_notes_page.notes:
            if outbox_note.note_id in self.outbox_note_ids and outbox_note.is_read:
                # Newly read note
                results.append({"type": self.READ_OUTBOX_NOTE, "note": outbox_note})
        # Reset inbox note ids and outbox note ids
        self.inbox_note_ids = [note.note_id for note in inbox_notes_page.notes]
        self.outbox_note_ids = [
            note.note_id for note in outbox_notes_page.notes if not note.is_read
        ]
        # Update last check time
        self.last_check = datetime.now()
        # Return results
        return results[::-1]

    def format_item(self, item: Dict) -> EventMessage:
        # Construct output
        output = "Err, notes did something?"
        note = item["note"]  # type: FAKey.FAReader.FANote
        if item["type"] == self.NEW_INBOX_NOTE:
            output = \
                f"You have a new note. Subject: {note.subject}, From: {note.name}, " \
                f"Link: https://www.furaffinity.net/viewmessage/{note.note_id}/"
        if item["type"] == self.READ_OUTBOX_NOTE:
            output = "An outbox note has been read. Subject: {}, To: {}".format(
                note.subject, note.name
            )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["inbox_note_ids"] = []
        for note_id in self.inbox_note_ids:
            json_obj["inbox_note_ids"].append(note_id)
        json_obj["outbox_note_ids"] = []
        for note_id in self.outbox_note_ids:
            json_obj["outbox_note_ids"].append(note_id)
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'FANotificationNotesSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load inbox_note_ids
        inbox_ids = []
        for note_id in json_obj["inbox_note_ids"]:
            inbox_ids.append(note_id)
        # Load outbox_note_ids
        outbox_ids = []
        for note_id in json_obj["outbox_note_ids"]:
            outbox_ids.append(note_id)
        new_sub = FANotificationNotesSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            inbox_note_ids=inbox_ids,
            outbox_note_ids=outbox_ids,
        )
        new_sub.last_update = last_update
        return new_sub


class FANotificationFavSub(Subscription['FAKey.FAReader.FANotificationFavourite']):
    names: List[str] = [
        "fa favs notifications",
        "fa favs",
        "furaffinity favs",
        "fa favourites notifications",
        "fa favourites",
        "furaffinity favourites",
    ]
    type_name: str = "fa_notif_favs"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        highest_fav_id: Optional[int] = None,
    ):
        """
        :param highest_fav_id: ID number of the highest favourite notification seen
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: FAKey = fa_key
        self.highest_fav_id: int = 0 if highest_fav_id is None else highest_fav_id

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'FANotificationFavSub':
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Cannot create FA favourite notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` "
                "and your cookie values."
            )
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        fa_sub = FANotificationFavSub(
            server, destination, fa_key, update_frequency=search_delta
        )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["favs"]]

    def get_name(self) -> str:
        return "FA favourite notifications for {}".format(self.fa_key.user.name)

    def check(self, *, ignore_result: bool = False) -> List['FAKey.FAReader.FANotificationFavourite']:
        fa_reader = self.fa_key.get_fa_reader()
        notif_page = fa_reader.get_notification_page()
        results = []
        for notif in notif_page.favourites:
            if int(notif.fav_id) > self.highest_fav_id:
                results.append(notif)
        if len(notif_page.favourites) > 0:
            self.highest_fav_id = int(notif_page.favourites[0].fav_id)
        # Update last check time
        self.last_check = datetime.now()
        # Return results
        return results[::-1]

    def format_item(self, new_fav: 'FAKey.FAReader.FANotificationFavourite') -> EventMessage:
        output = (
            "You have a new favourite notification, {} ( http://furaffinity.net/user/{}/ ) "
            'has favourited your submission "{}" {}'.format(
                new_fav.name,
                new_fav.username,
                new_fav.submission_name,
                new_fav.submission_link,
            )
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["highest_fav_id"] = self.highest_fav_id
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'FANotificationFavSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load highest favourite id
        highest_fav_id = None
        if "highest_fav_id" in json_obj:
            highest_fav_id = json_obj["highest_fav_id"]
        new_sub = FANotificationFavSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            highest_fav_id=highest_fav_id,
        )
        new_sub.last_update = last_update
        return new_sub


class FANotificationCommentsSub(
    Subscription[Union[
        'FAKey.FAReader.FANotificationCommentSubmission',
        'FAKey.FAReader.FANotificationCommentJournal',
        'FAKey.FAReader.FANotificationShout'
    ]]
):
    names: List[str] = [
        "{}{}{}".format(fa, comments, notifications)
        for fa in ["fa ", "furaffinity "]
        for comments in ["comments", "comment", "shouts", "shout"]
        for notifications in ["", " notifications"]
    ]
    type_name: str = "fa_notif_comments"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_comment_id_journal: Optional[int] = None,
        latest_comment_id_submission: Optional[int] = None,
        latest_shout_id: Optional[int] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: FAKey = fa_key
        self.latest_comment_id_journal: int = (
            0 if latest_comment_id_journal is None else latest_comment_id_journal
        )
        self.latest_comment_id_submission: int = (
            0 if latest_comment_id_submission is None else latest_comment_id_submission
        )
        self.latest_shout_id: int = 0 if latest_shout_id is None else latest_shout_id

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'FANotificationCommentsSub':
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Cannot create FA comments notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
            )
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        fa_sub = FANotificationCommentsSub(
            server, destination, fa_key, update_frequency=search_delta
        )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["comments"]]

    def get_name(self) -> str:
        return "FA comments for {}".format(self.fa_key.user.name)

    def check(
            self, *, ignore_result: bool = False
    ) -> List[Union[
        'FAKey.FAReader.FANotificationCommentSubmission',
        'FAKey.FAReader.FANotificationCommentJournal',
        'FAKey.FAReader.FANotificationShout'
    ]]:
        notif_page = self.fa_key.get_fa_reader().get_notification_page()
        results = []
        # Check submission comments
        for submission_notif in notif_page.submission_comments:
            if int(submission_notif.comment_id) > self.latest_comment_id_submission:
                results.append(submission_notif)
        # Check journal comments
        for journal_notif in notif_page.journal_comments:
            if int(journal_notif.comment_id) > self.latest_comment_id_journal:
                results.append(journal_notif)
        # Check shouts
        for shout_notif in notif_page.shouts:
            if int(shout_notif.shout_id) > self.latest_shout_id:
                results.append(shout_notif)
        # Reset high water marks.
        if len(notif_page.submission_comments) > 0:
            self.latest_comment_id_submission = int(
                notif_page.submission_comments[0].comment_id
            )
        if len(notif_page.journal_comments) > 0:
            self.latest_comment_id_journal = int(
                notif_page.journal_comments[0].comment_id
            )
        if len(notif_page.shouts) > 0:
            self.latest_shout_id = int(notif_page.shouts[0].shout_id)
        # Update last check time
        self.last_check = datetime.now()
        # Return results
        return results[::-1]

    def format_item(
            self, item: Union[
                'FAKey.FAReader.FANotificationCommentSubmission',
                'FAKey.FAReader.FANotificationCommentJournal',
                'FAKey.FAReader.FANotificationShout'
            ]
    ) -> EventMessage:
        output = "Err, comments did something?"
        fa_reader = self.fa_key.get_fa_reader()
        if isinstance(item, FAKey.FAReader.FANotificationShout):
            try:
                user_page_shouts = fa_reader.get_user_page(item.page_username).shouts
                shout = [
                    shout
                    for shout in user_page_shouts
                    if shout.shout_id == item.shout_id
                ]
                output = (
                    "You have a new shout, from {} ( http://furaffinity.net/user/{}/ ) "
                    "has left a shout saying: \n\n{}".format(
                        item.name, item.username, shout[0].text
                    )
                )
            except HTTPError:
                output = (
                    "You have a new shout, from {} ( http://furaffinity.net/user/{}/ ) "
                    "has left a shout but I can't find it on your user page: \n"
                    "https://furaffinity.net/user/{}/".format(
                        item.name, item.username, item.page_username
                    )
                )
        if isinstance(item, FAKey.FAReader.FANotificationCommentJournal):
            try:
                journal_page = fa_reader.get_journal_page(item.journal_id)
                comment = journal_page.comments_section.get_comment_by_id(
                    item.comment_id
                )
                output = (
                    "You have a journal comment notification. {} has made a new comment {}on {} journal "
                    '"{}" {} : \n\n{}'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.journal_yours else "their"),
                        item.journal_name,
                        item.journal_link,
                        comment.text,
                    )
                )
            except HTTPError:
                output = (
                    "You have a journal comment notification. {} has made a new comment {}on {} journal "
                    '"{}" {} but I can\'t find the comment.'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.journal_yours else "their"),
                        item.journal_name,
                        item.journal_link,
                    )
                )
        if isinstance(item, FAKey.FAReader.FANotificationCommentSubmission):
            try:
                submission_page = fa_reader.get_submission_page(item.submission_id)
                comment = submission_page.comments_section.get_comment_by_id(
                    item.comment_id
                )
                output = (
                    "You have a submission comment notification. "
                    '{} has made a new comment {}on {} submission "{}" {} : \n\n{}'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.submission_yours else "their"),
                        item.submission_name,
                        item.submission_link,
                        comment.text,
                    )
                )
            except HTTPError:
                output = (
                    "You have a submission comment notification. "
                    '{} has made a new comment {}on {} submission "{}" {} : but I can\'t find the comment.'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.submission_yours else "their"),
                        item.submission_name,
                        item.submission_link,
                    )
                )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["latest_comment_id_journal"] = self.latest_comment_id_journal
        json_obj["latest_comment_id_submission"] = self.latest_comment_id_submission
        json_obj["latest_shout_id"] = self.latest_shout_id
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'FANotificationCommentsSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load comment IDs and count
        latest_comment_id_journal = int(json_obj["latest_comment_id_journal"])
        latest_comment_id_submission = int(json_obj["latest_comment_id_submission"])
        latest_shout_id = int(json_obj["latest_shout_id"])
        new_sub = FANotificationCommentsSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            latest_comment_id_journal=latest_comment_id_journal,
            latest_comment_id_submission=latest_comment_id_submission,
            latest_shout_id=latest_shout_id,
        )
        new_sub.last_update = last_update
        return new_sub


class FAUserFavsSub(Subscription[Optional['FAKey.FAReader.FAViewSubmissionPage']]):
    names: List[str] = [
        "fa user favs",
        "furaffinity user favs",
        "furaffinity user favourites",
        "fa user favourites",
        "furaffinity user favorites",
        "fa user favorites",
    ]
    type_name: str = "fa_user_favs"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'FAKey',
        username: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_ids: Optional[List[str]] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: FAKey = fa_key
        self.username: str = username.lower().strip()
        if latest_ids is None:
            latest_ids = []
        self.latest_ids: List[str] = latest_ids

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'FAUserFavsSub':
        # Get FAKey object
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Cannot create FA user favourites subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
            )
        # Get server and destination
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if last argument is check period.
        try:
            try_period = input_evt.command_args.split()[-1]
            search_delta = isodate.parse_duration(try_period)
            username = input_evt.command_args[: -len(try_period)].strip()
        except isodate.isoerror.ISO8601Error:
            username = input_evt.command_args.strip()
            search_delta = isodate.parse_duration("PT600S")
        # Create FA user favs object
        fa_sub = FAUserFavsSub(
            server, destination, fa_key, username, update_frequency=search_delta
        )
        # Check if it's a valid user
        try:
            fa_key.get_fa_reader().get_user_page(username)
        except Exception:
            raise SubscriptionException(
                "This does not appear to be a valid FA username."
            )
        fa_sub.check(ignore_result=True)
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    def get_name(self) -> str:
        return 'Favourites subscription for "{}"'.format(self.username)

    def check(self, *, ignore_result: bool = False) -> List[Optional['FAKey.FAReader.FAViewSubmissionPage']]:
        """
        Returns the list of FA Favourites since the last ones were seen, in oldest->newest order
        """
        fa_reader = self.fa_key.get_fa_reader()
        results = []
        favs_page = fa_reader.get_user_fav_page(self.username)
        next_batch = []
        matched_ids = False
        for result_id in favs_page.fav_ids:
            # Batch things that have been seen, so that the results after the last result in latest_ids aren't included
            if result_id in self.latest_ids:
                results += next_batch
                next_batch = []
                matched_ids = True
            else:
                next_batch.append(result_id)
        # If no images in search matched an ID in last seen, send all results from search
        if not matched_ids:
            results += next_batch
        # Get submission pages for each result
        result_pages = []
        for result_id in results:
            if ignore_result:
                result_pages.append(None)
            else:
                result_pages.append(fa_reader.get_submission_page(result_id))
        # Create new list of latest ten results
        self.latest_ids = favs_page.fav_ids[:10]
        self.last_check = datetime.now()
        return result_pages[::-1]

    def format_item(self, item: Optional['FAKey.FAReader.FAViewSubmissionPage']) -> EventMessage:
        link = "https://furaffinity.net/view/{}".format(item.submission_id)
        title = item.title
        posted_by = item.name
        # Construct output
        output = '{} has favourited a new image. "{}" by {}. {}'.format(
            self.username, title, posted_by, link
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        # Get submission page and file extension
        image_url = item.full_image
        file_extension = image_url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif"]:
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, image_url, inbound=False
            )
            return output_evt
        return EventMessage(self.server, channel, user, output, inbound=False)

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'FAUserFavsSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        username = json_obj["username"]
        # Create FAUserFavsSub
        new_sub = FAUserFavsSub(
            server,
            destination,
            fa_key,
            username,
            last_check=last_check,
            update_frequency=update_frequency,
            latest_ids=latest_ids,
        )
        new_sub.last_update = last_update
        return new_sub

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["username"] = self.username
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj


class FAUserWatchersSub(Subscription['FAKey.FAReader.FAWatch']):
    names: List[str] = [
        "fa user watchers",
        "fa user new watchers",
        "furaffinity user watchers",
        "furaffinity user new watchers",
    ]
    type_name: str = "fa_user_watchers"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'FAKey',
        username: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        newest_watchers: Optional[List[str]] = None,
    ):
        """
        :param newest_watchers: List of user's most recent new watchers' usernames
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: FAKey = fa_key
        self.username: str = username
        self.newest_watchers: List[str] = [] if newest_watchers is None else newest_watchers

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'FAUserWatchersSub':
        # Get FAKey object
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Cannot create FA user watchers subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
            )
        # Get server and destination
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if last argument is check period.
        try:
            try_period = input_evt.command_args.split()[-1]
            search_delta = isodate.parse_duration(try_period)
            username = input_evt.command_args[: -len(try_period)].strip()
        except isodate.isoerror.ISO8601Error:
            username = input_evt.command_args.strip()
            search_delta = isodate.parse_duration("PT600S")
        # Create FA user favs object
        fa_sub = FAUserWatchersSub(
            server, destination, fa_key, username, update_frequency=search_delta
        )
        # Check if it's a valid user
        try:
            fa_key.get_fa_reader().get_user_page(username)
        except Exception:
            raise SubscriptionException("This does not appear to be a valid username.")
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    def get_name(self) -> str:
        return 'New watchers subscription for "{}"'.format(self.username)

    def check(self, *, ignore_result: bool = False) -> List['FAKey.FAReader.FAWatch']:
        fa_reader = self.fa_key.get_fa_reader()
        results = []
        user_page = fa_reader.get_user_page(self.username)
        next_batch = []
        matched_ids = False
        for new_watcher in user_page.watched_by:
            watcher_username = new_watcher.watcher_username
            # Batch things that have been seen, so that the results after the last result in latest_ids aren't included
            if watcher_username in self.newest_watchers:
                results += next_batch
                next_batch = []
                matched_ids = True
            else:
                next_batch.append(new_watcher)
        # If no watchers in list matched an ID in last seen, send all results from list
        if not matched_ids:
            results += next_batch
        # Create new list of latest ten results
        self.newest_watchers = [
            new_watcher.watcher_username for new_watcher in user_page.watched_by
        ]
        self.last_check = datetime.now()
        return results[::-1]

    def format_item(self, item: 'FAKey.FAReader.FAWatch') -> EventMessage:
        link = "https://furaffinity.net/user/{}/".format(item.watcher_username)
        # Construct output
        output = "{} has watched {}. Link: {}".format(
            item.watcher_name, item.watched_name, link
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        return EventMessage(self.server, channel, user, output, inbound=False)

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["username"] = self.username
        json_obj["newest_watchers"] = []
        for new_watcher in self.newest_watchers:
            json_obj["newest_watchers"].append(new_watcher)
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'FAUserWatchersSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load username
        username = json_obj["username"]
        # Load newest watcher list
        newest_watchers = []
        for new_watcher in json_obj["newest_watchers"]:
            newest_watchers.append(new_watcher)
        new_sub = FAUserWatchersSub(
            server,
            destination,
            fa_key,
            username,
            last_check=last_check,
            update_frequency=update_frequency,
            newest_watchers=newest_watchers,
        )
        new_sub.last_update = last_update
        return new_sub


class FANotificationWatchSub(FAUserWatchersSub):
    names: List[str] = [
        "{}{}{}{}".format(fa, new, watchers, notifications)
        for fa in ["fa ", "furaffinity "]
        for new in ["new ", ""]
        for watchers in ["watcher", "watchers"]
        for notifications in ["", " notifications"]
    ]
    type_name: str = "fa_notif_watchers"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        newest_watchers: Optional[str] = None,
    ):
        """
        :param newest_watchers: List of user's most recent new watchers' usernames
        """
        username: str = fa_key.get_fa_reader().get_notification_page().username
        super().__init__(
            server,
            destination,
            fa_key,
            username,
            last_check=last_check,
            update_frequency=update_frequency,
            newest_watchers=newest_watchers,
        )

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'FANotificationWatchSub':
        # Get FAKey object
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Cannot create FA watcher notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
            )
        # Get server and destination
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        # Create FA user watchers object
        try:
            fa_sub = FANotificationWatchSub(
                server, destination, fa_key, update_frequency=search_delta
            )
        except Exception:
            raise SubscriptionException(
                "Yours does not appear to be a valid username? I cannot access your profile page."
            )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["watchers"]]

    def get_name(self) -> str:
        return "New watchers notifications for {}".format(self.fa_key.user.name)

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        del json_obj["username"]
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'FANotificationWatchSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
        assert isinstance(fa_keys, FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load newest watcher list
        newest_watchers = []
        for new_watcher in json_obj["newest_watchers"]:
            newest_watchers.append(new_watcher)
        new_sub = FANotificationWatchSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            newest_watchers=newest_watchers,
        )
        new_sub.last_update = last_update
        return new_sub


class RedditSub(Subscription[Dict]):
    names: List[str] = ["reddit", "subreddit"]
    type_name: str = "subreddit"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        subreddit: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_ids: Optional[List[str]] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.subreddit: str = subreddit
        if latest_ids is None:
            latest_ids = []
        self.latest_ids: List[str] = latest_ids

    @staticmethod
    def create_from_input(input_evt: EventMessage, sub_repo: SubscriptionRepo) -> 'RedditSub':
        # Get event data
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        clean_text = input_evt.command_args.strip().lower()
        text_split = clean_text.split()
        # Subreddit regex
        sub_regex = re.compile(r"r/([^\s]*)/?")
        if len(text_split) == 1:
            sub_name = (
                clean_text
                if sub_regex.search(clean_text) is None
                else sub_regex.search(clean_text).group(1)
            )
            reddit_sub = RedditSub(server, destination, sub_name)
            reddit_sub.check()
            return reddit_sub
        if len(text_split) > 2:
            raise SubscriptionException(
                "Too many arguments. Please give a subreddit, and optionally, a check period."
            )
        try:
            search_delta = isodate.parse_duration(text_split[0])
            subreddit = text_split[1]
        except isodate.isoerror.ISO8601Error:
            subreddit = text_split[0]
            search_delta = isodate.parse_duration(text_split[1])
        sub_name = (
            clean_text
            if sub_regex.search(subreddit) is None
            else sub_regex.search(subreddit).group(1)
        )
        reddit_sub = RedditSub(
            server, destination, sub_name, update_frequency=search_delta
        )
        reddit_sub.check()
        return reddit_sub

    def matches_name(self, name_clean: str) -> bool:
        return (
            self.subreddit == name_clean or "r/{}".format(self.subreddit) in name_clean
        )

    def get_name(self) -> str:
        return "/r/{}".format(self.subreddit)

    def check(self, *, ignore_result: bool = False) -> List[Dict]:
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

    def format_item(self, item: Dict) -> EventMessage:
        # Event destination
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        # Item data
        link = "https://reddit.com/r/{}/comments/{}/".format(
            self.subreddit, item["data"]["id"]
        )
        title = item["data"]["title"]
        author = item["data"]["author"]
        author_link = "https://www.reddit.com/user/{}".format(author)
        url = item["data"]["url"]
        # Check if link is direct to a media file, if so, add photo to output message
        file_extension = url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif", "mp4", "gifv"]:
            if file_extension == "gifv":
                url = url[:-4] + "mp4"
            # Make output message
            output = (
                "Update on /r/{}/ subreddit. "
                '<a href="{}">{}</a> by "<a href="{}">u/{}</a>"\n'
                '<a href="{}">direct image</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    url,
                )
            )
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Handle gfycat links as photos
        gfycat_regex = re.compile(
            r"(?:https?://)?(?:www\.)?gfycat\.com/([a-z]+)", re.IGNORECASE
        )
        gfycat_match = gfycat_regex.match(url)
        if gfycat_match is not None:
            direct_url = "https://giant.gfycat.com/{}.mp4".format(gfycat_match.group(1))
            # Make output message
            output = (
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'
                '<a href="{}">gfycat</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    url,
                )
            )
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, direct_url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Handle reddit video links
        vreddit_regex = re.compile(r"https?://v.redd.it/[a-z0-9]+")
        vreddit_match = vreddit_regex.match(url)
        if vreddit_match is not None:
            if item["data"]["secure_media"] is None:
                direct_url = item["data"]["crosspost_parent_list"][0]["secure_media"][
                    "reddit_video"
                ]["fallback_url"]
            else:
                direct_url = item["data"]["secure_media"]["reddit_video"][
                    "fallback_url"
                ]
            # Make output message
            output = (
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'
                '<a href="{}">vreddit</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    direct_url,
                )
            )
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, direct_url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Make output message if the link isn't direct to a media file
        if item["data"]["selftext"] != "":
            output = (
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                )
            )
        else:
            output = (
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'
                '<a href="{}">{}</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    url,
                    Commons.html_escape(url),
                )
            )
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        output_evt.formatting = EventMessage.Formatting.HTML
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["subreddit"] = self.subreddit
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> 'RedditSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
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
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        subreddit = json_obj["subreddit"]
        new_sub = RedditSub(
            server, destination, subreddit, last_check, update_frequency, latest_ids
        )
        new_sub.last_update = last_update
        return new_sub


class SubscriptionCommon(ABC):
    type_name: str = ""

    def to_json(self) -> Optional[Dict]:
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj: Optional[Dict]) -> 'SubscriptionCommon':
        raise NotImplementedError()


class FAKeysCommon(SubscriptionCommon):
    type_name: str = "fa_keys"

    def __init__(self):
        self.list_keys: Dict[User, FAKey] = dict()

    def get_key_by_user(self, user: User) -> Optional['FAKey']:
        if user in self.list_keys:
            return self.list_keys[user]
        user_data_parser = hallo.modules.user_data.UserDataParser()
        fa_data: hallo.modules.user_data.FAKeyData = user_data_parser.get_data_by_user_and_type(
            user, hallo.modules.user_data.FAKeyData
        )
        if fa_data is None:
            return None
        fa_key = FAKey(user, fa_data.cookie_a, fa_data.cookie_b)
        self.add_key(fa_key)
        return fa_key

    def add_key(self, key: 'FAKey') -> None:
        self.list_keys[key.user] = key

    def to_json(self) -> Optional[Dict]:
        return None

    @staticmethod
    def from_json(json_obj: Optional[Dict]) -> 'FAKeysCommon':
        return FAKeysCommon()


class FAKey:
    def __init__(self, user: User, cookie_a: str, cookie_b: str) -> None:
        self.user = user
        self.cookie_a = cookie_a
        self.cookie_b = cookie_b
        self.fa_reader: Optional[FAKey.FAReader] = None

    def get_fa_reader(self) -> 'FAKey.FAReader':
        if self.fa_reader is None:
            self.fa_reader = FAKey.FAReader(self.cookie_a, self.cookie_b)
        return self.fa_reader

    class FAReader:
        NOTES_INBOX = "inbox"
        NOTES_OUTBOX = "outbox"

        class FALoginFailedError(Exception):
            pass

        def __init__(self, cookie_a: str, cookie_b: str):
            self.a = cookie_a
            self.b = cookie_b
            self.timeout: timedelta = timedelta(seconds=60)
            self.notification_page_cache = CachedObject(
                lambda: FAKey.FAReader.FANotificationsPage(
                    self._get_api_data("notifications/others.json", True)
                ),
                self.timeout,
            )
            self.submissions_page_cache = CachedObject(
                lambda: FAKey.FAReader.FASubmissionsPage(
                    self._get_api_data("notifications/submissions.json", True)
                ),
                self.timeout,
            )
            self.notes_page_inbox_cache = CachedObject(
                lambda: FAKey.FAReader.FANotesPage(
                    self._get_api_data("notes/inbox.json", True), self.NOTES_INBOX
                ),
                self.timeout,
            )
            self.notes_page_outbox_cache = CachedObject(
                lambda: FAKey.FAReader.FANotesPage(
                    self._get_api_data("notes/outbox.json", True), self.NOTES_OUTBOX
                ),
                self.timeout,
            )

        def _get_api_data(self, path: str, needs_cookie: bool = False) -> Dict:
            fa_api_url = os.getenv("FA_API_URL", "https://faexport.spangle.org.uk")
            url = "{}/{}".format(fa_api_url, path)
            if needs_cookie:
                cookie_string = "b=" + self.b + "; a=" + self.a
                return Commons.load_url_json(url, [["FA_COOKIE", cookie_string]])
            return Commons.load_url_json(url)

        def get_notification_page(self) -> 'FAKey.FAReader.FANotificationsPage':
            return self.notification_page_cache.get()

        def get_submissions_page(self) -> 'FAKey.FAReader.FASubmissionsPage':
            return self.submissions_page_cache.get()

        def get_notes_page(self, folder: str) -> 'FAKey.FAReader.FANotesPage':
            if folder == self.NOTES_INBOX:
                return self.notes_page_inbox_cache.get()
            if folder == self.NOTES_OUTBOX:
                return self.notes_page_outbox_cache.get()
            raise ValueError("Invalid FA note folder.")

        def get_user_page(self, username: str) -> 'FAKey.FAReader.FAUserPage':
            # Needs shout list, for checking own shouts
            data = self._get_api_data("/user/{}.json".format(username))

            def shout_data_getter():
                return self._get_api_data("/user/{}/shouts.json".format(username))

            user_page = FAKey.FAReader.FAUserPage(data, shout_data_getter, username)
            return user_page

        def get_user_fav_page(self, username: str) -> 'FAKey.FAReader.FAUserFavouritesPage':
            id_list = self._get_api_data("/user/{}/favorites.json".format(username))
            fav_page = FAKey.FAReader.FAUserFavouritesPage(id_list, username)
            return fav_page

        def get_submission_page(self, submission_id: Union[int, str]) -> 'FAKey.FAReader.FAViewSubmissionPage':
            data = self._get_api_data("/submission/{}.json".format(submission_id))

            def comment_data_getter():
                return self._get_api_data(
                    "/submission/{}/comments.json".format(submission_id)
                )

            sub_page = FAKey.FAReader.FAViewSubmissionPage(
                data, comment_data_getter, submission_id
            )
            return sub_page

        def get_journal_page(self, journal_id: Union[int, str]) -> 'FAKey.FAReader.FAViewJournalPage':
            data = self._get_api_data("/journal/{}.json".format(journal_id))

            def comment_data_getter():
                return self._get_api_data(
                    "/journal/{}/comments.json".format(journal_id)
                )

            journal_page = FAKey.FAReader.FAViewJournalPage(
                data, comment_data_getter, journal_id
            )
            return journal_page

        def get_search_page(self, search_term: str) -> 'FAKey.FAReader.FASearchPage':
            id_list = self._get_api_data("/search.json?q={}".format(search_term))
            search_page = FAKey.FAReader.FASearchPage(id_list, search_term)
            return search_page

        class FANotificationsPage:
            def __init__(self, data: Dict):
                self.username: str = data["current_user"]["profile_name"]
                self.watches: List[FAKey.FAReader.FANotificationWatch] = []
                watch_list = data["new_watches"]
                for watch_notif in watch_list:
                    try:
                        new_watch = FAKey.FAReader.FANotificationWatch(
                            watch_notif["name"],
                            watch_notif["profile_name"],
                            watch_notif["avatar"],
                        )
                        self.watches.append(new_watch)
                    except Exception as e:
                        logger.error("Failed to read watch: ", exc_info=e)
                self.submission_comments: List[FAKey.FAReader.FANotificationCommentSubmission] = []
                sub_comment_list = data["new_submission_comments"]
                for sub_comment_notif in sub_comment_list:
                    try:
                        new_comment = FAKey.FAReader.FANotificationCommentSubmission(
                            sub_comment_notif["comment_id"],
                            sub_comment_notif["profile_name"],
                            sub_comment_notif["name"],
                            sub_comment_notif["is_reply"],
                            sub_comment_notif["your_submission"],
                            sub_comment_notif["submission_id"],
                            sub_comment_notif["title"],
                        )
                        self.submission_comments.append(new_comment)
                    except Exception as e:
                        logger.error("Failed to read submission comment: ", exc_info=e)
                self.journal_comments: List[FAKey.FAReader.FANotificationCommentJournal] = []
                jou_comment_list = data["new_journal_comments"]
                for jou_comment_notif in jou_comment_list:
                    try:
                        new_comment = FAKey.FAReader.FANotificationCommentJournal(
                            jou_comment_notif["comment_id"],
                            jou_comment_notif["profile_name"],
                            jou_comment_notif["name"],
                            jou_comment_notif["is_reply"],
                            jou_comment_notif["your_journal"],
                            jou_comment_notif["journal_id"],
                            jou_comment_notif["title"],
                        )
                        self.journal_comments.append(new_comment)
                    except Exception as e:
                        logger.error("Failed to read journal comment: ", exc_info=e)
                self.shouts: List[FAKey.FAReader.FANotificationShout] = []
                shout_list = data["new_shouts"]
                for shout_notif in shout_list:
                    try:
                        new_shout = FAKey.FAReader.FANotificationShout(
                            shout_notif["shout_id"],
                            shout_notif["profile_name"],
                            shout_notif["name"],
                            data["current_user"]["profile_name"],
                        )
                        self.shouts.append(new_shout)
                    except Exception as e:
                        logger.error("Failed to read shout: ", exc_info=e)
                self.favourites: List[FAKey.FAReader.FANotificationFavourite] = []
                fav_list = data["new_favorites"]
                for fav_notif in fav_list:
                    try:
                        new_fav = FAKey.FAReader.FANotificationFavourite(
                            fav_notif["favorite_notification_id"],
                            fav_notif["profile_name"],
                            fav_notif["name"],
                            fav_notif["submission_id"],
                            fav_notif["submission_name"],
                        )
                        self.favourites.append(new_fav)
                    except Exception as e:
                        logger.error("Failed to read favourite: ", exc_info=e)
                self.journals: List[FAKey.FAReader.FANotificationJournal] = []
                jou_list = data["new_journals"]
                for jou_notif in jou_list:
                    try:
                        new_journal = FAKey.FAReader.FANotificationJournal(
                            jou_notif["journal_id"],
                            jou_notif["title"],
                            jou_notif["profile_name"],
                            jou_notif["name"],
                        )
                        self.journals.append(new_journal)
                    except Exception as e:
                        logger.error("Failed to read journal: ", exc_info=e)

        class FANotificationWatch:
            def __init__(self, name: str, username: str, avatar: str):
                self.name: str = name
                self.username: str = username
                self.link: str = "https://furaffinity.net/user/{}/".format(username)
                self.avatar: str = avatar

        class FANotificationCommentSubmission:
            def __init__(
                self,
                comment_id: str,
                username: str,
                name: str,
                comment_on: bool,
                submission_yours: bool,
                submission_id: str,
                submission_name: str,
            ):
                self.comment_id: str = comment_id
                self.comment_link: str = "https://furaffinity.net/view/{}/#cid:{}".format(
                    submission_id, comment_id
                )
                self.username: str = username
                self.name: str = name
                self.comment_on: bool = comment_on
                self.submission_yours: bool = submission_yours
                self.submission_id = submission_id
                self.submission_name = submission_name
                self.submission_link: str = "https://furaffinity.net/view/{}/".format(
                    submission_id
                )

        class FANotificationCommentJournal:
            def __init__(
                self,
                comment_id: str,
                username: str,
                name: str,
                comment_on: bool,
                journal_yours: bool,
                journal_id: str,
                journal_name: str,
            ):
                self.comment_id: str = comment_id
                self.comment_link: str = "https://furaffinity.net/journal/{}/#cid:{}".format(
                    journal_id, comment_id
                )
                self.username: str = username
                self.name: str = name
                self.comment_on: bool = comment_on
                self.journal_yours: bool = journal_yours
                self.journal_id: str = journal_id
                self.journal_name: str = journal_name
                self.journal_link: str = "https://furaffinity.net/journal/{}/".format(
                    journal_id
                )

        class FANotificationShout:
            def __init__(self, shout_id: str, username: str, name: str, page_username: str):
                self.shout_id: str = shout_id
                self.username: str = username
                self.name: str = name
                self.page_username: str = page_username

        class FANotificationFavourite:
            def __init__(self, fav_id: str, username: str, name: str, submission_id: str, submission_name: str):
                self.fav_id: str = fav_id
                self.username: str = username
                self.name: str = name
                self.submission_id: str = submission_id
                self.submission_name: str = submission_name
                self.submission_link: str = "https://furaffinity.net/view/{}/".format(
                    submission_id
                )

        class FANotificationJournal:
            def __init__(self, journal_id: str, journal_name: str, username: str, name: str):
                self.journal_id: str = journal_id
                self.journal_link: str = "https://furaffinity.net/journal/{}/".format(
                    journal_id
                )
                self.journal_name: str = journal_name
                self.username: str = username
                self.name: str = name

        class FASubmissionsPage:
            def __init__(self, data: Dict):
                self.submissions: List[FAKey.FAReader.FANotificationSubmission] = []
                subs_list = data["new_submissions"]
                for sub_notif in subs_list:
                    new_submission = FAKey.FAReader.FANotificationSubmission(
                        sub_notif["id"],
                        sub_notif["link"],
                        sub_notif["title"],
                        sub_notif["profile_name"],
                        sub_notif["name"],
                    )
                    self.submissions.append(new_submission)

        class FANotificationSubmission:
            def __init__(self, submission_id: str, preview_link: str, title: str, username: str, name: str):
                self.submission_id: str = submission_id
                self.submission_link: str = "https://furaffinity.net/view/{}/".format(
                    submission_id
                )
                self.preview_link: str = preview_link
                self.title: str = title
                self.username: str = username
                self.name: str = name

        class FANotesPage:
            def __init__(self, data: Dict, folder: str):
                self.folder: str = folder
                self.notes: List[FAKey.FAReader.FANote] = []
                for note in data:
                    new_note = FAKey.FAReader.FANote(
                        note["note_id"],
                        note["subject"],
                        note["profile_name"],
                        note["name"],
                        note["is_read"],
                    )
                    self.notes.append(new_note)

        class FANote:
            def __init__(self, note_id: str, subject: str, username: str, name: str, is_read: bool):
                self.note_id: str = note_id
                self.note_link: str = "https://www.furaffinity.net/viewmessage/{}/".format(
                    note_id
                )
                self.subject: str = subject
                self.username: str = username
                self.name: str = name
                self.is_read: bool = is_read

        class FAUserPage:
            def __init__(self, data: Dict, shout_data_getter: Callable[[], Dict], username: str):
                self.username: str = username
                self.name: str = data["full_name"]
                self.user_title: Optional[str] = (
                    data["user_title"] if len(data["user_title"]) != 0 else None
                )
                self.registered_since: datetime = dateutil.parser.parse(data["registered_at"])
                self.current_mood: str = data["current_mood"]
                # artist_profile
                self.num_page_visits: int = int(data["pageviews"])
                self.num_submissions: int = int(data["submissions"])
                self.num_comments_received: int = int(data["comments_received"])
                self.num_comments_given: int = int(data["comments_given"])
                self.num_journals: int = int(data["journals"])
                self.num_favourites: int = int(data["favorites"])
                # artist_info
                # contact_info
                # featured_submission
                self._shout_data_getter: Callable[[], Dict] = shout_data_getter
                self._shout_cache: Optional[List[FAKey.FAReader.FAShout]] = None
                # watcher lists
                self.watched_by: List[FAKey.FAReader.FAWatch] = []
                for watch in data["watchers"]["recent"]:
                    watcher_username = watch["link"].split("/")[-2]
                    watcher_name = watch["name"]
                    new_watch = FAKey.FAReader.FAWatch(
                        watcher_username, watcher_name, self.username, self.name
                    )
                    self.watched_by.append(new_watch)
                self.is_watching: List[FAKey.FAReader.FAWatch] = []
                for watch in data["watching"]["recent"]:
                    watched_username = watch["link"].split("/")[-2]
                    watched_name = watch["name"]
                    new_watch = FAKey.FAReader.FAWatch(
                        self.username, self.name, watched_username, watched_name
                    )
                    self.is_watching.append(new_watch)

            @property
            def shouts(self) -> List['FAKey.FAReader.FAShout']:
                if self._shout_cache is None:
                    shout_data = self._shout_data_getter()
                    for shout in shout_data:
                        shout_id = shout["id"].replace("shout-", "")
                        username = shout["profile_name"]
                        name = shout["name"]
                        avatar = shout["avatar"]
                        text = shout["text"]
                        new_shout = FAKey.FAReader.FAShout(
                            shout_id, username, name, avatar, text
                        )
                        self.shouts.append(new_shout)
                return self._shout_cache

        class FAShout:
            def __init__(self, shout_id: str, username: str, name: str, avatar: str, text: str):
                self.shout_id: str = shout_id
                self.username: str = username
                self.name: str = name
                self.avatar: str = avatar
                self.text: str = text

        class FAWatch:
            def __init__(
                self, watcher_username: str, watcher_name: str, watched_username: str, watched_name: str
            ):
                self.watcher_username: str = watcher_username
                self.watcher_name: str = watcher_name
                self.watched_username: str = watched_username
                self.watched_name: str = watched_name

        class FAUserFavouritesPage:
            def __init__(self, id_list: List[int], username: str):
                self.username: str = username
                self.fav_ids: List[int] = id_list

        class FAViewSubmissionPage:
            def __init__(self, data: Dict, comments_data_getter: Callable[[], Dict], submission_id: str):
                self.submission_id: str = submission_id
                self.title: str = data["title"]
                self.full_image: str = data["download"]
                self.username: str = data["profile_name"]
                self.name: str = data["name"]
                self.avatar_link: str = data["avatar"]
                self.description: str = data["description_body"]
                submission_time_str = data["posted_at"]
                self.submission_time: datetime = dateutil.parser.parse(submission_time_str)
                self.category: str = data["category"]
                self.theme: str = data["theme"]
                self.species: str = data["species"]
                self.gender: str = data["gender"]
                self.num_favourites: int = int(data["favorites"])
                self.num_comments: int = int(data["comments"])
                self.num_views: int = int(data["views"])
                # resolution_x = None
                # resolution_y = None
                self.keywords: List[str] = data["keywords"]
                self.rating: str = data["rating"]
                self._comments_section_getter: Callable[[], Dict] = comments_data_getter
                self._comments_section_cache: Optional[FAKey.FAReader.FACommentsSection] = None

            @property
            def comments_section(self) -> 'FAKey.FAReader.FACommentsSection':
                if self._comments_section_cache is None:
                    comments_data = self._comments_section_getter()
                    self._comments_section_cache = FAKey.FAReader.FACommentsSection(
                        comments_data
                    )
                return self._comments_section_cache

        class FACommentsSection:
            def __init__(self, comments_data: Dict):
                self.top_level_comments: List[FAKey.FAReader.FAComment] = []
                for comment in comments_data:
                    username = comment["profile_name"]
                    name = comment["name"]
                    avatar_link = comment["avatar"]
                    comment_id = comment["id"]
                    posted_datetime = dateutil.parser.parse(comment["posted_at"])
                    text = comment["text"].strip()
                    new_comment = FAKey.FAReader.FAComment(
                        username, name, avatar_link, comment_id, posted_datetime, text
                    )
                    if comment["reply_to"] == "":
                        self.top_level_comments.append(new_comment)
                    else:
                        parent_id = comment["reply_to"]
                        parent_comment = self.get_comment_by_id(parent_id)
                        new_comment.parent = parent_comment
                        parent_comment.reply_comments.append(new_comment)

            def get_comment_by_id(
                    self, comment_id: str, parent_comment: Optional['FAKey.FAReader.FAComment'] = None
            ) -> Optional['FAKey.FAReader.FAComment']:
                if parent_comment is None:
                    for comment in self.top_level_comments:
                        found_comment = self.get_comment_by_id(comment_id, comment)
                        if found_comment is not None:
                            return found_comment
                    return None
                if parent_comment.comment_id == comment_id:
                    return parent_comment
                for comment in parent_comment.reply_comments:
                    found_comment = self.get_comment_by_id(comment_id, comment)
                    if found_comment is not None:
                        return found_comment
                return None

        class FAComment:
            def __init__(
                self,
                username: str,
                name: str,
                avatar_link: str,
                comment_id: str,
                posted_datetime: datetime,
                text: str,
                parent_comment: Optional['FAKey.FAReader.FAComment'] = None,
            ):
                self.username: str = username
                self.name: str = name
                self.avatar_link: str = avatar_link
                self.comment_id: str = comment_id
                self.posted_datetime: datetime = posted_datetime
                self.text: str = text
                self.parent_comment: Optional[FAKey.FAReader.FAComment] = parent_comment
                self.reply_comments: List[FAKey.FAReader.FAComment] = []

        class FAViewJournalPage:
            def __init__(self, data: Dict, comments_data_getter: Callable[[], Dict], journal_id: str):
                self.journal_id: str = journal_id
                self.username: str = data["profile_name"]
                self.name: str = data["name"]
                self.avatar_link: Optional[str] = data["avatar"]
                self.title: str = data["title"]
                self.posted_datetime: datetime = dateutil.parser.parse(data["posted_at"])
                self.journal_header: Optional[str] = data["journal_header"]
                self.journal_text: str = data["journal_body"]
                self.journal_footer: Optional[str] = data["journal_footer"]
                self._comments_section_getter: Callable[[], Dict] = comments_data_getter
                self._comments_section_cache: Optional[FAKey.FAReader.FACommentsSection] = None

            @property
            def comments_section(self) -> 'FAKey.FAReader.FACommentsSection':
                if self._comments_section_cache is None:
                    comments_data = self._comments_section_getter()
                    self._comments_section_cache = FAKey.FAReader.FACommentsSection(
                        comments_data
                    )
                return self._comments_section_cache

        class FASearchPage:
            def __init__(self, id_list: List[str], search_term: str):
                self.search_term: str = search_term
                self.id_list: List[str] = id_list


class SubscriptionFactory(object):
    sub_classes: List[Type[Subscription]] = [
        E621Sub,
        E621TaggingSub,
        RssSub,
        FANotificationNotesSub,
        FAUserFavsSub,
        FAUserWatchersSub,
        FANotificationWatchSub,
        FANotificationFavSub,
        FANotificationCommentsSub,
        RedditSub,
    ]
    common_classes: List[Type[SubscriptionCommon]] = [FAKeysCommon]

    @staticmethod
    def get_names() -> List[str]:
        return [
            name
            for sub_class in SubscriptionFactory.sub_classes
            for name in sub_class.names
        ]

    @staticmethod
    def get_class_by_name(name: str) -> Type[Subscription]:
        classes = [
            sub_class
            for sub_class in SubscriptionFactory.sub_classes
            if name in sub_class.names
        ]
        if len(classes) != 1:
            raise SubscriptionException(
                "Failed to find a subscription type matching the name {}".format(name)
            )
        return classes[0]

    @staticmethod
    def from_json(sub_json: Dict, hallo_obj: Hallo, sub_repo: SubscriptionRepo) -> Subscription:
        sub_type_name = sub_json["sub_type"]
        for sub_class in SubscriptionFactory.sub_classes:
            if sub_class.type_name == sub_type_name:
                return sub_class.from_json(sub_json, hallo_obj, sub_repo)
        raise SubscriptionException(
            "Could not load subscription of type {}".format(sub_type_name)
        )

    @staticmethod
    def common_from_json(common_json: Dict) -> SubscriptionCommon:
        common_type_name = common_json["common_type"]
        for common_class in SubscriptionFactory.common_classes:
            if common_class.type_name == common_type_name:
                return common_class.from_json(common_json)
        raise SubscriptionException(
            "Could not load common configuration of type {}".format(common_type_name)
        )


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
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, add, sub)
                for name in SubscriptionFactory.get_names()
                for template in name_templates
                for add in self.add_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Adds a new subscription to be checked for updates which will be posted to the current location."
            " Format: add subscription <sub type> <sub details> <update period?>"
        )

    def run(self, event: EventMessage) -> EventMessage:
        # Construct type name
        sub_type_name = " ".join(
            [
                w
                for w in event.command_name.lower().split()
                if w not in self.sub_words + self.add_words
            ]
        ).strip()
        # Get class from sub type name
        sub_class = SubscriptionFactory.get_class_by_name(sub_type_name)
        # Get current RSS feed list
        function_dispatcher = event.server.hallo.function_dispatcher
        sub_check_class = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_class
        )  # type: SubscriptionCheck
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
        return event.create_response(
            "Created a new {} subscription for {}".format(
                sub_class.type_name, sub_obj.get_name()
            )
        )


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
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {2}",
            "{2} {1}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, remove, sub)
                for name in SubscriptionFactory.get_names()
                for template in name_templates
                for remove in self.remove_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Removes a specified subscription the current location. "
            " Format: remove subscription <feed type> <feed title or url>"
        )

    def run(self, event: EventMessage) -> EventMessage:
        # Handy variables
        server = event.server
        hallo_obj = server.hallo
        function_dispatcher = hallo_obj.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name(
            "check subscription"
        )
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_function
        )  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(hallo_obj)
        # Clean up input
        clean_input = event.command_args.strip()
        # Acquire lock
        with sub_repo.sub_lock:
            # Find any feeds with specified title
            test_subs = sub_repo.get_subs_by_name(
                clean_input.lower(),
                event.user if event.channel is None else event.channel,
            )
            if len(test_subs) == 1:
                del_sub = test_subs[0]
                sub_repo.remove_sub(del_sub)
                return event.create_response(
                    "Removed {} subscription to {}. Updates will no longer be sent to {}.".format(
                        del_sub.type_name, del_sub.get_name(), del_sub.destination.name
                    )
                )
            if len(test_subs) > 1:
                for del_sub in test_subs:
                    sub_repo.remove_sub(del_sub)
                return event.create_response(
                    "Removed {} subscriptions.\n{}".format(
                        len(test_subs),
                        "\n".join(
                            [
                                "{} - {}".format(del_sub.type_name, del_sub.get_name())
                                for del_sub in test_subs
                            ]
                        ),
                    )
                )
        return event.create_response(
            "Error, there are no subscriptions in this channel matching that name."
        )


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
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {2}",
            "{2} {1}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, check, sub)
                for name in SubscriptionFactory.get_names()
                for template in name_templates
                for check in self.check_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Checks a specified feed for updates and returns them. Format: subscription check <feed name>"
        self.subscription_repo = None
        """ :type : SubscriptionRepo | None"""

    def get_sub_repo(self, hallo_obj: Hallo) -> SubscriptionRepo:
        if self.subscription_repo is None:
            self.subscription_repo = SubscriptionRepo.load_json(hallo_obj)
        return self.subscription_repo

    @staticmethod
    def is_persistent() -> bool:
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return True

    @staticmethod
    def load_function() -> 'SubscriptionCheck':
        """Loads the function, persistent functions only."""
        return SubscriptionCheck()

    def save_function(self) -> None:
        """Saves the function, persistent functions only."""
        if self.subscription_repo is not None:
            self.subscription_repo.save_json()

    def get_passive_events(self) -> Set[Type[Event]]:
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMinute}

    def run(self, event: EventMessage) -> EventMessage:
        # Handy variables
        hallo_obj = event.server.hallo
        destination = event.user if event.channel is None else event.channel
        # Clean up input
        clean_input = event.command_args.strip().lower()
        # Acquire lock
        sub_repo = self.get_sub_repo(hallo_obj)
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
                    error = SubscriptionCheckError(search_sub, e)
                    logger.error(error.get_log_line())
            # Save list
            sub_repo.save_json()
        # Output response to user
        if found_items == 0:
            return event.create_response(
                "There were no updates for specified subscriptions."
            )
        return event.create_response(
            "{} subscription updates were found.".format(found_items)
        )

    def passive_run(self, event: Event, hallo_obj: Hallo) -> Optional[ServerEvent]:
        """
        Replies to an event not directly addressed to the bot.
        :type event: events.Event
        :type hallo_obj: hallo.Hallo
        """
        # Check through all feeds to see which need updates
        sub_repo = self.get_sub_repo(hallo_obj)
        with sub_repo.sub_lock:
            logger.debug("SubCheck - Got lock")
            for search_sub in sub_repo.sub_list:
                # Only check those which have been too long since last check
                if search_sub.needs_check():
                    # Get new items
                    try:
                        logger.debug("SubCheck - Checking %s", search_sub)
                        new_items = search_sub.check()
                        logger.debug("SubCheck - Got %s new items", len(new_items))
                        # Output all new items
                        for search_item in new_items:
                            logger.debug("SubCheck - Sending")
                            search_sub.send_item(search_item)
                    except Exception as e:
                        error = SubscriptionCheckError(search_sub, e)
                        logger.error(error.get_log_line())
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
        name_templates = {
            "{0} {1}",
            "{1} {0}",
            "{1} {2}",
            "{2} {1}",
            "{1} {0} {2}",
            "{1} {2} {0}",
            "{2} {0} {1}",
            "{0} {2} {1}",
        }
        self.names = set(
            [
                template.format(name, list_word, sub)
                for name in SubscriptionFactory.get_names()
                for template in name_templates
                for list_word in self.list_words
                for sub in self.sub_words
            ]
        )
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Lists subscriptions for the current channel. Format: list subscription"
        )

    def run(self, event: EventMessage) -> EventMessage:
        # Handy variables
        server = event.server
        hallo_obj = server.hallo
        function_dispatcher = hallo_obj.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name(
            "check subscription"
        )
        sub_check_obj = function_dispatcher.get_function_object(
            sub_check_function
        )  # type: SubscriptionCheck
        sub_repo = sub_check_obj.get_sub_repo(hallo_obj)
        # Find list of feeds for current channel.
        with sub_repo.sub_lock:
            dest_searches = sub_repo.get_subs_by_destination(
                event.user if event.channel is None else event.channel
            )
        if len(dest_searches) == 0:
            return event.create_response(
                "There are no subscriptions posting to this destination."
            )
        output_lines = ["Subscriptions posting to this channel:"]
        for search_item in dest_searches:
            new_line = "{} - {}".format(search_item.type_name, search_item.get_name())
            if search_item.last_update is not None:
                new_line += " ({})".format(
                    search_item.last_update.strftime("%Y-%m-%d %H:%M:%S")
                )
            output_lines.append(new_line)
        return event.create_response("\n".join(output_lines))


class GoogleDocsSub(Subscription):
    pass


class TwitterSub(Subscription):
    pass


class YoutubeSub(Subscription):
    pass


class ImgurSub(Subscription):
    pass
