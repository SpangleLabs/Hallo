from typing import TYPE_CHECKING, TypedDict

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.modules.subscriptions.source_fa_favs import fa_key_from_input, fa_key_from_json
from hallo.modules.subscriptions.stream_source import StreamSource, Key
from hallo.modules.subscriptions.common_fa_key import FAKey
from hallo.modules.subscriptions.source import Source
from hallo.server import Server

if TYPE_CHECKING:
    from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


class FANotesInboxSource(StreamSource[FAKey.FAReader.FANote]):
    type_name = "fa_notes_inbox"
    type_names = ["fa notes inbox"]

    def __init__(self, fa_key: FAKey, last_keys: list[Key] | None = None) -> None:
        super().__init__(last_keys)
        self.fa_key = fa_key

    async def current_state(self) -> list[FAKey.FAReader.FANote]:
        fa_reader = self.fa_key.get_fa_reader()
        return fa_reader.get_notes_page(FAKey.FAReader.NOTES_INBOX).notes

    def item_to_key(self, item: FAKey.FAReader.FANote) -> Key:
        return item.note_id

    def item_to_event(
            self,
            server: Server,
            channel: Channel | None,
            user: User | None,
            item: FAKey.FAReader.FANote
    ) -> EventMessage:
        return EventMessage(
            server,
            channel,
            user,
            f"You have a new note. Subject: {item.subject}, From: {item.name}, "
            f"Link: https://www.furaffinity.net/viewmessage/{item.note_id}/"
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["inbox notes"]]

    @property
    def title(self) -> str:
        return "inbox notes"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo: 'SubscriptionRepo') -> 'FANotesInboxSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FANotesInboxSource(fa_key)

    @classmethod
    def from_json(cls, json_data: dict, destination: Destination, sub_repo: 'SubscriptionRepo') -> 'FANotesInboxSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FANotesInboxSource(fa_key, json_data["last_keys"])

    def to_json(self) -> dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FANotesOutboxSource(StreamSource[FAKey.FAReader.FANote]):
    type_name = "fa_notes_outbox"
    type_names = ["fa notes outbox"]

    def __init__(self, fa_key: FAKey, last_keys: list[Key] | None = None) -> None:
        super().__init__(last_keys)
        self.fa_key = fa_key

    async def current_state(self) -> list[FAKey.FAReader.FANote]:
        fa_reader = self.fa_key.get_fa_reader()
        return [
            note for note in
            fa_reader.get_notes_page(FAKey.FAReader.NOTES_OUTBOX).notes
            if note.is_read
        ]

    def item_to_key(self, item: FAKey.FAReader.FANote) -> Key:
        return item.note_id

    def item_to_event(
            self,
            server: Server,
            channel: Channel | None,
            user: User | None,
            item: FAKey.FAReader.FANote
    ) -> EventMessage:
        return EventMessage(
            server, channel, user,
            f"An outbox note has been read. Subject: {item.subject}, To: {item.name}"
        )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["outbox notes"]]

    @property
    def title(self) -> str:
        return "outbox notes"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FANotesOutboxSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FANotesOutboxSource(fa_key)

    @classmethod
    def from_json(
            cls,
            json_data: dict,
            destination: Destination,
            sub_repo: 'SubscriptionRepo',
    ) -> 'FANotesOutboxSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FANotesOutboxSource(fa_key, json_data["last_keys"])

    def to_json(self) -> dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FANotesState(TypedDict):
    inbox: list[FAKey.FAReader.FANote]
    outbox: list[FAKey.FAReader.FANote]


class FANotesUpdate(TypedDict):
    inbox: list[FAKey.FAReader.FANote]
    outbox: list[FAKey.FAReader.FANote]


class FANotesSource(Source[FANotesState, FANotesUpdate]):
    type_name: str = "fa_notif_notes"
    type_names: list[str] = ["fa notes notifications", "fa notes", "furaffinity notes"]

    def __init__(self, fa_key: FAKey, inbox_source: FANotesInboxSource, outbox_source: FANotesOutboxSource) -> None:
        super().__init__()
        self.fa_key = fa_key
        self.inbox_source = inbox_source
        self.outbox_source = outbox_source

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["notes"]]

    @property
    def title(self) -> str:
        return f"FA notes for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo: 'SubscriptionRepo') -> 'FANotesSource':
        fa_key = fa_key_from_input(user, sub_repo)
        inbox_source = FANotesInboxSource(fa_key)
        outbox_source = FANotesOutboxSource(fa_key)
        return FANotesSource(fa_key, inbox_source, outbox_source)

    async def current_state(self) -> FANotesState:
        return FANotesState(
            inbox=self.inbox_source.current_state(),
            outbox=self.outbox_source.current_state(),
        )

    def state_change(self, state: FANotesState) -> FANotesUpdate | None:
        inbox_change = self.inbox_source.state_change(state["inbox"])
        outbox_change = self.outbox_source.state_change(state["outbox"])
        if not inbox_change and not outbox_change:
            return None
        return FANotesUpdate(
            inbox=inbox_change,
            outbox=outbox_change,
        )

    def save_state(self, state: FANotesState) -> None:
        self.inbox_source.save_state(state["inbox"])
        self.outbox_source.save_state(state["outbox"])

    def events(
            self, server: Server, channel: Channel | None, user: User | None, update: FANotesUpdate
    ) -> list[EventMessage]:
        return (
                self.inbox_source.events(server, channel, user, update["inbox"])
                + self.outbox_source.events(server, channel, user, update["outbox"])
        )

    @classmethod
    def from_json(cls, json_data: dict, destination: Destination, sub_repo: 'SubscriptionRepo') -> 'FANotesSource':
        # Load fa_key
        user_addr = json_data["fa_key_user_address"]
        fa_key = fa_key_from_json(user_addr, destination.server, sub_repo)
        inbox_source = FANotesInboxSource.from_json(json_data["inbox"], destination, sub_repo)
        outbox_source = FANotesOutboxSource.from_json(json_data["outbox"], destination, sub_repo)
        return FANotesSource(fa_key, inbox_source, outbox_source)

    def to_json(self) -> dict:
        json_data = {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "inbox": self.inbox_source.to_json(),
            "outbox": self.outbox_source.to_json()
        }
        return json_data
