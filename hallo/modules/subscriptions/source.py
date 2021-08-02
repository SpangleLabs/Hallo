from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Dict, TypeVar

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage
from hallo.hallo import Hallo
from hallo.server import Server

State = TypeVar("State")
Update = TypeVar("Update")


class Source(ABC, Generic[State, Update]):
    type_name: str = None
    type_names: List[str] = None

    def __init__(self):
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
    def from_input(cls, argument: str, user: User, sub_repo) -> 'Source':
        pass

    @abstractmethod
    def current_state(self) -> State:
        pass

    @abstractmethod
    def state_change(self, state: State) -> Optional[Update]:
        pass

    @abstractmethod
    def save_state(self, state: State) -> None:
        pass

    @abstractmethod
    def events(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            update: Update
    ) -> List[EventMessage]:
        """
        Creates a list of events to represent a given update. This should have the oldest update first.
        """
        pass

    def passive_run(self, event: EventMessage, hallo_obj: Hallo) -> bool:
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'Source':
        pass

    @abstractmethod
    def to_json(self) -> Dict:
        pass
