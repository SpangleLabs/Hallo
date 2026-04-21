from abc import abstractmethod
from typing import TypeVar, Generic

from hallo.destination import Channel, User
from hallo.events import EventMessage
from hallo.modules.subscriptions.source import Source
from hallo.server import Server

Item = TypeVar("Item")
Key = str | int


class StreamSource(Source[list[Item], list[Item]], Generic[Item]):
    def __init__(self, last_keys: list[Key] | None) -> None:
        super().__init__()
        self.last_keys: list[Key] = last_keys or []

    @abstractmethod
    def current_state(self) -> list[Item]:
        pass

    def state_change(self, state: list[Item]) -> list[Item]:
        # If no last keys, All state is update
        if not self.last_keys:
            return state
        # Otherwise, get all the items before the last of the previously-seen keys.
        new_items = []
        batch = []
        for item in state:
            key = self.item_to_key(item)
            if key in self.last_keys:
                new_items += batch
                batch = []
            else:
                batch.append(item)
        # If everything is in batch, that means it was all new items, previous keys weren't seen
        if batch and not new_items:
            new_items += batch
        return new_items

    def save_state(self, state: list[Item]) -> None:
        self.last_keys = [self.item_to_key(item) for item in state]

    def events(
            self,
            server: Server,
            channel: Channel | None,
            user: User | None,
            update: list[Item]
    ) -> list[EventMessage]:
        return [self.item_to_event(server, channel, user, item) for item in update[::-1]]

    @abstractmethod
    def item_to_key(self, item: Item) -> Key:
        pass

    @abstractmethod
    def item_to_event(
            self,
            server: Server,
            channel: Channel | None,
            user: User | None,
            item: Item
    ) -> EventMessage:
        pass
