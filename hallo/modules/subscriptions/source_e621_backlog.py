from typing import List, Optional, Dict, TYPE_CHECKING

from yippi import Post, YippiClient

import hallo.modules.subscriptions.common_e6_key
import hallo.modules.subscriptions.source_e621
import hallo.modules.subscriptions.source_e621_tagging
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.subscription_exception
from hallo.destination import User, Destination
from hallo.events import EventMessage
from hallo.inc.commons import Commons
import hallo.modules.subscriptions.source

if TYPE_CHECKING:
    from hallo.hallo import Hallo
    import hallo.modules.subscriptions.subscription_check
    import hallo.modules.subscriptions.subscription_repo


class E621BacklogTaggingMenu(hallo.modules.subscriptions.source_e621_tagging.E621TaggingMenu):
    type = "e621_backlog_tagging"

    def text_for_post(self, item: 'Post', suffix: str = None) -> str:
        prefix = f'Another item for "{self.search}" backlog e621 tagging.'
        return hallo.modules.subscriptions.source_e621_tagging.text_for_post(item, prefix=prefix, suffix=suffix)


class E621BacklogTaggingSource(hallo.modules.subscriptions.source_e621_tagging.E621TaggingSource):
    type_name = "e621_backlog_tagging"
    type_names: List[str] = [
        "e621 backlog tagging",
        "e621 backlog tagging search",
        "tagging e621 backlog",
        "e621 backlog",
        "e621 backlog tag",
    ]

    def __init__(
            self,
            search: str,
            e6_client: YippiClient,
            sub_repo: 'hallo.modules.subscriptions.subscription_repo.SubscriptionRepo',
            owner: User,
            tags: List[str],
            start_id: Optional[int] = None,
            current_batch_ids: Optional[List[int]] = None,
            sent_ids: Optional[List[int]] = None,
            batch_size: int = 5,
            remaining_count: Optional[int] = None,
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(search, e6_client, sub_repo, owner, tags, last_keys)
        self.start_id = start_id
        self.current_batch_ids = current_batch_ids or []
        self.sent_ids = sent_ids or []
        self.batch_size = batch_size
        self.remaining_count = remaining_count

    @property
    def title(self) -> str:
        return f'search through backlog of "{self.search}" to apply tags {self.tags}. ' \
               f'Done {len(self.sent_ids)}, about {self.get_remaining_count()} remaining.'

    def item_text_prefix(self) -> str:
        return f'New backlog tagging item on "{self.search}" e621 search.'

    def current_state(self) -> List[Post]:
        if self.start_id is None:
            self.start_id = self.find_start_id()
            self.generate_next_batch()
            return []
        post_data = []
        for post_id in self.current_batch_ids:
            post = self.e6_client.post(post_id)
            post_data.append(post)
        return post_data

    def find_start_id(self):
        search = f"{self.search} order:-id"
        posts = self.e6_client.posts(search)
        if not posts:
            raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                "There are no results for this search."
            )
        return posts[0].id

    def generate_next_batch(self):
        # Update sent IDs
        self.sent_ids += self.current_batch_ids
        # Build search query
        search = f"{self.search} order:-id id:<={self.start_id}"
        # Set up paging
        new_posts = []
        page = 1
        while len(new_posts) < self.batch_size:
            page_posts = self.e6_client.posts(search, page=page)
            incomplete_posts = list(filter(lambda p: p.id not in self.sent_ids, page_posts))
            new_posts += incomplete_posts
            page += 1
        self.current_batch_ids = [p.id for p in new_posts[:self.batch_size]]
        if self.remaining_count is not None:
            self.remaining_count -= len(self.current_batch_ids)

    def get_remaining_count(self):
        if self.remaining_count is not None:
            return self.remaining_count
        smallest_id = min(self.sent_ids)
        search = f"{self.search} id:<={smallest_id}"
        count_posts = 0
        page = 1
        while True:
            page_posts = len(self.e6_client.posts(search, page=page))
            if page_posts:
                count_posts += page_posts
                page += 1
            else:
                break
        self.remaining_count = count_posts
        return count_posts

    def passive_run(self, event: EventMessage, hallo_obj: 'Hallo') -> bool:
        text_split = event.text.strip().split()
        if not text_split:
            return False
        if text_split[0].lower() not in ["more", "another"]:
            return False
        count = self.batch_size
        if len(text_split) > 1:
            name_split = text_split[1:]
            if Commons.is_int_string(name_split[0]):
                count = int(name_split[0])
                name_split = name_split[1:]
            elif Commons.is_int_string(name_split[-1]):
                count = int(name_split[-1])
                name_split = name_split[:-1]
            if name_split:
                sub_name = " ".join(name_split).lower()
                if not self.matches_name(sub_name):
                    return False
        # Post up to `count` new posts.
        self.batch_size = count
        self.generate_next_batch()
        remaining_count = self.get_remaining_count()
        resp = event.create_response(
            f"Okay, will send {self.batch_size} more updates. There are about {remaining_count} posts left."
        )
        event.reply(resp)
        return True

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'E621BacklogTaggingSource':
        user_addr = json_data["e621_user_address"]
        user = destination.server.get_user_by_address(user_addr)
        e6_client = hallo.modules.subscriptions.source_e621.e6_client_from_input(user, sub_repo)
        return cls(
            json_data["search"],
            e6_client,
            sub_repo,
            user,
            json_data["tags"],
            json_data.get("start_id"),
            json_data["current_batch_ids"],
            json_data["sent_ids"],
            json_data["batch_size"],
            json_data.get("remaining_count"),
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "search": self.search,
            "tags": self.tags,
            "e621_user_address": self.owner.address,
            "start_id": self.start_id,
            "current_batch_ids": self.current_batch_ids,
            "sent_ids": self.sent_ids,
            "batch_size": self.batch_size,
            "remaining_count": self.remaining_count
        }
