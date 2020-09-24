from datetime import datetime, timedelta
from typing import Optional, List, Dict

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.hallo import Hallo
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class FAUserFavsSub(
    hallo.modules.subscriptions.subscriptions.Subscription[Optional['FAKey.FAReader.FAViewSubmissionPage']]
):
    names: List[str] = [
        "fa user favs",
        "furaffinity user favs",
        "furaffinity user favourites",
        "fa user favourites",
        "furaffinity user favorites",
        "fa user favorites",
    ]
    type_name: str = "fa_user_favs"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'hallo.modules.subscriptions.common_fa_key.FAKey',
        username: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_ids: Optional[List[str]] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: hallo.modules.subscriptions.common_fa_key.FAKey = fa_key
        self.username: str = username.lower().strip()
        if latest_ids is None:
            latest_ids = []
        self.latest_ids: List[str] = latest_ids

    @staticmethod
    def create_from_input(
            input_evt: EventMessage, sub_repo
    ) -> 'FAUserFavsSub':
        # Get FAKey object
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Cannot create FA user favourites subscription without cookie details. "
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
        fa_sub = FAUserFavsSub(
            server, destination, fa_key, username, update_frequency=search_delta
        )
        # Check if it's a valid user
        try:
            fa_key.get_fa_reader().get_user_page(username)
        except Exception:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "This does not appear to be a valid FA username."
            )
        fa_sub.check(ignore_result=True)
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean == self.username.lower().strip()

    def get_name(self) -> str:
        return 'Favourites subscription for "{}"'.format(self.username)

    def check(
            self, *, ignore_result: bool = False
    ) -> List[Optional['hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAViewSubmissionPage']]:
        """
        Returns the list of FA Favourites since the last ones were seen, in oldest->newest order
        """
        fa_reader = self.fa_key.get_fa_reader()
        results = []
        favs_page = fa_reader.get_user_fav_page(self.username)
        next_batch = []
        matched_ids = False
        for result_id in favs_page.fav_ids:
            # Batch things that have been seen, so that the results after the last result in latest_ids aren't included
            if result_id in self.latest_ids:
                results += next_batch
                next_batch = []
                matched_ids = True
            else:
                next_batch.append(result_id)
        # If no images in search matched an ID in last seen, send all results from search
        if not matched_ids:
            results += next_batch
        # Get submission pages for each result
        result_pages = []
        for result_id in results:
            if ignore_result:
                result_pages.append(None)
            else:
                result_pages.append(fa_reader.get_submission_page(result_id))
        # Create new list of latest ten results
        self.latest_ids = favs_page.fav_ids[:10]
        self.last_check = datetime.now()
        return result_pages[::-1]

    def format_item(
        self, item: Optional['hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FAViewSubmissionPage']
    ) -> EventMessage:
        link = "https://furaffinity.net/view/{}".format(item.submission_id)
        title = item.title
        posted_by = item.name
        # Construct output
        output = '{} has favourited a new image. "{}" by {}. {}'.format(
            self.username, title, posted_by, link
        )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        # Get submission page and file extension
        image_url = item.full_image
        file_extension = image_url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif"]:
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, image_url, inbound=False
            )
            return output_evt
        return EventMessage(self.server, channel, user, output, inbound=False)

    @staticmethod
    def from_json(
        json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'FAUserFavsSub':
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
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        username = json_obj["username"]
        # Create FAUserFavsSub
        new_sub = FAUserFavsSub(
            server,
            destination,
            fa_key,
            username,
            last_check=last_check,
            update_frequency=update_frequency,
            latest_ids=latest_ids,
        )
        new_sub.last_update = last_update
        return new_sub

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["username"] = self.username
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj
