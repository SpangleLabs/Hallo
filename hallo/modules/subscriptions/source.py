from abc import ABC, abstractmethod
from typing import Generic, TypeVar, TYPE_CHECKING

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage
from hallo.hallo import Hallo
from hallo.server import Server

if TYPE_CHECKING:
    from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


State = TypeVar("State")
Update = TypeVar("Update")


class Source(ABC, Generic[State, Update]):
    type_name: str = None
    type_names: list[str] = None

    def __init__(self) -> None:
        pass

    @abstractmethod
    def matches_name(self, name_clean: str) -> bool:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_input(cls, argument: str, user: User, sub_repo: 'SubscriptionRepo') -> 'Source':
        pass

    @abstractmethod
    async def current_state(self) -> State:
        pass

    @abstractmethod
    def state_change(self, state: State) -> Update | None:
        pass

    @abstractmethod
    def save_state(self, state: State) -> None:
        pass

    @abstractmethod
    def events(
            self,
            server: Server,
            channel: Channel | None,
            user: User | None,
            update: Update
    ) -> list[EventMessage]:
        """
        Creates a list of events to represent a given update. This should have the oldest update first.
        """
        pass

    async def passive_run(self, event: EventMessage, hallo_obj: Hallo) -> bool:
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, json_data: dict, destination: Destination, sub_repo: 'SubscriptionRepo') -> 'Source':
        pass

    @abstractmethod
    def to_json(self) -> dict:
        pass
