import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from xml.etree import ElementTree

import isodate

import hallo.modules.subscriptions.sub_rss
import hallo.modules.subscriptions.subscriptions
from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.hallo import Hallo
from hallo.server import Server


class TwitterSub(hallo.modules.subscriptions.sub_rss.RssSub):
    names: List[str] = ["twitter", "tweets", "twitter account"]
    type_name: str = "twitter"

    profile_regex = re.compile(
        r"^(?:(?:https://)?(?:www.)?(?:twitter.com|nitter.net)/|@)?([^/]+)(?:/?$|/?(with_replies|media)$)",
        re.IGNORECASE
    )

    def __init__(
            self,
            server: Server,
            destination: Destination,
            handle: str,
            extra: Optional[str],
            last_check: Optional[datetime] = None,
            update_frequency: Optional[timedelta] = None,
            last_item_hash: Optional[str] = None
    ):
        url = f"https://nitter.net/{handle}/rss"
        if extra is not None:
            url = f"https://nitter.net/{handle}/{extra}/rss"
        super().__init__(server, destination, url, last_check, update_frequency, handle, last_item_hash)
        self.handle = handle
        self.extra = extra

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            sub_repo
    ) -> 'TwitterSub':
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # Get user specified stuff
        split_args = input_evt.command_args.split()
        argument = split_args[0]
        match = TwitterSub.profile_regex.match(argument)
        if match is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Argument does not match pattern for twitter account"
            )
        handle = match.group(1)
        extra = match.group(2)
        feed_period = "PT600S"
        if len(split_args) > 1:
            feed_period = split_args[1]
        try:
            feed_delta = isodate.parse_duration(feed_period)
        except isodate.isoerror.ISO8601Error:
            feed_delta = isodate.parse_duration("PT10M")
        try:
            twitter_sub = TwitterSub(server, destination, handle, extra, update_frequency=feed_delta)
            twitter_sub.check()
        except Exception as e:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Failed to create twitter subscription", e
            )
        return twitter_sub

    def matches_name(self, name_clean: str) -> bool:
        handle_clean = self.handle.lower().strip()
        match = self.profile_regex.match(name_clean)
        if match is None:
            return False
        return match.group(1).lower().strip() == handle_clean and self.extra == match.group(2)

    def get_name(self) -> str:
        if self.extra is None:
            return f"@{self.handle}"
        return f"@{self.handle}/{self.extra}"

    def format_item(self, rss_item: ElementTree.Element) -> Optional[EventMessage]:
        item_link = self._get_item_link(rss_item).replace("nitter.net", "twitter.com")
        # Construct output
        output = f"Update on \"{self.get_name()}\" twitter feed. {item_link}"
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["handle"] = self.handle
        json_obj["extra"] = self.extra
        json_obj["last_item"] = self.last_item_hash
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'TwitterSub':
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
        handle = json_obj["handle"]
        extra = json_obj["extra"]
        last_hash = json_obj["last_item"]
        new_sub = TwitterSub(
            server, destination, handle, extra, last_check, update_frequency, last_hash
        )
        new_sub.last_update = last_update
        return new_sub
