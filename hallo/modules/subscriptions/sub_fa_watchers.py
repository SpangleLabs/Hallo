from datetime import datetime, timedelta
from typing import List, Optional, Dict

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.hallo import Hallo
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class FAUserWatchersSub(
    hallo.modules.subscriptions.subscriptions.Subscription[
        hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch
    ]
):
    names: List[str] = [
        "fa user watchers",
        "fa user new watchers",
        "furaffinity user watchers",
        "furaffinity user new watchers",
    ]
    type_name: str = "fa_user_watchers"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: hallo.modules.subscriptions.common_fa_key.FAKey,
        username: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        newest_watchers: Optional[List[str]] = None,
    ):
        """
        :param newest_watchers: List of user's most recent new watchers' usernames
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: hallo.modules.subscriptions.common_fa_key.FAKey = fa_key
        self.username: str = username
        self.newest_watchers: List[str] = [] if newest_watchers is None else newest_watchers

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            sub_repo
    ) -> 'FAUserWatchersSub':
        # Get FAKey object
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Cannot create FA user watchers subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
            )
        # Get server and destination
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if last argument is check period.
        try:
            try_period = input_evt.command_args.split()[-1]
            search_delta = isodate.parse_duration(try_period)
            username = input_evt.command_args[: -len(try_period)].strip()
        except isodate.isoerror.ISO8601Error:
            username = input_evt.command_args.strip()
            search_delta = isodate.parse_duration("PT600S")
        # Create FA user favs object
        fa_sub = FAUserWatchersSub(
            server, destination, fa_key, username, update_frequency=search_delta
        )
        # Check if it's a valid user
        try:
            fa_key.get_fa_reader().get_user_page(username)
        except Exception:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "This does not appear to be a valid username."
            )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    def get_name(self) -> str:
        return 'New watchers subscription for "{}"'.format(self.username)

    def check(
            self, *, ignore_result: bool = False
    ) -> List[hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch]:
        fa_reader = self.fa_key.get_fa_reader()
        results = []
        user_page = fa_reader.get_user_page(self.username)
        next_batch = []
        matched_ids = False
        for new_watcher in user_page.watched_by:
            watcher_username = new_watcher.watcher_username
            # Batch things that have been seen, so that the results after the last result in latest_ids aren't included
            if watcher_username in self.newest_watchers:
                results += next_batch
                next_batch = []
                matched_ids = True
            else:
                next_batch.append(new_watcher)
        # If no watchers in list matched an ID in last seen, send all results from list
        if not matched_ids:
            results += next_batch
        # Create new list of latest ten results
        self.newest_watchers = [
            new_watcher.watcher_username for new_watcher in user_page.watched_by
        ]
        self.last_check = datetime.now()
        return results[::-1]

    def format_item(self, item: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAWatch) -> EventMessage:
        link = "https://furaffinity.net/user/{}/".format(item.watcher_username)
        # Construct output
        output = "{} has watched {}. Link: {}".format(
            item.watcher_name, item.watched_name, link
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        return EventMessage(self.server, channel, user, output, inbound=False)

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["username"] = self.username
        json_obj["newest_watchers"] = []
        for new_watcher in self.newest_watchers:
            json_obj["newest_watchers"].append(new_watcher)
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'FAUserWatchersSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
        # Load channel or user
        if "channel_address" in json_obj:
            destination = server.get_channel_by_address(json_obj["channel_address"])
        else:
            if "user_address" in json_obj:
                destination = server.get_user_by_address(json_obj["user_address"])
            else:
                raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                    "Channel or user must be defined."
                )
        if destination is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException("Could not find chanel or user.")
        # Load last check
        last_check = None
        if "last_check" in json_obj:
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load username
        username = json_obj["username"]
        # Load newest watcher list
        newest_watchers = []
        for new_watcher in json_obj["newest_watchers"]:
            newest_watchers.append(new_watcher)
        new_sub = FAUserWatchersSub(
            server,
            destination,
            fa_key,
            username,
            last_check=last_check,
            update_frequency=update_frequency,
            newest_watchers=newest_watchers,
        )
        new_sub.last_update = last_update
        return new_sub


class FANotificationWatchSub(FAUserWatchersSub):
    names: List[str] = [
        "{}{}{}{}".format(fa, new, watchers, notifications)
        for fa in ["fa ", "furaffinity "]
        for new in ["new ", ""]
        for watchers in ["watcher", "watchers"]
        for notifications in ["", " notifications"]
    ]
    type_name: str = "fa_notif_watchers"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: hallo.modules.subscriptions.common_fa_key.FAKey,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        newest_watchers: Optional[str] = None,
    ):
        """
        :param newest_watchers: List of user's most recent new watchers' usernames
        """
        username: str = fa_key.get_fa_reader().get_notification_page().username
        super().__init__(
            server,
            destination,
            fa_key,
            username,
            last_check=last_check,
            update_frequency=update_frequency,
            newest_watchers=newest_watchers,
        )

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            sub_repo
    ) -> 'FANotificationWatchSub':
        # Get FAKey object
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Cannot create FA watcher notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
            )
        # Get server and destination
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        # Create FA user watchers object
        try:
            fa_sub = FANotificationWatchSub(
                server, destination, fa_key, update_frequency=search_delta
            )
        except Exception:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Yours does not appear to be a valid username? I cannot access your profile page."
            )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["watchers"]]

    def get_name(self) -> str:
        return "New watchers notifications for {}".format(self.fa_key.user.name)

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        del json_obj["username"]
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'FANotificationWatchSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
        # Load channel or user
        if "channel_address" in json_obj:
            destination = server.get_channel_by_address(json_obj["channel_address"])
        else:
            if "user_address" in json_obj:
                destination = server.get_user_by_address(json_obj["user_address"])
            else:
                raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                    "Channel or user must be defined."
                )
        if destination is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException("Could not find chanel or user.")
        # Load last check
        last_check = None
        if "last_check" in json_obj:
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load newest watcher list
        newest_watchers = []
        for new_watcher in json_obj["newest_watchers"]:
            newest_watchers.append(new_watcher)
        new_sub = FANotificationWatchSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            newest_watchers=newest_watchers,
        )
        new_sub.last_update = last_update
        return new_sub
