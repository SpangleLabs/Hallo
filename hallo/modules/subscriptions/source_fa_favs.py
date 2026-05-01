from typing import NewType, TYPE_CHECKING

from hallo.modules.subscriptions.subscription_exception import SubscriptionException
from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.modules.subscriptions.stream_source import StreamSource, Key
from hallo.modules.subscriptions.common_fa_key import FAKey, FAKeysCommon
from hallo.server import Server

if TYPE_CHECKING:
    from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


SubmissionId = NewType("SubmissionId", int)


def fa_key_from_json(user_addr: str, server: Server, sub_repo: 'SubscriptionRepo') -> FAKey:
    user = server.get_user_by_address(user_addr)
    if user is None:
        raise SubscriptionException(f"Could not find user matching address `{user_addr}`")
    fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
    assert isinstance(fa_keys, FAKeysCommon)
    fa_key = fa_keys.get_key_by_user(user)
    if fa_key is None:
        raise SubscriptionException(f"Could not find fa key for user: {user.name}")
    return fa_key


def fa_key_from_input(user: User, sub_repo: 'SubscriptionRepo') -> FAKey:
    fa_keys = sub_repo.get_common_config_by_type(FAKeysCommon)
    assert isinstance(fa_keys, FAKeysCommon)
    fa_key = fa_keys.get_key_by_user(user)
    if fa_key is None:
        raise SubscriptionException(
            "Cannot create FA user favourites subscription without cookie details. "
            "Please set up FA cookies with "
            "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
        )
    return fa_key


class FAFavsSource(StreamSource[SubmissionId]):
    type_name: str = "fa_user_favs"
    type_names: list[str] = [
        "fa user favs",
        "furaffinity user favs",
        "furaffinity user favourites",
        "fa user favourites",
        "furaffinity user favorites",
        "fa user favorites",
    ]

    def __init__(
            self,
            fa_key: FAKey,
            username: str,
            last_keys: list[Key] | None = None
    ) -> None:
        super().__init__(last_keys)
        self.username = username
        self.fa_key = fa_key

    def item_to_key(self, item: SubmissionId) -> Key:
        return item

    async def item_to_event(
            self,
            server: Server,
            channel: Channel | None,
            user: User | None,
            item: SubmissionId
    ) -> EventMessage:
        fa_reader = self.fa_key.get_fa_reader()
        submission = fa_reader.get_submission_page(item)
        link = f"https://furaffinity.net/view/{item}"
        title = submission.title
        posted_by = submission.name
        # Construct output
        output = f'{self.username} has favourited a new image. "{title}" by {posted_by}. {link}'
        # Get submission page and file extension
        image_url = submission.full_image
        file_extension = image_url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif"]:
            output_evt = EventMessageWithPhoto(
                server, channel, user, output, image_url, inbound=False
            )
            return output_evt
        return EventMessage(server, channel, user, output, inbound=False)

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    @property
    def title(self) -> str:
        return f'Favourites subscription for "{self.username}"'

    @classmethod
    async def from_input(cls, argument: str, user: User, sub_repo: 'SubscriptionRepo') -> 'FAFavsSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FAFavsSource(fa_key, argument)

    async def current_state(self) -> list[SubmissionId]:
        fa_reader = self.fa_key.get_fa_reader()
        favs_page = fa_reader.get_user_fav_page(self.username)
        return [SubmissionId(x) for x in favs_page.submission_ids]

    @classmethod
    def from_json(cls, json_data: dict, destination: Destination, sub_repo: 'SubscriptionRepo') -> 'FAFavsSource':
        user_addr = json_data["fa_key_user_address"]
        fa_key = fa_key_from_json(user_addr, destination.server, sub_repo)
        return FAFavsSource(
            fa_key,
            json_data["username"],
            json_data["last_keys"]
        )

    def to_json(self) -> dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "fa_key_user_address": self.fa_key.user.address,
            "username": self.username
        }
