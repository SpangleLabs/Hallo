import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.hallo import Hallo
from hallo.inc.commons import Commons
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class E621Sub(hallo.modules.subscriptions.subscriptions.Subscription[Dict]):
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
    def create_from_input(
            input_evt: EventMessage, sub_repo
    ) -> 'E621Sub':
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
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
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
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'E621Sub':
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
        new_sub = E621Sub(
            server, destination, search, last_check, update_frequency, latest_ids
        )
        new_sub.last_update = last_update
        return new_sub
