import hashlib
import re
from typing import List, Dict, Optional
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.commons import Commons
from hallo.modules.new_subscriptions.stream_source import StreamSource, Key
from hallo.server import Server


def _get_item_title(feed_item: ElementTree.Element) -> str:
    title_elem = feed_item.find("title")
    if title_elem is not None:
        return title_elem.text
    return feed_item.find("{http://www.w3.org/2005/Atom}title").text


def _get_item_link(feed_item: ElementTree.Element) -> str:
    link_elem = feed_item.find("link")
    if link_elem is not None:
        return link_elem.text
    return feed_item.find("{http://www.w3.org/2005/Atom}link").get("href")


def _get_feed_items(rss_elem: ElementTree.Element) -> List[ElementTree.Element]:
    channel_elem = rss_elem.find("channel")
    if channel_elem is not None:
        return channel_elem.findall("item")
    else:
        return rss_elem.findall("{http://www.w3.org/2005/Atom}entry")


class RssSource(StreamSource[ElementTree.Element]):
    names: List[str] = ["rss", "rss feed"]
    type_name: str = "rss"

    def __init__(self, url: str, feed_title: Optional[str] = None, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.url = url
        if feed_title is None:
            feed_title = self._get_feed_title()
        self.feed_title = feed_title

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

    def current_state(self) -> List[ElementTree.Element]:
        rss_data = self.get_rss_data()
        rss_elem = ElementTree.fromstring(rss_data)
        # Update title
        self.feed_title = self._get_feed_title()
        return _get_feed_items(rss_elem)

    def item_to_key(self, item: ElementTree.Element) -> Key:
        item_guid_elem = item.find("guid")
        if item_guid_elem is not None:
            item_hash = item_guid_elem.text
        else:
            item_link_elem = item.find("link")
            if item_link_elem is not None:
                item_hash = item_link_elem.text
            else:
                item_xml = ElementTree.tostring(item)
                item_hash = hashlib.md5(item_xml).hexdigest()
        return item_hash

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: ElementTree.Element
    ) -> EventMessage:
        # Check custom formatting
        custom_evt = self._format_custom_sites(server, channel, user, item)
        if custom_evt is not None:
            return custom_evt
        # Load item xml
        item_title = _get_item_title(item)
        item_link = _get_item_link(item)
        # Construct output
        output = f'Update on "{self.feed_title}" RSS feed. "{item_title}" {item_link}'
        output_evt = EventMessage(server, channel, user, output, inbound=False)
        return output_evt

    def _format_custom_sites(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: ElementTree.Element
    ) -> Optional[EventMessage]:
        if "xkcd.com" in self.url:
            item_title = item.find("title").text
            item_link = item.find("link").text
            comic_number = item_link.strip("/").split("/")[-1]
            json_link = f"https://xkcd.com/{comic_number}/info.0.json"
            comic_json = Commons.load_url_json(json_link)
            alt_text = comic_json["alt"]
            output = f'Update on "{self.feed_title}" RSS feed. "{item_title}" {item_link}\nAlt text: {alt_text}'
            return EventMessage(server, channel, user, output, inbound=False)
        if "awoocomic" in self.feed_title:
            item_title = item.find("title").text
            if " - " in item_title:
                item_title = item_title.split(" - ")[0]
            item_link = item.find("link").text
            output = f'Update on "{self.feed_title}" RSS feed. "{item_title}" {item_link}'
            return EventMessage(server, channel, user, output, inbound=False)
        if "smbc-comics.com" in self.url:
            item_title = item.find("title").text
            item_link = item.find("link").text
            page_code = Commons.load_url_string(item_link)
            soup = BeautifulSoup(page_code, "html.parser")
            comic_img = soup.select_one("img#cc-comic")
            alt_text = comic_img["title"]
            after_comic_img = soup.select_one("#aftercomic img")
            return EventMessageWithPhoto(
                server,
                channel,
                user,
                f'Update on "{self.feed_title}" RSS feed. "{item_title}" {item_link}\nAlt text: {alt_text}',
                [comic_img["src"], after_comic_img["src"]],
                inbound=False
            )
        if "rss.app" in self.url:
            item_title = _get_item_title(item)
            item_link = _get_item_link(item)
            page_code = Commons.load_url_string(item_link)
            soup = BeautifulSoup(page_code, "html.parser")
            head_script = soup.select_one("head script")
            if head_script is None:
                return None
            url_regex = re.compile(r"var url = \"([^\"]+)\";", re.IGNORECASE)
            url_result = url_regex.search(head_script.text)
            if url_result is None:
                return None
            output = f'Update on "{self.feed_title}" RSS feed. "{item_title}" {url_result.group(1)}'
            return EventMessage(server, channel, user, output, inbound=False)
        if "nitter.net" in self.url:
            item_title = _get_item_title(item)
            item_link = _get_item_link(item).replace("nitter.net", "twitter.com")
            # Construct output
            output = f'Update on "{self.feed_title}" RSS feed. "{item_title}" {item_link}'
            output_evt = EventMessage(server, channel, user, output, inbound=False)
            return output_evt
        return None

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [
            self.feed_title.lower().strip(),
            self.url.lower().strip(),
            self.title.lower().strip(),
        ]

    @property
    def title(self) -> str:
        return f"{self.feed_title} ({self.url})"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'RssSource':
        return RssSource(argument)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'RssSource':
        return RssSource(
            json_data["url"],
            json_data["title"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "url": self.url,
            "title": self.feed_title,
            "last_keys": self.last_keys
        }
