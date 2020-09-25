import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import List, Generic, TypeVar, Dict

import isodate

from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage
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
            update_frequency = isodate.parse_duration("PT5M")
        self.server = server
        """ :type : Server.Server"""
        self.destination = destination
        """ :type : Destination.Destination"""
        self.last_check = last_check
        """ :type : datetime"""
        self.update_frequency = update_frequency
        """ :type : timedelta"""
        self.last_update = None
        """ :type : datetime | None"""

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

    def get_name(self) -> None:
        """
        Returns a printable name for the subscription
        :rtype: str
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


class GoogleDocsSub(Subscription):
    pass


class YoutubeSub(Subscription):
    # https://webapps.stackexchange.com/questions/111680/how-to-find-channel-rss-feed-on-youtube
    pass


class ImgurSub(Subscription):
    pass
