from typing import Optional, List, Dict

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage
import hallo.modules.subscriptions.source_fa_favs
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.common_fa_key
from hallo.server import Server


class FAFavNotificationsSource(
    hallo.modules.subscriptions.stream_source.StreamSource[
        hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationFavourite
    ]
):
    type_name: str = "fa_notif_favs"
    type_names: List[str] = [
        "fa favs notifications",
        "fa favs",
        "furaffinity favs",
        "fa favourites notifications",
        "fa favourites",
        "furaffinity favourites",
    ]

    def __init__(
            self,
            fa_key: hallo.modules.subscriptions.common_fa_key.FAKey,
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[
        hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationFavourite
    ]:
        fa_reader = self.fa_key.get_fa_reader()
        notif_page = fa_reader.get_notification_page()
        return notif_page.favourites

    def item_to_key(
            self,
            item: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationFavourite
    ) -> hallo.modules.subscriptions.stream_source.Key:
        return item.fav_id

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationFavourite
    ) -> EventMessage:
        return EventMessage(
            server, channel, user,
            f"You have a new favourite notification, {item.name} ( http://furaffinity.net/user/{item.username}/ ) "
            f'has favourited your submission "{item.submission_name}" {item.submission_link}'
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["favs"]]

    @property
    def title(self) -> str:
        return f"FA favourite notifications for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAFavNotificationsSource':
        fa_key = hallo.modules.subscriptions.source_fa_favs.fa_key_from_input(user, sub_repo)
        return FAFavNotificationsSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAFavNotificationsSource':
        fa_key = hallo.modules.subscriptions.source_fa_favs.fa_key_from_json(
            json_data["fa_key_user_address"], destination.server, sub_repo
        )
        return FAFavNotificationsSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }
