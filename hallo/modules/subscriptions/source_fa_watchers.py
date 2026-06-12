from typing import TYPE_CHECKING

from hallo.inc.commons import Commons
from hallo.modules.subscriptions.subscription_exception import SubscriptionException
from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage
from hallo.modules.subscriptions.source_fa_favs import fa_key_from_input, fa_key_from_json
from hallo.modules.subscriptions.stream_source import StreamSource, Key
from hallo.modules.subscriptions.common_fa_key import FAKey
from hallo.server import Server

if TYPE_CHECKING:
    from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


class FAUserWatchersSource(StreamSource[FAKey.FAReader.FAWatch]):
    type_name: str = "fa_user_watchers"
    type_names: list[str] = [
        "fa user watchers",
        "fa user new watchers",
        "furaffinity user watchers",
        "furaffinity user new watchers",
    ]

    def __init__(self, fa_key: FAKey, username: str, last_keys: list[Key] | None = None) -> None:
        super().__init__(last_keys)
        self.fa_key = fa_key
        self.username = username

    async def current_state(self) -> list[FAKey.FAReader.FAWatch]:
        fa_reader = self.fa_key.get_fa_reader()
        user_page = await fa_reader.get_user_page(self.username)
        return user_page.watched_by

    def item_to_key(self, item: FAKey.FAReader.FAWatch) -> Key:
        return item.watcher_username

    async def item_to_event(
            self, server: Server, channel: Channel | None, user: User | None,
            item: FAKey.FAReader.FAWatch
    ) -> EventMessage:
        link = f"https://furaffinity.net/user/{item.watcher_username}/"
        return EventMessage(
            server, channel, user,
            f"{item.watcher_name} has watched {item.watched_name}. Link: {link}",
            inbound=False
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    @property
    def title(self) -> str:
        return f'New watchers subscription for "{self.username}"'

    @classmethod
    async def from_input(cls, argument: str, user: User, sub_repo: 'SubscriptionRepo') -> 'FAUserWatchersSource':
        fa_key = fa_key_from_input(user, sub_repo)
        # Check if it's a valid user
        try:
            await fa_key.get_fa_reader().get_user_page(argument)
        except Exception:
            raise SubscriptionException("This does not appear to be a valid username.")
        return FAUserWatchersSource(fa_key, argument)

    @classmethod
    def from_json(
            cls, json_data: dict, destination: Destination, sub_repo: 'SubscriptionRepo'
    ) -> 'FAUserWatchersSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FAUserWatchersSource(
            fa_key,
            json_data["username"],
            json_data["last_keys"]
        )

    def to_json(self) -> dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "username": self.username,
            "last_keys": self.last_keys
        }


class FAWatchersSource(FAUserWatchersSource):
    type_name: str = "fa_notif_watchers"
    type_names: list[str] = [
        f"{fa}{new}{watchers}{notifications}"
        for fa in ["fa ", "furaffinity "]
        for new in ["new ", ""]
        for watchers in ["watcher", "watchers"]
        for notifications in ["", " notifications"]
    ]

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["watchers"]]

    @property
    def title(self) -> str:
        return f"New watchers notifications for {self.fa_key.user.name}"

    @classmethod
    async def from_input(cls, argument: str, user: User, sub_repo: 'SubscriptionRepo') -> 'FAWatchersSource':
        fa_key = fa_key_from_input(user, sub_repo)
        fa_reader = fa_key.get_fa_reader()
        notifications_page = await fa_reader.get_notification_page()
        username = notifications_page.username
        return FAWatchersSource(fa_key, username)

    @classmethod
    def from_json(cls, json_data: dict, destination: Destination, sub_repo: 'SubscriptionRepo') -> 'FAWatchersSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FAWatchersSource(fa_key, json_data["username"], json_data["last_keys"])

    def to_json(self) -> dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "username": self.username,
            "last_keys": self.last_keys
        }
