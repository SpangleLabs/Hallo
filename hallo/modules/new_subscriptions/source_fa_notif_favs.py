from typing import Optional, List, Dict

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage
from hallo.modules.new_subscriptions.source_fa_favs import fa_key_from_input, fa_key_from_json
from hallo.modules.new_subscriptions.stream_source import StreamSource, Key, Item
from hallo.modules.new_subscriptions.common_fa_key import FAKey
from hallo.server import Server


class FAFavNotificationsSource(StreamSource[FAKey.FAReader.FANotificationFavourite]):
    names: List[str] = [
        "fa favs notifications",
        "fa favs",
        "furaffinity favs",
        "fa favourites notifications",
        "fa favourites",
        "furaffinity favourites",
    ]
    type_name: str = "fa_notif_favs"

    def __init__(self, fa_key: FAKey, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[FAKey.FAReader.FANotificationFavourite]:
        fa_reader = self.fa_key.get_fa_reader()
        notif_page = fa_reader.get_notification_page()
        return notif_page.favourites

    def item_to_key(self, item: FAKey.FAReader.FANotificationFavourite) -> Key:
        return item.fav_id

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: FAKey.FAReader.FANotificationFavourite
    ) -> EventMessage:
        return EventMessage(
            server, channel, user,
            f"You have a new favourite notification, {item.name} ( http://furaffinity.net/user/{item.username}/ ) "
            f'has favourited your submission "{item.submission_name}" {item.submission_link}'
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["favs"]]

    @property
    def title(self) -> str:
        return f"FA favourite notifications for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAFavNotificationsSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FAFavNotificationsSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAFavNotificationsSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FAFavNotificationsSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }
