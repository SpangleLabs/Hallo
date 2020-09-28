import logging
import os
from datetime import timedelta, datetime
from typing import Dict, Optional, Union, List, Callable

import dateutil.parser

import hallo.modules.user_data
from hallo.destination import User
from hallo.inc.commons import CachedObject, Commons
import hallo.modules.new_subscriptions.subscription_common

logger = logging.getLogger(__name__)


class FAKeysCommon(hallo.modules.new_subscriptions.subscription_common.SubscriptionCommon):
    type_name: str = "fa_keys"

    def __init__(self):
        self.list_keys: Dict[User, FAKey] = dict()

    def get_key_by_user(self, user: User) -> Optional['FAKey']:
        if user in self.list_keys:
            return self.list_keys[user]
        user_data_parser = hallo.modules.user_data.UserDataParser()
        fa_data: hallo.modules.user_data.FAKeyData = user_data_parser.get_data_by_user_and_type(
            user, hallo.modules.user_data.FAKeyData
        )
        if fa_data is None:
            return None
        fa_key = FAKey(user, fa_data.cookie_a, fa_data.cookie_b)
        self.add_key(fa_key)
        return fa_key

    def add_key(self, key: 'FAKey') -> None:
        self.list_keys[key.user] = key

    def to_json(self) -> Optional[Dict]:
        return None

    @staticmethod
    def from_json(json_obj: Optional[Dict]) -> 'FAKeysCommon':
        return FAKeysCommon()


class FAKey:
    def __init__(self, user: User, cookie_a: str, cookie_b: str) -> None:
        self.user = user
        self.cookie_a = cookie_a
        self.cookie_b = cookie_b
        self.fa_reader: Optional[FAKey.FAReader] = None

    def get_fa_reader(self) -> 'FAKey.FAReader':
        if self.fa_reader is None:
            self.fa_reader = FAKey.FAReader(self.cookie_a, self.cookie_b)
        return self.fa_reader

    class FAReader:
        NOTES_INBOX = "inbox"
        NOTES_OUTBOX = "outbox"

        class FALoginFailedError(Exception):
            pass

        def __init__(self, cookie_a: str, cookie_b: str):
            self.a = cookie_a
            self.b = cookie_b
            self.timeout: timedelta = timedelta(seconds=60)
            self.notification_page_cache = CachedObject(
                lambda: FAKey.FAReader.FANotificationsPage(
                    self._get_api_data("notifications/others.json", True)
                ),
                self.timeout,
            )
            self.submissions_page_cache = CachedObject(
                lambda: FAKey.FAReader.FASubmissionsPage(
                    self._get_api_data("notifications/submissions.json", True)
                ),
                self.timeout,
            )
            self.notes_page_inbox_cache = CachedObject(
                lambda: FAKey.FAReader.FANotesPage(
                    self._get_api_data("notes/inbox.json", True), self.NOTES_INBOX
                ),
                self.timeout,
            )
            self.notes_page_outbox_cache = CachedObject(
                lambda: FAKey.FAReader.FANotesPage(
                    self._get_api_data("notes/outbox.json", True), self.NOTES_OUTBOX
                ),
                self.timeout,
            )

        def _get_api_data(self, path: str, needs_cookie: bool = False) -> Union[Dict, List]:
            fa_api_url = os.getenv("FA_API_URL", "https://faexport.spangle.org.uk")
            url = "{}/{}".format(fa_api_url, path)
            if needs_cookie:
                cookie_string = "b=" + self.b + "; a=" + self.a
                return Commons.load_url_json(url, [["FA_COOKIE", cookie_string]])
            return Commons.load_url_json(url)

        def get_notification_page(self) -> 'FAKey.FAReader.FANotificationsPage':
            return self.notification_page_cache.get()

        def get_submissions_page(self) -> 'FAKey.FAReader.FASubmissionsPage':
            return self.submissions_page_cache.get()

        def get_notes_page(self, folder: str) -> 'FAKey.FAReader.FANotesPage':
            if folder == self.NOTES_INBOX:
                return self.notes_page_inbox_cache.get()
            if folder == self.NOTES_OUTBOX:
                return self.notes_page_outbox_cache.get()
            raise ValueError("Invalid FA note folder.")

        def get_user_page(self, username: str) -> 'FAKey.FAReader.FAUserPage':
            # Needs shout list, for checking own shouts
            data = self._get_api_data("/user/{}.json".format(username))

            def shout_data_getter():
                return self._get_api_data("/user/{}/shouts.json".format(username))

            user_page = FAKey.FAReader.FAUserPage(data, shout_data_getter, username)
            return user_page

        def get_user_fav_page(self, username: str) -> 'FAKey.FAReader.FAUserFavouritesPage':
            # This endpoint returns a list of submission IDs
            id_list: List[int] = self._get_api_data("/user/{}/favorites.json".format(username))
            fav_page = FAKey.FAReader.FAUserFavouritesPage(id_list, username)
            return fav_page

        def get_submission_page(self, submission_id: Union[int, str]) -> 'FAKey.FAReader.FAViewSubmissionPage':
            data = self._get_api_data("/submission/{}.json".format(submission_id))

            def comment_data_getter():
                return self._get_api_data(
                    "/submission/{}/comments.json".format(submission_id)
                )

            sub_page = FAKey.FAReader.FAViewSubmissionPage(
                data, comment_data_getter, submission_id
            )
            return sub_page

        def get_journal_page(self, journal_id: Union[int, str]) -> 'FAKey.FAReader.FAViewJournalPage':
            data = self._get_api_data("/journal/{}.json".format(journal_id))

            def comment_data_getter():
                return self._get_api_data(
                    "/journal/{}/comments.json".format(journal_id)
                )

            journal_page = FAKey.FAReader.FAViewJournalPage(
                data, comment_data_getter, journal_id
            )
            return journal_page

        def get_search_page(self, search_term: str) -> 'FAKey.FAReader.FASearchPage':
            id_list = self._get_api_data("/search.json?q={}".format(search_term))
            search_page = FAKey.FAReader.FASearchPage(id_list, search_term)
            return search_page

        class FANotificationsPage:
            def __init__(self, data: Dict):
                self.username: str = data["current_user"]["profile_name"]
                self.watches: List[FAKey.FAReader.FANotificationWatch] = []
                watch_list = data["new_watches"]
                for watch_notif in watch_list:
                    try:
                        new_watch = FAKey.FAReader.FANotificationWatch(
                            watch_notif["name"],
                            watch_notif["profile_name"],
                            watch_notif["avatar"],
                        )
                        self.watches.append(new_watch)
                    except Exception as e:
                        logger.error("Failed to read watch: ", exc_info=e)
                self.submission_comments: List[FAKey.FAReader.FANotificationCommentSubmission] = []
                sub_comment_list = data["new_submission_comments"]
                for sub_comment_notif in sub_comment_list:
                    try:
                        new_comment = FAKey.FAReader.FANotificationCommentSubmission(
                            sub_comment_notif["comment_id"],
                            sub_comment_notif["profile_name"],
                            sub_comment_notif["name"],
                            sub_comment_notif["is_reply"],
                            sub_comment_notif["your_submission"],
                            sub_comment_notif["submission_id"],
                            sub_comment_notif["title"],
                        )
                        self.submission_comments.append(new_comment)
                    except Exception as e:
                        logger.error("Failed to read submission comment: ", exc_info=e)
                self.journal_comments: List[FAKey.FAReader.FANotificationCommentJournal] = []
                jou_comment_list = data["new_journal_comments"]
                for jou_comment_notif in jou_comment_list:
                    try:
                        new_comment = FAKey.FAReader.FANotificationCommentJournal(
                            jou_comment_notif["comment_id"],
                            jou_comment_notif["profile_name"],
                            jou_comment_notif["name"],
                            jou_comment_notif["is_reply"],
                            jou_comment_notif["your_journal"],
                            jou_comment_notif["journal_id"],
                            jou_comment_notif["title"],
                        )
                        self.journal_comments.append(new_comment)
                    except Exception as e:
                        logger.error("Failed to read journal comment: ", exc_info=e)
                self.shouts: List[FAKey.FAReader.FANotificationShout] = []
                shout_list = data["new_shouts"]
                for shout_notif in shout_list:
                    try:
                        new_shout = FAKey.FAReader.FANotificationShout(
                            shout_notif["shout_id"],
                            shout_notif["profile_name"],
                            shout_notif["name"],
                            data["current_user"]["profile_name"],
                        )
                        self.shouts.append(new_shout)
                    except Exception as e:
                        logger.error("Failed to read shout: ", exc_info=e)
                self.favourites: List[FAKey.FAReader.FANotificationFavourite] = []
                fav_list = data["new_favorites"]
                for fav_notif in fav_list:
                    try:
                        new_fav = FAKey.FAReader.FANotificationFavourite(
                            fav_notif["favorite_notification_id"],
                            fav_notif["profile_name"],
                            fav_notif["name"],
                            fav_notif["submission_id"],
                            fav_notif["submission_name"],
                        )
                        self.favourites.append(new_fav)
                    except Exception as e:
                        logger.error("Failed to read favourite: ", exc_info=e)
                self.journals: List[FAKey.FAReader.FANotificationJournal] = []
                jou_list = data["new_journals"]
                for jou_notif in jou_list:
                    try:
                        new_journal = FAKey.FAReader.FANotificationJournal(
                            jou_notif["journal_id"],
                            jou_notif["title"],
                            jou_notif["profile_name"],
                            jou_notif["name"],
                        )
                        self.journals.append(new_journal)
                    except Exception as e:
                        logger.error("Failed to read journal: ", exc_info=e)

        class FANotificationWatch:
            def __init__(self, name: str, username: str, avatar: str):
                self.name: str = name
                self.username: str = username
                self.link: str = "https://furaffinity.net/user/{}/".format(username)
                self.avatar: str = avatar

        class FANotificationCommentSubmission:
            def __init__(
                    self,
                    comment_id: str,
                    username: str,
                    name: str,
                    comment_on: bool,
                    submission_yours: bool,
                    submission_id: str,
                    submission_name: str,
            ):
                self.comment_id: str = comment_id
                self.comment_link: str = "https://furaffinity.net/view/{}/#cid:{}".format(
                    submission_id, comment_id
                )
                self.username: str = username
                self.name: str = name
                self.comment_on: bool = comment_on
                self.submission_yours: bool = submission_yours
                self.submission_id = submission_id
                self.submission_name = submission_name
                self.submission_link: str = "https://furaffinity.net/view/{}/".format(
                    submission_id
                )

        class FANotificationCommentJournal:
            def __init__(
                    self,
                    comment_id: str,
                    username: str,
                    name: str,
                    comment_on: bool,
                    journal_yours: bool,
                    journal_id: str,
                    journal_name: str,
            ):
                self.comment_id: str = comment_id
                self.comment_link: str = "https://furaffinity.net/journal/{}/#cid:{}".format(
                    journal_id, comment_id
                )
                self.username: str = username
                self.name: str = name
                self.comment_on: bool = comment_on
                self.journal_yours: bool = journal_yours
                self.journal_id: str = journal_id
                self.journal_name: str = journal_name
                self.journal_link: str = "https://furaffinity.net/journal/{}/".format(
                    journal_id
                )

        class FANotificationShout:
            def __init__(self, shout_id: str, username: str, name: str, page_username: str):
                self.shout_id: str = shout_id
                self.username: str = username
                self.name: str = name
                self.page_username: str = page_username

        class FANotificationFavourite:
            def __init__(self, fav_id: str, username: str, name: str, submission_id: str, submission_name: str):
                self.fav_id: str = fav_id
                self.username: str = username
                self.name: str = name
                self.submission_id: str = submission_id
                self.submission_name: str = submission_name
                self.submission_link: str = "https://furaffinity.net/view/{}/".format(
                    submission_id
                )

        class FANotificationJournal:
            def __init__(self, journal_id: str, journal_name: str, username: str, name: str):
                self.journal_id: str = journal_id
                self.journal_link: str = "https://furaffinity.net/journal/{}/".format(
                    journal_id
                )
                self.journal_name: str = journal_name
                self.username: str = username
                self.name: str = name

        class FASubmissionsPage:
            def __init__(self, data: Dict):
                self.submissions: List[FAKey.FAReader.FANotificationSubmission] = []
                subs_list = data["new_submissions"]
                for sub_notif in subs_list:
                    new_submission = FAKey.FAReader.FANotificationSubmission(
                        sub_notif["id"],
                        sub_notif["link"],
                        sub_notif["title"],
                        sub_notif["profile_name"],
                        sub_notif["name"],
                    )
                    self.submissions.append(new_submission)

        class FANotificationSubmission:
            def __init__(self, submission_id: str, preview_link: str, title: str, username: str, name: str):
                self.submission_id: str = submission_id
                self.submission_link: str = "https://furaffinity.net/view/{}/".format(
                    submission_id
                )
                self.preview_link: str = preview_link
                self.title: str = title
                self.username: str = username
                self.name: str = name

        class FANotesPage:
            def __init__(self, data: Dict, folder: str):
                self.folder: str = folder
                self.notes: List[FAKey.FAReader.FANote] = []
                for note in data:
                    new_note = FAKey.FAReader.FANote(
                        note["note_id"],
                        note["subject"],
                        note["profile_name"],
                        note["name"],
                        note["is_read"],
                    )
                    self.notes.append(new_note)

        class FANote:
            def __init__(self, note_id: str, subject: str, username: str, name: str, is_read: bool):
                self.note_id: str = note_id
                self.note_link: str = "https://www.furaffinity.net/viewmessage/{}/".format(
                    note_id
                )
                self.subject: str = subject
                self.username: str = username
                self.name: str = name
                self.is_read: bool = is_read

        class FAUserPage:
            def __init__(self, data: Dict, shout_data_getter: Callable[[], Dict], username: str):
                self.username: str = username
                self.name: str = data["full_name"]
                self.user_title: Optional[str] = (
                    data["user_title"] if len(data["user_title"]) != 0 else None
                )
                self.registered_since: datetime = dateutil.parser.parse(data["registered_at"])
                self.current_mood: str = data["current_mood"]
                # artist_profile
                self.num_page_visits: int = int(data["pageviews"])
                self.num_submissions: int = int(data["submissions"])
                self.num_comments_received: int = int(data["comments_received"])
                self.num_comments_given: int = int(data["comments_given"])
                self.num_journals: int = int(data["journals"])
                self.num_favourites: int = int(data["favorites"])
                # artist_info
                # contact_info
                # featured_submission
                self._shout_data_getter: Callable[[], Dict] = shout_data_getter
                self._shout_cache: Optional[List[FAKey.FAReader.FAShout]] = None
                # watcher lists
                self.watched_by: List[FAKey.FAReader.FAWatch] = []
                for watch in data["watchers"]["recent"]:
                    watcher_username = watch["link"].split("/")[-2]
                    watcher_name = watch["name"]
                    new_watch = FAKey.FAReader.FAWatch(
                        watcher_username, watcher_name, self.username, self.name
                    )
                    self.watched_by.append(new_watch)
                self.is_watching: List[FAKey.FAReader.FAWatch] = []
                for watch in data["watching"]["recent"]:
                    watched_username = watch["link"].split("/")[-2]
                    watched_name = watch["name"]
                    new_watch = FAKey.FAReader.FAWatch(
                        self.username, self.name, watched_username, watched_name
                    )
                    self.is_watching.append(new_watch)

            @property
            def shouts(self) -> List['FAKey.FAReader.FAShout']:
                if self._shout_cache is None:
                    shout_data = self._shout_data_getter()
                    for shout in shout_data:
                        shout_id = shout["id"].replace("shout-", "")
                        username = shout["profile_name"]
                        name = shout["name"]
                        avatar = shout["avatar"]
                        text = shout["text"]
                        new_shout = FAKey.FAReader.FAShout(
                            shout_id, username, name, avatar, text
                        )
                        self.shouts.append(new_shout)
                return self._shout_cache

        class FAShout:
            def __init__(self, shout_id: str, username: str, name: str, avatar: str, text: str):
                self.shout_id: str = shout_id
                self.username: str = username
                self.name: str = name
                self.avatar: str = avatar
                self.text: str = text

        class FAWatch:
            def __init__(
                    self, watcher_username: str, watcher_name: str, watched_username: str, watched_name: str
            ):
                self.watcher_username: str = watcher_username
                self.watcher_name: str = watcher_name
                self.watched_username: str = watched_username
                self.watched_name: str = watched_name

        class FAUserFavouritesPage:
            def __init__(self, id_list: List[int], username: str):
                self.username: str = username
                self.submission_ids: List[int] = id_list

        class FAViewSubmissionPage:
            def __init__(self, data: Dict, comments_data_getter: Callable[[], Dict], submission_id: str):
                self.submission_id: str = submission_id
                self.title: str = data["title"]
                self.full_image: str = data["download"]
                self.username: str = data["profile_name"]
                self.name: str = data["name"]
                self.avatar_link: str = data["avatar"]
                self.description: str = data["description_body"]
                submission_time_str = data["posted_at"]
                self.submission_time: datetime = dateutil.parser.parse(submission_time_str)
                self.category: str = data["category"]
                self.theme: str = data["theme"]
                self.species: str = data["species"]
                self.gender: str = data["gender"]
                self.num_favourites: int = int(data["favorites"])
                self.num_comments: int = int(data["comments"])
                self.num_views: int = int(data["views"])
                # resolution_x = None
                # resolution_y = None
                self.keywords: List[str] = data["keywords"]
                self.rating: str = data["rating"]
                self._comments_section_getter: Callable[[], Dict] = comments_data_getter
                self._comments_section_cache: Optional[FAKey.FAReader.FACommentsSection] = None

            @property
            def comments_section(self) -> 'FAKey.FAReader.FACommentsSection':
                if self._comments_section_cache is None:
                    comments_data = self._comments_section_getter()
                    self._comments_section_cache = FAKey.FAReader.FACommentsSection(
                        comments_data
                    )
                return self._comments_section_cache

        class FACommentsSection:
            def __init__(self, comments_data: Dict):
                self.top_level_comments: List[FAKey.FAReader.FAComment] = []
                for comment in comments_data:
                    username = comment["profile_name"]
                    name = comment["name"]
                    avatar_link = comment["avatar"]
                    comment_id = comment["id"]
                    posted_datetime = dateutil.parser.parse(comment["posted_at"])
                    text = comment["text"].strip()
                    new_comment = FAKey.FAReader.FAComment(
                        username, name, avatar_link, comment_id, posted_datetime, text
                    )
                    if comment["reply_to"] == "":
                        self.top_level_comments.append(new_comment)
                    else:
                        parent_id = comment["reply_to"]
                        parent_comment = self.get_comment_by_id(parent_id)
                        new_comment.parent = parent_comment
                        parent_comment.reply_comments.append(new_comment)

            def get_comment_by_id(
                    self, comment_id: str, parent_comment: Optional['FAKey.FAReader.FAComment'] = None
            ) -> Optional['FAKey.FAReader.FAComment']:
                if parent_comment is None:
                    for comment in self.top_level_comments:
                        found_comment = self.get_comment_by_id(comment_id, comment)
                        if found_comment is not None:
                            return found_comment
                    return None
                if parent_comment.comment_id == comment_id:
                    return parent_comment
                for comment in parent_comment.reply_comments:
                    found_comment = self.get_comment_by_id(comment_id, comment)
                    if found_comment is not None:
                        return found_comment
                return None

        class FAComment:
            def __init__(
                    self,
                    username: str,
                    name: str,
                    avatar_link: str,
                    comment_id: str,
                    posted_datetime: datetime,
                    text: str,
                    parent_comment: Optional['FAKey.FAReader.FAComment'] = None,
            ):
                self.username: str = username
                self.name: str = name
                self.avatar_link: str = avatar_link
                self.comment_id: str = comment_id
                self.posted_datetime: datetime = posted_datetime
                self.text: str = text
                self.parent_comment: Optional[FAKey.FAReader.FAComment] = parent_comment
                self.reply_comments: List[FAKey.FAReader.FAComment] = []

        class FAViewJournalPage:
            def __init__(self, data: Dict, comments_data_getter: Callable[[], Dict], journal_id: str):
                self.journal_id: str = journal_id
                self.username: str = data["profile_name"]
                self.name: str = data["name"]
                self.avatar_link: Optional[str] = data["avatar"]
                self.title: str = data["title"]
                self.posted_datetime: datetime = dateutil.parser.parse(data["posted_at"])
                self.journal_header: Optional[str] = data["journal_header"]
                self.journal_text: str = data["journal_body"]
                self.journal_footer: Optional[str] = data["journal_footer"]
                self._comments_section_getter: Callable[[], Dict] = comments_data_getter
                self._comments_section_cache: Optional[FAKey.FAReader.FACommentsSection] = None

            @property
            def comments_section(self) -> 'FAKey.FAReader.FACommentsSection':
                if self._comments_section_cache is None:
                    comments_data = self._comments_section_getter()
                    self._comments_section_cache = FAKey.FAReader.FACommentsSection(
                        comments_data
                    )
                return self._comments_section_cache

        class FASearchPage:
            def __init__(self, id_list: List[str], search_term: str):
                self.search_term: str = search_term
                self.id_list: List[str] = id_list
