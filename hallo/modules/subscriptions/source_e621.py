import urllib.parse
from typing import Dict, List, Optional

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.commons import Commons
import hallo.modules.subscriptions.stream_source
from hallo.server import Server


class E621Source(hallo.modules.subscriptions.stream_source.StreamSource[Dict]):
    type_name: str = "e621"
    type_names: List[str] = ["e621", "e621 search", "search e621"]

    def __init__(self, search: str, last_keys: List[hallo.modules.subscriptions.stream_source.Key] = None):
        super().__init__(last_keys)
        self.search: str = search

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.search.lower().strip()

    @property
    def title(self) -> str:
        return f"search for \"{self.search}\""

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'E621Source':
        return E621Source(
            argument
        )

    def current_state(self) -> List[Dict]:
        search = "{} order:-id".format(self.search)  # Sort by id
        url = "https://e621.net/posts.json?tags={}&limit=50".format(
            urllib.parse.quote(search)
        )
        results = Commons.load_url_json(url)
        return results["posts"]

    def item_to_key(self, item: Dict) -> hallo.modules.subscriptions.stream_source.Key:
        return item["id"]

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: Dict
    ) -> EventMessage:
        link = "https://e621.net/posts/{}".format(item["id"])
        # Create rating string
        rating_dict = {"e": "(Explicit)", "q": "(Questionable)", "s": "(Safe)"}
        rating = rating_dict.get(item["rating"], "(Unknown)")
        # Construct output
        output = 'Update on "{}" e621 search. {} {}'.format(self.search, link, rating)
        if item["file"]["ext"] in ["swf", "webm"] or item["file"]["url"] is None:
            return EventMessage(server, channel, user, output, inbound=False)
        image_url = item["file"]["url"]
        return EventMessageWithPhoto(
            server, channel, user, output, image_url, inbound=False
        )

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'E621Source':
        return E621Source(
            json_data["search"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "search": self.search
        }
