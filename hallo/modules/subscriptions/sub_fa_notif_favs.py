from datetime import datetime, timedelta
from typing import List, Optional, Dict

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.hallo import Hallo
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class FANotificationFavSub(
    hallo.modules.subscriptions.subscriptions.Subscription['FAKey.FAReader.FANotificationFavourite']
):
    names: List[str] = [
        "fa favs notifications",
        "fa favs",
        "furaffinity favs",
        "fa favourites notifications",
        "fa favourites",
        "furaffinity favourites",
    ]
    type_name: str = "fa_notif_favs"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'hallo.modules.subscriptions.common_fa_key.FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        highest_fav_id: Optional[int] = None,
    ):
        """
        :param highest_fav_id: ID number of the highest favourite notification seen
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: hallo.modules.subscriptions.common_fa_key.FAKey = fa_key
        self.highest_fav_id: int = 0 if highest_fav_id is None else highest_fav_id

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            sub_repo
    ) -> 'FANotificationFavSub':
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Cannot create FA favourite notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` "
                "and your cookie values."
            )
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        fa_sub = FANotificationFavSub(
            server, destination, fa_key, update_frequency=search_delta
        )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["favs"]]

    def get_name(self) -> str:
        return "FA favourite notifications for {}".format(self.fa_key.user.name)

    def check(
            self, *, ignore_result: bool = False
    ) -> List[hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationFavourite]:
        fa_reader = self.fa_key.get_fa_reader()
        notif_page = fa_reader.get_notification_page()
        results = []
        for notif in notif_page.favourites:
            if int(notif.fav_id) > self.highest_fav_id:
                results.append(notif)
        if len(notif_page.favourites) > 0:
            self.highest_fav_id = int(notif_page.favourites[0].fav_id)
        # Update last check time
        self.last_check = datetime.now()
        # Return results
        return results[::-1]

    def format_item(
            self, new_fav: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationFavourite
    ) -> EventMessage:
        output = (
            "You have a new favourite notification, {} ( http://furaffinity.net/user/{}/ ) "
            'has favourited your submission "{}" {}'.format(
                new_fav.name,
                new_fav.username,
                new_fav.submission_name,
                new_fav.submission_link,
            )
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["highest_fav_id"] = self.highest_fav_id
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'FANotificationFavSub':
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
                raise hallo.modules.subscriptions.subscriptions.SubscriptionException("Channel or user must be defined.")
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
        # Load highest favourite id
        highest_fav_id = None
        if "highest_fav_id" in json_obj:
            highest_fav_id = json_obj["highest_fav_id"]
        new_sub = FANotificationFavSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            highest_fav_id=highest_fav_id,
        )
        new_sub.last_update = last_update
        return new_sub
