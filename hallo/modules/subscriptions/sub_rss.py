import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from xml.etree import ElementTree

import isodate
from bs4 import BeautifulSoup

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.hallo import Hallo
from hallo.inc.commons import Commons
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class RssSub(hallo.modules.subscriptions.subscriptions.Subscription[ElementTree.Element]):
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

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            sub_repo
    ) -> 'RssSub':
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
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Failed to create RSS subscription", e
            )
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
        if "nitter.net" in self.url:
            item_title = self._get_item_title(rss_item)
            item_link = self._get_item_link(rss_item).replace("nitter.net", "twitter.com")
            # Construct output
            output = 'Update on "{}" RSS feed. "{}" {}'.format(
                self.title, item_title, item_link
            )
            channel = self.destination if isinstance(self.destination, Channel) else None
            user = self.destination if isinstance(self.destination, User) else None
            output_evt = EventMessage(self.server, channel, user, output, inbound=False)
            return output_evt
        return None

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["title"] = self.title
        json_obj["url"] = self.url
        json_obj["last_item"] = self.last_item_hash
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'RssSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
        # Load channel or user
        if "channel_address" in json_obj:
            destination = server.get_channel_by_address(json_obj["channel_address"])
        else:
            if "user_address" in json_obj:
                destination = server.get_user_by_address(json_obj["user_address"])
            else:
                raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                    "Channel or user must be defined."
                )
        if destination is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException("Could not find chanel or user.")
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
