from typing import List, Optional, Dict

from yippi import Post, Rating

import hallo.modules.subscriptions.subscription_exception
from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.input_parser import InputParser
import hallo.modules.subscriptions.source_e621
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.common_e6_key
from hallo.server import Server


class E621TaggingSource(hallo.modules.subscriptions.source_e621.E621Source):
    type_name = "e621_tagging"
    type_names: List[str] = ["e621 tagging", "e621 tagging search", "tagging e621"]

    def __init__(
            self,
            search: str,
            e6_client: hallo.modules.subscriptions.common_e6_key.E6ClientCommon,
            e6_key: hallo.modules.subscriptions.common_e6_key.E6Key,
            tags: List[str],
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(search, e6_client, e6_key, last_keys)
        self.tags: List[str] = tags

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'E621TaggingSource':
        parsed = InputParser(argument)
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
                raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                    'You need to specify a search term with search="search term" and '
                    'tags to watch with tags="tags to watch"'
                )
        e6_client = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_e6_key.E6ClientCommon)
        e6_key = hallo.modules.subscriptions.source_e621.e6_key_from_input(user, sub_repo)
        return E621TaggingSource(search, e6_client, e6_key, tags)

    @property
    def title(self) -> str:
        return f'search for "{self.search}" to apply tags {self.tags}'

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
        # Check tags
        post_tags = [tag for tag_list in item.tags.values() for tag in tag_list]
        tag_results = {tag: tag in post_tags for tag in self.tags}
        tag_output = [f"{tag}: {val}" for tag, val in tag_results.items()]
        # Construct output
        output = f'Update on "{self.search}" tagging e621 search. {link} {rating}.\nWatched tags: {tag_output}'
        if item.file["ext"] in ["swf", "webm"] or item.file["url"] is None:
            return EventMessage(server, channel, user, output, inbound=False)
        image_url = item.file["url"]
        return EventMessageWithPhoto(
            server, channel, user, output, image_url, inbound=False
        )

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'E621TaggingSource':
        user_addr = json_data["e621_user_address"]
        e6_key = hallo.modules.subscriptions.source_e621.e6_key_from_json(user_addr, destination.server, sub_repo)
        e6_client = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_e6_key.E6ClientCommon)
        return E621TaggingSource(
            json_data["search"],
            e6_client,
            e6_key,
            json_data["tags"],
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
            "tags": self.tags,
            "e621_user_address": user_addr
        }
