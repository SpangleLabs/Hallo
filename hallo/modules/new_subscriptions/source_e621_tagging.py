from typing import List, Optional, Dict

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.input_parser import InputParser
from hallo.modules.new_subscriptions.source_e621 import E621Source
from hallo.modules.new_subscriptions.stream_source import Key
from hallo.modules.new_subscriptions.subscription import SubscriptionException
from hallo.server import Server


class E621TaggingSource(E621Source):
    def __init__(self, search: str, tags: List[str], last_keys: Optional[List[Key]] = None):
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
                raise SubscriptionException(
                    'You need to specify a search term with search="search term" and '
                    'tags to watch with tags="tags to watch"'
                )
        return E621TaggingSource(search, tags)

    @property
    def title(self) -> str:
        return 'search for "{}" to apply tags {}'.format(self.search, self.tags)

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
        # Check tags
        post_tags = [tag for tag_list in item["tags"].values() for tag in tag_list]
        tag_results = {tag: tag in post_tags for tag in self.tags}
        tag_output = ["{}: {}".format(tag, val) for tag, val in tag_results.items()]
        # Construct output
        output = 'Update on "{}" tagging e621 search. {} {}.\nWatched tags: {}'.format(
            self.search, link, rating, tag_output
        )
        if item["file"]["ext"] in ["swf", "webm"] or item["file"]["url"]:
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
