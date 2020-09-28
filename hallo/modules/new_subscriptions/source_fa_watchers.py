from typing import Dict, Optional, List

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage
from hallo.modules.new_subscriptions.source_fa_favs import fa_key_from_input, fa_key_from_json
from hallo.modules.new_subscriptions.stream_source import StreamSource, Key
from hallo.modules.new_subscriptions.common_fa_key import FAKey
from hallo.modules.new_subscriptions.subscription import SubscriptionException
from hallo.server import Server


class FAUserWatchersSource(StreamSource[FAKey.FAReader.FAWatch]):
    names: List[str] = [
        "fa user watchers",
        "fa user new watchers",
        "furaffinity user watchers",
        "furaffinity user new watchers",
    ]
    type_name: str = "fa_user_watchers"

    def __init__(self, fa_key: FAKey, username: str, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.fa_key = fa_key
        self.username = username

    def current_state(self) -> List[FAKey.FAReader.FAWatch]:
        fa_reader = self.fa_key.get_fa_reader()
        user_page = fa_reader.get_user_page(self.username)
        return user_page.watched_by

    def item_to_key(self, item: FAKey.FAReader.FAWatch) -> Key:
        return item.watcher_username

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: FAKey.FAReader.FAWatch
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
        fa_key = fa_key_from_input(user, sub_repo)
        # Check if it's a valid user
        try:
            fa_key.get_fa_reader().get_user_page(argument)
        except Exception:
            raise SubscriptionException(
                "This does not appear to be a valid username."
            )
        return FAUserWatchersSource(fa_key, argument)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAUserWatchersSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
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

    def __init__(self, fa_key: FAKey, last_keys: Optional[List[Key]] = None):
        username = fa_key.get_fa_reader().get_notification_page().username
        super().__init__(fa_key, username, last_keys)

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["watchers"]]

    @property
    def title(self) -> str:
        return f"New watchers notifications for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAWatchersSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FAWatchersSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAWatchersSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FAWatchersSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys
        }
