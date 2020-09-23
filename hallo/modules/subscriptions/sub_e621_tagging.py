from datetime import datetime, timedelta
from typing import List, Optional, Dict

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.hallo import Hallo
from hallo.inc.input_parser import InputParser
import hallo.modules.subscriptions.sub_e621
import hallo.modules.subscriptions.subscription_repo
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class E621TaggingSub(hallo.modules.subscriptions.sub_e621.E621Sub):
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
    def create_from_input(
            input_evt: EventMessage, sub_repo: hallo.modules.subscriptions.subscription_repo.SubscriptionRepo
    ) -> 'E621TaggingSub':
        """
        :type input_evt: Events.EventMessage
        :type sub_repo: hallo.modules.subscriptions.subscription_repo.SubscriptionRepo
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
                lambda x, y: hallo.modules.subscriptions.subscriptions.is_valid_iso8601_period(x)
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
                raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
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
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
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
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo: hallo.modules.subscriptions.subscription_repo.SubscriptionRepo
    ) -> 'E621TaggingSub':
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
