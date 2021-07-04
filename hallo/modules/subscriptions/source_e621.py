import urllib.parse
from typing import Dict, List, Optional

from yippi import Post, Rating, YippiClient

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.subscription_exception
import hallo.modules.subscriptions.common_e6_key
from hallo.server import Server


def e6_client_from_json(user_addr: str, server: Server, sub_repo) -> YippiClient:
    user = server.get_user_by_address(user_addr)
    if user is None:
        raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
            "Could not find user matching address `{}`".format(user_addr)
        )
    e6_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_e6_key.E6KeysCommon)
    e6_client = e6_keys.get_client_by_user(user)
    return e6_client


def e6_client_from_input(user: User, sub_repo) -> YippiClient:
    e6_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_e6_key.E6KeysCommon)
    e6_client = e6_keys.get_client_by_user(user)
    return e6_client


class E621Source(hallo.modules.subscriptions.stream_source.StreamSource[Post]):
    type_name: str = "e621"
    type_names: List[str] = ["e621", "e621 search", "search e621"]

    def __init__(
            self,
            search: str,
            e6_client: YippiClient,
            last_keys: List[hallo.modules.subscriptions.stream_source.Key] = None
    ):
        super().__init__(last_keys)
        self.e6_client = e6_client
        self.search: str = search

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.search.lower().strip()

    @property
    def title(self) -> str:
        return f"search for \"{self.search}\""

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'E621Source':
        e6_client = e6_client_from_input(user, sub_repo)
        return E621Source(
            argument,
            e6_client
        )

    def current_state(self) -> List[Post]:
        return self.e6_client.posts(self.search)

    def item_to_key(self, item: Post) -> hallo.modules.subscriptions.stream_source.Key:
        return item.id

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: Post
    ) -> EventMessage:
        link = f"https://e621.net/posts/{item.id}"
        # Create rating string
        rating_dict = {Rating.EXPLICIT: "(Explicit)", Rating.QUESTIONABLE: "(Questionable)", Rating.SAFE: "(Safe)"}
        rating = rating_dict.get(item.rating, "(Unknown)")
        # Construct output
        output = f'Update on "{self.search}" e621 search. {link} {rating}'
        if item.file["ext"] in ["swf", "webm"] or item.file["url"] is None:
            return EventMessage(server, channel, user, output, inbound=False)
        image_url = item.file["url"]
        return EventMessageWithPhoto(
            server, channel, user, output, image_url, inbound=False
        )

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'E621Source':
        user_addr = json_data["e621_user_address"]
        e6_client = e6_client_from_json(user_addr, destination.server, sub_repo)
        return E621Source(
            json_data["search"],
            e6_client,
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        user_addr = None
        if self.e6_key:
            user_addr = self.e6_key.user.address
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "search": self.search,
            "e621_user_address": user_addr
        }
