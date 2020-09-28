from typing import Dict, Optional, List
from urllib.error import HTTPError

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage
from hallo.modules.new_subscriptions.source import Source, Update, State
from hallo.modules.new_subscriptions.source_fa_favs import fa_key_from_json, fa_key_from_input
from hallo.modules.new_subscriptions.stream_source import StreamSource, Key
from hallo.modules.new_subscriptions.common_fa_key import FAKey
from hallo.server import Server


class FASubmissionCommentSource(StreamSource[FAKey.FAReader.FANotificationCommentSubmission]):
    type_name = "fa submission comments"
    type_names = ["fa submission comments"]

    def __init__(self, fa_key: FAKey, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[FAKey.FAReader.FANotificationCommentSubmission]:
        notif_page = self.fa_key.get_fa_reader().get_notification_page()
        return notif_page.submission_comments

    def item_to_key(self, item: FAKey.FAReader.FANotificationCommentSubmission) -> Key:
        return item.comment_id

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: FAKey.FAReader.FANotificationCommentSubmission
    ) -> EventMessage:
        fa_reader = self.fa_key.get_fa_reader()
        response_str = "in response to your comment " if item.comment_on else ""
        owner_str = "your" if item.submission_yours else "their"
        try:
            submission_page = fa_reader.get_submission_page(item.submission_id)
            comment = submission_page.comments_section.get_comment_by_id(
                item.comment_id
            )
            return EventMessage(
                server, channel, user,
                "You have a submission comment notification. "
                f'{item.name} has made a new comment {response_str}on {owner_str} submission '
                f'"{item.submission_name}" {item.submission_link} : \n\n{comment.text}'
            )
        except HTTPError:
            return EventMessage(
                server, channel, user,
                "You have a submission comment notification. "
                f'{item.name} has made a new comment {response_str}on {owner_str} submission '
                f'"{item.submission_name}" {item.submission_link} : but I can\'t find the comment.'
            )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["submission comments"]]

    @property
    def title(self) -> str:
        return f"FA submission comments for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FASubmissionCommentSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FASubmissionCommentSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FASubmissionCommentSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FASubmissionCommentSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FAJournalCommentSource(StreamSource[FAKey.FAReader.FANotificationCommentJournal]):
    type_name = "fa journal comments"
    type_names = ["fa journal comments"]

    def __init__(self, fa_key: FAKey, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[FAKey.FAReader.FANotificationCommentJournal]:
        notif_page = self.fa_key.get_fa_reader().get_notification_page()
        return notif_page.journal_comments

    def item_to_key(self, item: FAKey.FAReader.FANotificationCommentJournal) -> Key:
        return item.comment_id

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: FAKey.FAReader.FANotificationCommentJournal
    ) -> EventMessage:
        fa_reader = self.fa_key.get_fa_reader()
        response_str = "in response to your comment " if item.comment_on else ""
        owner_str = "your" if item.journal_yours else "their"
        try:
            journal_page = fa_reader.get_journal_page(item.journal_id)
            comment = journal_page.comments_section.get_comment_by_id(
                item.comment_id
            )
            return EventMessage(
                server, channel, user,
                f"You have a journal comment notification. {item.name} has made a new comment "
                f"{response_str}on {owner_str} journal "
                f'"{item.journal_name}" {item.journal_link} : \n\n{comment.text}'
            )
        except HTTPError:
            return EventMessage(
                server, channel, user,
                f"You have a journal comment notification. {item.name} has made a new comment "
                f"{response_str}on {owner_str} journal "
                f'"{item.journal_name}" {item.journal_link} but I can\'t find the comment.'
            )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["journal comments"]]

    @property
    def title(self) -> str:
        return f"FA journal comments for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAJournalCommentSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FAJournalCommentSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAJournalCommentSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FAJournalCommentSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FAShoutSource(StreamSource[FAKey.FAReader.FANotificationShout]):
    type_name = "fa shouts"
    type_names = ["fa shouts"]

    def __init__(self, fa_key: FAKey, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.fa_key = fa_key

    def current_state(self) -> List[FAKey.FAReader.FANotificationShout]:
        notif_page = self.fa_key.get_fa_reader().get_notification_page()
        return notif_page.shouts

    def item_to_key(self, item: FAKey.FAReader.FANotificationShout) -> Key:
        return item.shout_id

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: FAKey.FAReader.FANotificationShout
    ) -> EventMessage:
        fa_reader = self.fa_key.get_fa_reader()
        try:
            user_page_shouts = fa_reader.get_user_page(item.page_username).shouts
            shout = [
                shout
                for shout in user_page_shouts
                if shout.shout_id == item.shout_id
            ]
            return EventMessage(
                server, channel, user,
                f"You have a new shout, from {item.name} ( http://furaffinity.net/user/{item.username}/ ) "
                f"has left a shout saying: \n\n{shout[0].text}"
            )
        except HTTPError:
            return EventMessage(
                server, channel, user,
                f"You have a new shout, from {item.name} ( http://furaffinity.net/user/{item.username}/ ) "
                "has left a shout but I can't find it on your user page: \n"
                f"https://furaffinity.net/user/{item.page_username}/"
            )

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.type_names + ["shouts"]]

    @property
    def title(self) -> str:
        return f"FA shouts for {self.fa_key.user.name}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FAShoutSource':
        fa_key = fa_key_from_input(user, sub_repo)
        return FAShoutSource(fa_key)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'FAShoutSource':
        fa_key = fa_key_from_json(json_data["fa_key_user_address"], destination.server, sub_repo)
        return FAShoutSource(fa_key, json_data["last_keys"])

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "fa_key_user_address": self.fa_key.user.address,
            "last_keys": self.last_keys
        }


class FACommentNotificationsSource(Source):
    names: List[str] = [
        "{}{}{}".format(fa, comments, notifications)
        for fa in ["fa ", "furaffinity "]
        for comments in ["comments", "comment", "shouts", "shout"]
        for notifications in ["", " notifications"]
    ]
    type_name: str = "fa_notif_comments"

    def __init__(
            self,
            fa_key: FAKey,
            submission_source: FASubmissionCommentSource,
            journal_source: FAJournalCommentSource,
            shout_source: FAShoutSource,
    ):
        super().__init__()
        self.fa_key = fa_key
        self.submission_source = submission_source
        self.journal_source = journal_source
        self.shout_source = shout_source

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["comments"]]

    @property
    def title(self) -> str:
        return "FA comments for {}".format(self.fa_key.user.name)

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'FACommentNotificationsSource':
        fa_key = fa_key_from_input(user, sub_repo)
        submission_source = FASubmissionCommentSource(fa_key)
        journal_source = FAJournalCommentSource(fa_key)
        shout_source = FAShoutSource(fa_key)
        return FACommentNotificationsSource(fa_key, submission_source, journal_source, shout_source)

    def current_state(self) -> State:
        return {
            "submissions": self.submission_source.current_state(),
            "journals": self.journal_source.current_state(),
            "shouts": self.shout_source.current_state()
        }

    def state_change(self, state: State) -> Optional[Update]:
        return {
            "submissions": self.submission_source.state_change(state["submissions"]),
            "journals": self.journal_source.state_change(state["journals"]),
            "shouts": self.shout_source.state_change(state["shouts"])
        }

    def save_state(self, state: State) -> None:
        self.submission_source.save_state(state["submissions"])
        self.journal_source.save_state(state["journals"])
        self.shout_source.save_state(state["shouts"])

    def events(
            self, server: Server, channel: Optional[Channel], user: Optional[User], update: Update
    ) -> List[EventMessage]:
        return (
            self.submission_source.events(server, channel, user, update["submissions"])
            + self.journal_source.events(server, channel, user, update["journals"])
            + self.shout_source.events(server, channel, user, update["shouts"])
        )

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'Source':
        user_addr = json_data["fa_key_user_address"]
        fa_key = fa_key_from_json(user_addr, destination.server, sub_repo)
        submission_source = FASubmissionCommentSource.from_json(json_data["submissions"], destination, sub_repo)
        journal_source = FAJournalCommentSource.from_json(json_data["journals"], destination, sub_repo)
        shout_source = FAShoutSource.from_json(json_data["shouts"], destination, sub_repo)
        return FACommentNotificationsSource(fa_key, submission_source, journal_source, shout_source)

    def to_json(self) -> Dict:
        json_data = super().to_json()
        json_data["type"] = self.type_name
        json_data["fa_key_user_address"] = self.fa_key.user.address
        json_data["submissions"] = self.submission_source.to_json()
        json_data["journals"] = self.journal_source.to_json()
        json_data["shouts"] = self.shout_source.to_json()
        return json_data
