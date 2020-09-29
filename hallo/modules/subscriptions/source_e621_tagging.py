from typing import List, Optional, Dict

import hallo.modules.subscriptions.subscription_exception
from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.input_parser import InputParser
import hallo.modules.subscriptions.source_e621
import hallo.modules.subscriptions.stream_source
from hallo.server import Server


class E621TaggingSource(hallo.modules.subscriptions.source_e621.E621Source):
    type_name = "e621_tagging"
    type_names: List[str] = ["e621 tagging", "e621 tagging search", "tagging e621"]

    def __init__(
            self,
            search: str,
            tags: List[str],
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(search, last_keys)
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
        return E621TaggingSource(search, tags)

    @property
    def title(self) -> str:
        return f'search for "{self.search}" to apply tags {self.tags}'

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: Dict
    ) -> EventMessage:
        link = f"https://e621.net/posts/{item['id']}"
        # Create rating string
        rating_dict = {"e": "(Explicit)", "q": "(Questionable)", "s": "(Safe)"}
        rating = rating_dict.get(item["rating"], "(Unknown)")
        # Check tags
        post_tags = [tag for tag_list in item["tags"].values() for tag in tag_list]
        tag_results = {tag: tag in post_tags for tag in self.tags}
        tag_output = [f"{tag}: {val}" for tag, val in tag_results.items()]
        # Construct output
        output = f'Update on "{self.search}" tagging e621 search. {link} {rating}.\nWatched tags: {tag_output}'
        if item["file"]["ext"] in ["swf", "webm"] or item["file"]["url"] is None:
            return EventMessage(server, channel, user, output, inbound=False)
        image_url = item["file"]["url"]
        return EventMessageWithPhoto(
            server, channel, user, output, image_url, inbound=False
        )

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'E621TaggingSource':
        return E621TaggingSource(
            json_data["search"],
            json_data["tags"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "search": self.search,
            "tags": self.tags
        }
