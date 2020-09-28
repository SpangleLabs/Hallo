from datetime import timedelta, datetime
from typing import Dict, Optional, Type

import dateutil.parser
import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.hallo import Hallo
import hallo.modules.subscriptions.source
import hallo.modules.subscriptions.subscription_factory
import hallo.modules.subscriptions.subscription_exception
from hallo.server import Server


class Subscription:
    def __init__(
            self,
            server: Server,
            destination: Destination,
            source: 'hallo.modules.new_subscriptions.source.Source',
            period: timedelta,
            last_check: Optional[datetime],
            last_update: Optional[datetime]
    ):
        self.server: Server = server
        self.destination: Destination = destination
        self.source: hallo.modules.subscriptions.source.Source = source
        self.period: timedelta = period
        self.last_check: Optional[datetime] = last_check
        self.last_update: Optional[datetime] = last_update

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            source_class: Type['hallo.modules.new_subscriptions.source.Source'],
            sub_repo,
    ) -> 'Subscription':
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
        try:
            source = source_class.from_input(argument, input_evt.user, sub_repo)
            subscription = Subscription(
                server,
                destination,
                source,
                feed_delta,
                None,
                None
            )
            subscription.update(False)
        except Exception as e:
            raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                f"Failed to create {source_class.type_name} subscription", e
            )
        return subscription

    def needs_check(self) -> bool:
        if self.last_check is None:
            return True
        if datetime.now() > self.last_check + self.period:
            return True
        return False

    def update(self, send: bool = True) -> bool:
        """
        Update subscriptions, get new state, find the change, send messages, and save state
        :param send: Whether to send messages
        :return: Whether messages were sent
        """
        new_state = self.source.current_state()
        was_update = False
        if send:
            update = self.source.state_change(new_state)
            if update:
                was_update = True
                self.last_update = datetime.now()
            self.send(update)
        self.source.save_state(new_state)
        self.last_check = datetime.now()
        return was_update

    def send(self, update):
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        events = self.source.events(self.server, channel, user, update)
        for event in events:
            self.server.send(event)

    @classmethod
    def from_json(cls, json_data: Dict, hallo_obj: Hallo, sub_repo) -> 'Subscription':
        server = hallo_obj.get_server_by_name(json_data["server_name"])
        if server is None:
            raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                'Could not find server with name "{}"'.format(json_data["server_name"])
            )
        # Load channel or user
        if "channel_address" in json_data:
            destination = server.get_channel_by_address(json_data["channel_address"])
        else:
            if "user_address" in json_data:
                destination = server.get_user_by_address(json_data["user_address"])
            else:
                raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                    "Channel or user must be defined."
                )
        if destination is None:
            raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                "Could not find channel or user."
            )
        # Load update frequency
        period = isodate.parse_duration(json_data["period"])
        # Load last check
        last_check = None
        if "last_check" in json_data:
            last_check = dateutil.parser.parse(json_data["last_check"])
        # Load last update
        last_update = None
        if "last_update" in json_data:
            last_update = dateutil.parser.parse(json_data["last_update"])
        # Load source
        source = hallo.modules.subscriptions.subscription_factory.SubscriptionFactory.source_from_json(
            json_data["source"], destination, sub_repo
        )
        subscription = Subscription(
            server,
            destination,
            source,
            period,
            last_check,
            last_update
        )
        return subscription

    def to_json(self) -> Dict:
        json_data = dict()
        json_data["server_name"] = self.server.name
        if isinstance(self.destination, Channel):
            json_data["channel_address"] = self.destination.address
        if isinstance(self.destination, User):
            json_data["user_address"] = self.destination.address
        json_data["period"] = isodate.duration_isoformat(self.period)
        if self.last_check is not None:
            json_data["last_check"] = self.last_check.isoformat()
        if self.last_update is not None:
            json_data["last_update"] = self.last_update.isoformat()
        json_data["source"] = self.source.to_json()
        return json_data
