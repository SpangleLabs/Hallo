from typing import Dict, Optional, List

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage
import hallo.modules.subscriptions.source_fa_favs
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscription
from hallo.server import Server


class FAUserWatchersSource(
    hallo.modules.subscriptions.stream_source.StreamSource[
        hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch
    ]
):
    names: List[str] = [
        "fa user watchers",
        "fa user new watchers",
        "furaffinity user watchers",
        "furaffinity user new watchers",
    ]
    type_name: str = "fa_user_watchers"

    def __init__(self, fa_key: hallo.modules.subscriptions.common_fa_key.FAKey, username: str,
                 last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None):
        super().__init__(last_keys)
        self.fa_key = fa_key
        self.username = username

    def current_state(self) -> List[hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch]:
        fa_reader = self.fa_key.get_fa_reader()
        user_page = fa_reader.get_user_page(self.username)
        return user_page.watched_by

    def item_to_key(
            self,
            item: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch
    ) -> hallo.modules.subscriptions.stream_source.Key:
        return item.watcher_username

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch
    ) -> EventMessage:
        link = "https://furaffinity.net/user/{}/".format(item.watcher_username)
        return EventMessage(
            server, channel, user,
            f"{item.watcher_name} has watched {item.watched_name}. Link: {link}"
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    @property
    def title(self) -> str:
        return f'New watchers subscription for "{self.username}"'

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAUserWatchersSource':
        fa_key = hallo.modules.subscriptions.source_fa_favs.fa_key_from_input(user, sub_repo)
        # Check if it's a valid user
        try:
            fa_key.get_fa_reader().get_user_page(argument)
        except Exception:
            raise hallo.modules.subscriptions.subscription.SubscriptionException(
                "This does not appear to be a valid username."
            )
        return FAUserWatchersSource(fa_key, argument)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAUserWatchersSource':
        fa_key = hallo.modules.subscriptions.source_fa_favs.fa_key_from_json(
            json_data["fa_key_user_address"],
            destination.server, sub_repo
        )
        return FAUserWatchersSource(
            fa_key,
            json_data["username"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "username": self.username,
            "last_keys": self.last_keys
        }


class FAWatchersSource(FAUserWatchersSource):
    names: List[str] = [
        "{}{}{}{}".format(fa, new, watchers, notifications)
        for fa in ["fa ", "furaffinity "]
        for new in ["new ", ""]
        for watchers in ["watcher", "watchers"]
        for notifications in ["", " notifications"]
    ]
    type_name: str = "fa_notif_watchers"

    def __init__(
            self,
            fa_key: hallo.modules.subscriptions.common_fa_key.FAKey,
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        username = fa_key.get_fa_reader().get_notification_page().username
        super().__init__(fa_key, username, last_keys)

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["watchers"]]

    @property
    def title(self) -> str:
        return f"New watchers notifications for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAWatchersSource':
        fa_key = hallo.modules.subscriptions.source_fa_favs.fa_key_from_input(user, sub_repo)
        return FAWatchersSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAWatchersSource':
        fa_key = hallo.modules.subscriptions.source_fa_favs.fa_key_from_json(
            json_data["fa_key_user_address"],
            destination.server, sub_repo
        )
        return FAWatchersSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }
