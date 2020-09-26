import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import List, Generic, TypeVar, Dict, Type, Optional, Union

import isodate

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.hallo import Hallo
from hallo.server import Server

logger = logging.getLogger(__name__)
T = TypeVar("T")
# TODO: Subscriptions inheriting from Subscription[Dict] could do with actual classes or types


def is_valid_iso8601_period(try_period: str) -> bool:
    try:
        isodate.parse_duration(try_period)
        return True
    except isodate.isoerror.ISO8601Error:
        return False


class SubscriptionException(Exception):
    pass


class Subscription(Generic[T], ABC):
    names: List[str] = []
    type_name: str = ""

    def __init__(
            self,
            server: Server,
            destination: Destination,
            last_check: datetime = None,
            update_frequency: timedelta = None
    ) -> None:
        if update_frequency is None:
            update_frequency = timedelta(minutes=5)
        self.server: Server = server
        self.destination: Destination = destination
        self.last_check: Optional[datetime] = last_check
        self.update_frequency: timedelta = update_frequency
        self.last_update: Optional[datetime] = None

    @staticmethod
    def create_from_input(
            input_evt: EventMessage, sub_repo
    ) -> 'Subscription':
        """
        Creates a new subscription object from a user's input line
        """
        raise NotImplementedError()

    def matches_name(self, name_clean: str) -> bool:
        """
        Returns whether a user input string matches this subscription object
        """
        raise NotImplementedError()

    def get_name(self) -> str:
        """
        Returns a printable name for the subscription
        """
        raise NotImplementedError()

    def check(self, *, ignore_result: bool = False) -> List[T]:
        """
        Checks the subscription, and returns a list of update objects, in whatever format that
        format_item() would like to receive them.
        The list should be ordered from oldest to newest.
        :param ignore_result: Whether the items returned will be formatted an used.
        """
        raise NotImplementedError()

    def send_item(self, item: T) -> None:
        self.last_update = datetime.now()
        output_evt = self.format_item(item)
        self.server.send(output_evt)

    def format_item(self, item: T) -> EventMessage:
        """
        Formats an item, as returned from check(), into an event that can be sent out
        """
        raise NotImplementedError()

    def needs_check(self) -> bool:
        """
        Returns whether a subscription check is overdue.
        """
        if self.last_check is None:
            return True
        if datetime.now() > self.last_check + self.update_frequency:
            return True
        return False

    def to_json(self) -> Dict:
        json_obj = dict()
        json_obj["server_name"] = self.server.name
        if isinstance(self.destination, Channel):
            json_obj["channel_address"] = self.destination.address
        if isinstance(self.destination, User):
            json_obj["user_address"] = self.destination.address
        if self.last_check is not None:
            json_obj["last_check"] = self.last_check.isoformat()
        json_obj["update_frequency"] = isodate.duration_isoformat(self.update_frequency)
        if self.last_update is not None:
            json_obj["last_update"] = self.last_update.isoformat()
        return json_obj

    @staticmethod
    def from_json(json_obj: Dict, hallo_obj: Hallo, sub_repo) -> 'Subscription':
        raise NotImplementedError()


Item = TypeVar("Item")
Key = Union[str, int]


class StreamSubWrapper(Subscription, Generic[Item]):

    def __init__(
            self,
            server: Server,
            destination: Destination,
            mini_sub: 'StreamSub[Item]',
            update_frequency: timedelta = None,
            last_check: datetime = None,
            last_keys: List[Key] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        if last_keys is None:
            last_keys = []
        self.last_keys = last_keys
        self.mini_sub = mini_sub

    @staticmethod
    def create_from_input(
            input_evt: EventMessage,
            mini_sub_class: Type['StreamSub'],
            sub_repo
    ) -> 'StreamSubWrapper':
        # TODO: can't change the signature. Think of GoogleDocsSub. We might want subscriptions which are not a feed of items, like this.
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # Get user specified stuff
        argument = input_evt.command_args.strip()
        split_args = argument.split()
        feed_delta = timedelta(minutes=10)
        if len(split_args) > 1:
            try:
                feed_delta = isodate.parse_duration(split_args[-1])
                argument = argument[:-len(split_args[-1])].strip()
            except isodate.isoerror.ISO8601Error:
                try:
                    feed_delta = isodate.parse_duration(split_args[0])
                    argument = argument[len(split_args[0]):].strip()
                except isodate.isoerror.ISO8601Error:
                    pass
        mini_sub = mini_sub_class.from_input(argument)
        try:
            twitter_sub = StreamSubWrapper(
                server,
                destination,
                mini_sub,
                update_frequency=feed_delta
            )
            twitter_sub.check()
        except Exception as e:
            raise SubscriptionException(
                f"Failed to create {mini_sub.name} subscription", e
            )
        return twitter_sub

    def matches_name(self, name_clean: str) -> bool:
        return self.mini_sub.matches_name(name_clean)

    def get_name(self) -> str:
        return self.mini_sub.name

    def check(self, *, ignore_result: bool = False) -> List[Item]:
        all_items = self.mini_sub.get_items()
        # TODO, return only new ones!
        new_items = all_items
        # TODO: we only want to mark these if format works, though
        self.last_keys = [self.mini_sub.item_to_key(item) for item in all_items]
        self.last_check = datetime.now()
        if not ignore_result:
            return new_items
        return []

    def format_item(self, item: Item) -> EventMessage:
        self.last_update = datetime.now()
        text = self.mini_sub.item_to_text(item)
        photo = self.mini_sub.item_to_photo(item)
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        if photo:
            return EventMessageWithPhoto(self.server, channel, user, text, photo, inbound=False)
        return EventMessage(self.server, channel, user, text, inbound=False)

    @staticmethod
    def from_json(
            json_data: Dict,
            hallo_obj: Hallo,
            mini_sub_class: Type['StreamSub'],
            sub_repo
    ) -> 'Subscription':
        server = hallo_obj.get_server_by_name(json_data["server_name"])
        if server is None:
            raise SubscriptionException(
                'Could not find server with name "{}"'.format(json_data["server_name"])
            )
        # Load channel or user
        if "channel_address" in json_data:
            destination = server.get_channel_by_address(json_data["channel_address"])
        else:
            if "user_address" in json_data:
                destination = server.get_user_by_address(json_data["user_address"])
            else:
                raise SubscriptionException(
                    "Channel or user must be defined."
                )
        if destination is None:
            raise SubscriptionException("Could not find chanel or user.")
        # Load last check
        last_check = None
        if "last_check" in json_data:
            last_check = datetime.strptime(
                json_data["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_data["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_data:
            last_update = datetime.strptime(
                json_data["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load last keys
        last_keys = []
        for last_key in json_data["last_keys"]:
            last_keys.append(last_key)
        # StreamSub loading
        mini_sub = mini_sub_class.from_json(json_data)
        new_sub = StreamSubWrapper(
            server,
            destination,
            mini_sub,
            update_frequency=update_frequency,
            last_check=last_check,
            last_keys=last_keys
        )
        new_sub.last_update = last_update
        return new_sub

    def to_json(self) -> Dict:
        json_data = super().to_json()
        json_data["last_keys"] = []
        for latest_id in self.last_keys:
            json_data["last_keys"].append(latest_id)
        json_data["type"] = self.mini_sub.type_name
        return self.mini_sub.to_json(json_data)


class StreamSub(ABC, Generic[Item]):
    type_name: str

    def get_items(self) -> List[Item]:
        pass  # TODO

    def item_to_key(self, item: Item) -> Key:
        pass  # TODO

    def item_to_text(self, item: Item) -> str:
        pass  # TODO

    def item_to_photo(self, item: Item) -> Optional[str]:
        pass  # TODO

    def matches_name(self, name_clean: str) -> bool:
        pass  # TODO

    @property
    def name(self) -> str:
        pass  # TODO

    @classmethod
    def from_input(cls, argument: str) -> 'StreamSub':
        pass  # TODO

    @classmethod
    def from_json(cls, json_data: Dict) -> 'StreamSub':
        pass

    def to_json(self, json_data: Dict) -> Dict:
        pass


class GoogleDocsSub(Subscription):
    pass


class YoutubeSub(Subscription):
    # https://webapps.stackexchange.com/questions/111680/how-to-find-channel-rss-feed-on-youtube
    pass


class ImgurSub(Subscription):
    pass
