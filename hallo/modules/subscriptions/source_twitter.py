import re
from typing import Optional, List, Dict
from xml.etree import ElementTree

import hallo.modules.subscriptions.subscription_exception
from hallo.destination import User, Channel, Destination
from hallo.events import EventMessage
import hallo.modules.subscriptions.source_rss
import hallo.modules.subscriptions.stream_source
from hallo.server import Server


class TwitterSource(hallo.modules.subscriptions.source_rss.RssSource):
    type_name: str = "twitter"
    type_names: List[str] = ["twitter", "tweets", "twitter account"]

    profile_regex = re.compile(
        r"^(?:(?:https://)?(?:www.)?(?:twitter.com|nitter.net)/|@)?([^/]+)(?:/?$|/?(with_replies|media)$)",
        re.IGNORECASE
    )

    def __init__(
            self,
            handle: str,
            extra: Optional[str],
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        url = f"https://nitter.net/{handle}/rss"
        if extra is not None:
            url = f"https://nitter.net/{handle}/{extra}/rss"
        super().__init__(url, last_keys=last_keys)
        self.handle = handle
        self.extra = extra

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'TwitterSource':
        match = TwitterSource.profile_regex.match(argument)
        if match is None:
            raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                "Argument does not match pattern for twitter account"
            )
        handle = match.group(1)
        extra = match.group(2)
        return TwitterSource(handle, extra)

    def matches_name(self, name_clean: str) -> bool:
        handle_clean = self.handle.lower().strip()
        match = self.profile_regex.match(name_clean)
        if match is None:
            return False
        return match.group(1).lower().strip() == handle_clean and self.extra == match.group(2)

    @property
    def title(self) -> str:
        if self.extra is None:
            return f"@{self.handle}"
        return f"@{self.handle}/{self.extra}"

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: ElementTree.Element
    ) -> EventMessage:
        item_link = hallo.modules.subscriptions.source_rss.get_rss_item_link(item).replace(
            "nitter.net", "twitter.com"
        )
        # Construct output
        output = f"Update on \"{self.title}\" twitter feed. {item_link}"
        return EventMessage(server, channel, user, output, inbound=False)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'TwitterSource':
        return TwitterSource(
            json_data["handle"],
            json_data["extra"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "handle": self.handle,
            "extra": self.extra,
            "last_keys": self.last_keys
        }
