import json
import os
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import TypeVar, Generic, Dict, List, Optional, Type, TYPE_CHECKING

from hallo.events import message_from_json

if TYPE_CHECKING:
    from hallo.events import EventMessage, EventMenuCallback
    from hallo.hallo import Hallo

T = TypeVar("T", bound='Menu')


class MenuException(Exception):
    pass


class MenuParseException(MenuException):
    pass


class MenuFactory(Generic[T]):

    def __init__(self, classes: List[Type[T]], hallo_obj: 'Hallo'):
        self.menu_classes = classes
        self.hallo = hallo_obj

    def load_menu_from_json(self, data: Dict) -> T:
        menu_class = next(filter(lambda m: m.type == data["menu_type"], self.menu_classes), None)
        if menu_class is None:
            raise MenuParseException(f"Unrecognised menu type: {data['menu_type']}")
        menu_msg = message_from_json(self.hallo, data["menu_msg"])
        return menu_class.from_json(self.hallo, menu_msg, data["menu_data"])


class MenuCache(Generic[T]):

    def __init__(self, filename: str):
        self.menus = defaultdict(lambda: defaultdict(lambda: []))
        self.filename = filename

    def count_menus(self) -> int:
        return sum(
            len(dest_menus)
            for server_menus in self.menus.values()
            for dest_menus in server_menus.values()
        )

    def add_menu(self, menu: T) -> None:
        # If the menu already exists, remove it.
        if menu.msg.message_id is not None:
            if self.get_menu_by_menu(menu):
                self.remove_menu(menu)
        # If the menu message has no keyboard, don't add it
        if not menu.msg.has_keyboard:
            return
        self.menus[menu.msg.server_name][menu.msg.destination_addr].append(menu)
        self.save_to_json()

    def get_menu_by_menu(self, menu: T) -> Optional[T]:
        return self.get_menu_by_id(menu.msg.server_name, menu.msg.destination_addr, menu.msg.message_id)

    def get_menu_by_event(self, msg: 'EventMessage') -> Optional[T]:
        return self.get_menu_by_id(msg.server_name, msg.destination_addr, msg.message_id)

    def get_menu_by_callback_event(self, event: 'EventMenuCallback') -> Optional[T]:
        return self.get_menu_by_id(event.server.name, event.destination.address, event.message_id)

    def get_menu_by_id(self, server_name: str, destination_addr: str, message_id: int) -> Optional[T]:
        if message_id is None:
            return None
        dest_menus = self.menus.get(server_name, {}).get(destination_addr, [])
        return next(filter(lambda m: m.msg.message_id == message_id, dest_menus), None)

    def remove_menu(self, menu: T) -> None:
        self.remove_menu_by_id(menu.msg.server_name, menu.msg.destination_addr, menu.msg.message_id)

    def remove_menu_by_event(self, msg: 'EventMessage') -> None:
        self.remove_menu_by_id(msg.server_name, msg.destination_addr, msg.message_id)

    def remove_menu_by_id(self, server_name: str, destination_addr: str, message_id: int) -> None:
        dest_menus = self.menus.get(server_name, {}).get(destination_addr, [])
        new_menus = list(filter(lambda m: m.msg.message_id != message_id, dest_menus))
        self.menus[server_name][destination_addr] = new_menus
        self.save_to_json()

    def save_to_json(self) -> None:
        data = {"servers": {}}
        for server_name, server_data in self.menus.items():
            data["servers"][server_name] = {}
            for chat_address, menu_list in server_data.items():
                data["servers"][server_name][chat_address] = {}
                data["servers"][server_name][chat_address]["menus"] = []
                for menu in menu_list:
                    data["servers"][server_name][chat_address]["menus"].append(menu.to_full_json())
        # Create parent directories
        os.makedirs(Path(self.filename).parent, exist_ok=True)
        # Save file
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, filename: str, menu_factory: MenuFactory[T]) -> 'MenuCache[T]':
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return cls(filename)
        cache = cls(filename)
        for server_name, server_data in data["servers"].items():
            for chat_addr, chat_data in server_data.items():
                for menu_data in chat_data["menus"]:
                    menu = menu_factory.load_menu_from_json(menu_data)
                    if menu.msg.message_id:
                        cache.add_menu(menu)
        return cache


class Menu(ABC):

    def __init__(self, msg: 'EventMessage'):
        self.msg: 'EventMessage' = msg

    @property
    def type(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_json(cls, hallo_obj: 'Hallo', msg: 'EventMessage', data: Dict) -> 'Menu':
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> Dict:
        raise NotImplementedError

    def to_full_json(self) -> Dict:
        return {
            "menu_type": self.type,
            "menu_msg": self.msg.to_json(),
            "menu_data": self.to_json()
        }

    @abstractmethod
    def handle_callback(self, event: 'EventMenuCallback') -> None:
        raise NotImplementedError
