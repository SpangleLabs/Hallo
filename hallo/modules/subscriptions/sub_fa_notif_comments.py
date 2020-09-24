from datetime import datetime, timedelta
from typing import Union, List, Optional, Dict
from urllib.error import HTTPError

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.hallo import Hallo
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class FANotificationCommentsSub(
    hallo.modules.subscriptions.subscriptions.Subscription[Union[
        'FAKey.FAReader.FANotificationCommentSubmission',
        'FAKey.FAReader.FANotificationCommentJournal',
        'FAKey.FAReader.FANotificationShout'
    ]]
):
    names: List[str] = [
        "{}{}{}".format(fa, comments, notifications)
        for fa in ["fa ", "furaffinity "]
        for comments in ["comments", "comment", "shouts", "shout"]
        for notifications in ["", " notifications"]
    ]
    type_name: str = "fa_notif_comments"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'hallo.modules.subscriptions.common_fa_key.FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_comment_id_journal: Optional[int] = None,
        latest_comment_id_submission: Optional[int] = None,
        latest_shout_id: Optional[int] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: hallo.modules.subscriptions.common_fa_key.FAKey = fa_key
        self.latest_comment_id_journal: int = (
            0 if latest_comment_id_journal is None else latest_comment_id_journal
        )
        self.latest_comment_id_submission: int = (
            0 if latest_comment_id_submission is None else latest_comment_id_submission
        )
        self.latest_shout_id: int = 0 if latest_shout_id is None else latest_shout_id

    @staticmethod
    def create_from_input(
            input_evt: EventMessage, sub_repo
    ) -> 'FANotificationCommentsSub':
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Cannot create FA comments notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` and your cookie values."
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
        fa_sub = FANotificationCommentsSub(
            server, destination, fa_key, update_frequency=search_delta
        )
        fa_sub.check()
        return fa_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["comments"]]

    def get_name(self) -> str:
        return "FA comments for {}".format(self.fa_key.user.name)

    def check(
            self, *, ignore_result: bool = False
    ) -> List[Union[
        'hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationCommentSubmission',
        'hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationCommentJournal',
        'hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationShout'
    ]]:
        notif_page = self.fa_key.get_fa_reader().get_notification_page()
        results = []
        # Check submission comments
        for submission_notif in notif_page.submission_comments:
            if int(submission_notif.comment_id) > self.latest_comment_id_submission:
                results.append(submission_notif)
        # Check journal comments
        for journal_notif in notif_page.journal_comments:
            if int(journal_notif.comment_id) > self.latest_comment_id_journal:
                results.append(journal_notif)
        # Check shouts
        for shout_notif in notif_page.shouts:
            if int(shout_notif.shout_id) > self.latest_shout_id:
                results.append(shout_notif)
        # Reset high water marks.
        if len(notif_page.submission_comments) > 0:
            self.latest_comment_id_submission = int(
                notif_page.submission_comments[0].comment_id
            )
        if len(notif_page.journal_comments) > 0:
            self.latest_comment_id_journal = int(
                notif_page.journal_comments[0].comment_id
            )
        if len(notif_page.shouts) > 0:
            self.latest_shout_id = int(notif_page.shouts[0].shout_id)
        # Update last check time
        self.last_check = datetime.now()
        # Return results
        return results[::-1]

    def format_item(
            self, item: Union[
                'hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationCommentSubmission',
                'hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationCommentJournal',
                'hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationShout'
            ]
    ) -> EventMessage:
        output = "Err, comments did something?"
        fa_reader = self.fa_key.get_fa_reader()
        if isinstance(item, hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationShout):
            try:
                user_page_shouts = fa_reader.get_user_page(item.page_username).shouts
                shout = [
                    shout
                    for shout in user_page_shouts
                    if shout.shout_id == item.shout_id
                ]
                output = (
                    "You have a new shout, from {} ( http://furaffinity.net/user/{}/ ) "
                    "has left a shout saying: \n\n{}".format(
                        item.name, item.username, shout[0].text
                    )
                )
            except HTTPError:
                output = (
                    "You have a new shout, from {} ( http://furaffinity.net/user/{}/ ) "
                    "has left a shout but I can't find it on your user page: \n"
                    "https://furaffinity.net/user/{}/".format(
                        item.name, item.username, item.page_username
                    )
                )
        if isinstance(item, hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationCommentJournal):
            try:
                journal_page = fa_reader.get_journal_page(item.journal_id)
                comment = journal_page.comments_section.get_comment_by_id(
                    item.comment_id
                )
                output = (
                    "You have a journal comment notification. {} has made a new comment {}on {} journal "
                    '"{}" {} : \n\n{}'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.journal_yours else "their"),
                        item.journal_name,
                        item.journal_link,
                        comment.text,
                    )
                )
            except HTTPError:
                output = (
                    "You have a journal comment notification. {} has made a new comment {}on {} journal "
                    '"{}" {} but I can\'t find the comment.'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.journal_yours else "their"),
                        item.journal_name,
                        item.journal_link,
                    )
                )
        if isinstance(item, hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANotificationCommentSubmission):
            try:
                submission_page = fa_reader.get_submission_page(item.submission_id)
                comment = submission_page.comments_section.get_comment_by_id(
                    item.comment_id
                )
                output = (
                    "You have a submission comment notification. "
                    '{} has made a new comment {}on {} submission "{}" {} : \n\n{}'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.submission_yours else "their"),
                        item.submission_name,
                        item.submission_link,
                        comment.text,
                    )
                )
            except HTTPError:
                output = (
                    "You have a submission comment notification. "
                    '{} has made a new comment {}on {} submission "{}" {} : but I can\'t find the comment.'.format(
                        item.name,
                        ("in response to your comment " if item.comment_on else ""),
                        ("your" if item.submission_yours else "their"),
                        item.submission_name,
                        item.submission_link,
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
        json_obj["latest_comment_id_journal"] = self.latest_comment_id_journal
        json_obj["latest_comment_id_submission"] = self.latest_comment_id_submission
        json_obj["latest_shout_id"] = self.latest_shout_id
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'FANotificationCommentsSub':
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
        # Load comment IDs and count
        latest_comment_id_journal = int(json_obj["latest_comment_id_journal"])
        latest_comment_id_submission = int(json_obj["latest_comment_id_submission"])
        latest_shout_id = int(json_obj["latest_shout_id"])
        new_sub = FANotificationCommentsSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            latest_comment_id_journal=latest_comment_id_journal,
            latest_comment_id_submission=latest_comment_id_submission,
            latest_shout_id=latest_shout_id,
        )
        new_sub.last_update = last_update
        return new_sub
