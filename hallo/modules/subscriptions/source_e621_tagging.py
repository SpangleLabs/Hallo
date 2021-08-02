from typing import List, Optional, Dict, TYPE_CHECKING

from yippi import Post, Rating, YippiClient

import hallo.modules.subscriptions.common_e6_key
import hallo.modules.subscriptions.source_e621
import hallo.modules.subscriptions.stream_source
import hallo.modules.subscriptions.subscription_exception
from hallo.destination import Channel, User, Destination
from hallo.events import EventMessage, EventMessageWithPhoto, EventMenuCallback, MenuButton
from hallo.inc.input_parser import InputParser
from hallo.inc.menus import Menu
from hallo.server import Server

if TYPE_CHECKING:
    from hallo.hallo import Hallo
    import hallo.modules.subscriptions.subscription_check
    import hallo.modules.subscriptions.subscription_repo


def buttons_for_submission(tag_results: Dict[str, bool], page: int = 1) -> List[List[MenuButton]]:
    columns = 2
    rows = 6
    per_page = columns * rows
    tag_names = sorted(tag_results.keys())
    pages = ((len(tag_results) - 1) // per_page) + 1
    tag_names_on_page = tag_names[(page - 1) * per_page: page * per_page]
    buttons = []
    button_row = []
    for tag_name in tag_names_on_page:
        button_emoji = "\u2714" if tag_results[tag_name] else "\u274C"
        button_row.append(MenuButton(f"{button_emoji} {tag_name}", f"tag:{tag_name}"))
        if len(button_row) >= columns:
            buttons.append(button_row)
            button_row = []
    if button_row:
        buttons.append(button_row)
    # Bottom row
    bottom_row = []
    if page > 1:
        bottom_row.append(MenuButton("\u23EE️Back", f"page:{page-1}"))
    bottom_row.append(MenuButton("\U0001F504Refresh", "refresh"))
    bottom_row.append(MenuButton("\U0001F4BESubmit", "submit"))
    if page < pages:
        bottom_row.append(MenuButton("\u23EDNext", f"page:{page+1}"))
    buttons.append(bottom_row)
    return buttons


def text_for_post(item: 'Post', *, prefix: str = None, suffix: str = None) -> str:
    link = f"https://e621.net/posts/{item.id}"
    # Create rating string
    rating_dict = {Rating.EXPLICIT: "(Explicit)", Rating.QUESTIONABLE: "(Questionable)", Rating.SAFE: "(Safe)"}
    rating = rating_dict.get(item.rating, "(Unknown)")
    # Construct output
    output = f'{link} {rating}.'
    if prefix is not None:
        output = prefix + "\n" + output
    if suffix is not None:
        output += "\n" + suffix
    return output


class E621TaggingMenu(Menu):
    type = "e621_tagging"

    def __init__(
            self,
            msg: 'EventMessage',
            user: 'User',
            e6_client: YippiClient,
            post_id: int,
            search: str,
            tag_results: Dict[str, bool],
            page: int = 1
    ) -> None:
        super().__init__(msg)
        self.user = user
        self.e6_client = e6_client
        self.post_id = post_id
        self.search = search
        self.tag_results = tag_results
        self.page = page
        self.clicked = False

    def text_for_post(self, item: 'Post', suffix: str = None) -> str:
        prefix = f'Update on "{self.search}" tagging e621 search.'
        return text_for_post(item, prefix=prefix, suffix=suffix)

    def handle_callback(self, event: 'EventMenuCallback') -> None:
        if self.clicked:
            return
        self.clicked = True
        if event.callback_data.startswith("page:"):
            self.page = int(event.callback_data.split(":")[1])
            return self.update_tag_menu()
        if event.callback_data.startswith("tag:"):
            tag = event.callback_data.split(":", 1)[1]
            self.tag_results[tag] = not self.tag_results[tag]
            return self.update_tag_menu()
        if event.callback_data == "refresh":
            post = self.e6_client.post(self.post_id)
            post_tags = [tag for tag_list in post.tags.values() for tag in tag_list]
            old_tag_results = self.tag_results
            self.tag_results = {tag: tag in post_tags for tag in self.tag_results.keys()}
            if old_tag_results != self.tag_results:
                return self.update_tag_menu()
            else:
                self.clicked = False
                return
        if event.callback_data == "submit":
            post = self.e6_client.post(self.post_id)
            negative_tags = set(tag for tag in self.tag_results.keys() if self.tag_results[tag] is False)
            positive_tags = set(tag for tag in self.tag_results.keys() if self.tag_results[tag] is True)
            current_tags = set(tag for tag_list in post.tags.values() for tag in tag_list)
            new_tags = positive_tags - current_tags
            del_tags = negative_tags.intersection(current_tags)
            menu_buttons = [
                [MenuButton("Save", "save")],
                [MenuButton("Cancel", "cancel")]
            ]
            if not new_tags and not del_tags:
                text = self.text_for_post(post, "This will not make any changes, are you sure?")
                return self.update(text, menu_buttons)
            suffix = ["This will make these changes"]
            if new_tags:
                suffix.append("Add tags: " + ", ".join(new_tags))
            if del_tags:
                suffix.append("Remove tags: " + ", ".join(del_tags))
            text = self.text_for_post(post, "\n".join(suffix))
            return self.update(text, menu_buttons)
        if event.callback_data == "cancel":
            post = self.e6_client.post(self.post_id)
            text = self.text_for_post(post)
            menu_buttons = buttons_for_submission(self.tag_results, self.page)
            return self.update(text, menu_buttons)
        if event.callback_data == "save":
            post = self.e6_client.post(self.post_id)
            negative_tags = set(tag for tag in self.tag_results.keys() if self.tag_results[tag] is False)
            positive_tags = set(tag for tag in self.tag_results.keys() if self.tag_results[tag] is True)
            current_tags = set(tag for tag_list in post.tags.values() for tag in tag_list)
            new_tags = positive_tags - current_tags
            del_tags = negative_tags.intersection(current_tags)
            text = self.text_for_post(post)
            if not new_tags and not del_tags:
                return self.update(text, None)
            new_tag_dict = {
                tag_key: [tag for tag in tag_list if tag not in negative_tags]
                for tag_key, tag_list in post.tags.items()
            }
            new_tag_dict["general"].extend(positive_tags)
            post.tags = new_tag_dict
            has_notes = post._original_data["has_notes"]
            post.update(has_notes=has_notes, reason="Tag change via Hallo bot")
            return self.update(text, None)

    def update_tag_menu(self) -> None:
        buttons = buttons_for_submission(self.tag_results, self.page)
        self.update(None, buttons)

    def update(self, text: Optional[str], menu_buttons: Optional[List[List[MenuButton]]]) -> None:
        new_event = self.msg.create_edit(text=text, menu_buttons=menu_buttons)
        self.msg.server.edit(self.msg, new_event)
        self.msg = new_event
        self.clicked = False

    @classmethod
    def from_json(cls, hallo_obj: 'Hallo', msg: 'EventMessage', data: Dict) -> 'Menu':
        server = hallo_obj.get_server_by_name(msg.server_name)
        user = server.get_user_by_address(data["user_addr"])
        if user is None:
            raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                "Could not find user matching address `{}`".format(data["user_addr"])
            )
        function_dispatcher = hallo_obj.function_dispatcher
        sub_check_class = function_dispatcher.get_function_by_name("check subscription")
        sub_check_obj: hallo.modules.subscriptions.subscription_check.SubscriptionCheck = function_dispatcher.get_function_object(
            sub_check_class
        )
        sub_repo = sub_check_obj.get_sub_repo(hallo_obj)
        e6_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_e6_key.E6KeysCommon)
        e6_client = e6_keys.get_client_by_user(user)
        return cls(
            msg,
            user,
            e6_client,
            data["post_id"],
            data["search"],
            data["tag_results"],
            data["page"]
        )

    def to_json(self) -> Dict:
        return {
            "user_addr": self.user.address,
            "post_id": self.post_id,
            "search": self.search,
            "tag_results": self.tag_results,
            "page": self.page
        }


class E621TaggingSource(hallo.modules.subscriptions.source_e621.E621Source):
    type_name = "e621_tagging"
    type_names: List[str] = ["e621 tagging", "e621 tagging search", "tagging e621"]

    def __init__(
            self,
            search: str,
            e6_client: YippiClient,
            sub_repo: 'hallo.modules.subscriptions.subscription_repo.SubscriptionRepo',
            owner: User,
            tags: List[str],
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(search, e6_client, owner, last_keys)
        self.sub_repo = sub_repo
        self.owner = owner
        self.tags: List[str] = tags

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'E621TaggingSource':
        parsed = InputParser(argument)
        tags_arg = parsed.get_arg_by_names(
            ["tags", "watched_tags", "to_tag", "watched tags", "to tag", "watch"]
        )
        search_arg = parsed.get_arg_by_names(
            [
                "search",
                "query",
                "search_query",
                "search query",
                "subscription",
                "sub",
                "search_term",
                "search term",
            ]
        )
        if tags_arg is not None:
            tags = tags_arg.split()
            if search_arg is not None:
                search = search_arg
            else:
                search = parsed.remaining_text
        else:
            if search_arg is not None:
                search = search_arg
                tags = parsed.remaining_text.split()
            else:
                raise hallo.modules.subscriptions.subscription_exception.SubscriptionException(
                    'You need to specify a search term with search="search term" and '
                    'tags to watch with tags="tags to watch"'
                )
        e6_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_e6_key.E6KeysCommon)
        # Make sure you're not using the default user here
        e6_client = e6_keys.get_client_by_user(user, allow_default=False)
        return cls(search, e6_client, sub_repo, user, tags)

    @property
    def title(self) -> str:
        return f'search for "{self.search}" to apply tags {self.tags}'

    def item_text_prefix(self) -> str:
        return f'Update on "{self.search}" tagging e621 search.'

    def item_to_event(
            self,
            server: Server,
            channel: Optional[Channel],
            user: Optional[User],
            item: Post
    ) -> EventMessage:
        # Check tags
        post_tags = [tag for tag_list in item.tags.values() for tag in tag_list]
        tag_results = {tag: tag in post_tags for tag in self.tags}
        # Construct output
        output = text_for_post(item, prefix=self.item_text_prefix())
        image_url = item.file["url"]
        menu_buttons = buttons_for_submission(tag_results)
        if item.file["ext"] in ["swf", "webm"] or image_url is None:
            msg = EventMessage(server, channel, user, output, inbound=False, menu_buttons=menu_buttons)
        else:
            msg = EventMessageWithPhoto(
                server, channel, user, output, image_url, inbound=False, menu_buttons=menu_buttons
            )
        menu = E621TaggingMenu(msg, self.owner, self.e6_client, item.id, self.search, tag_results)
        self.sub_repo.menu_cache.add_menu(menu)
        return msg

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'E621TaggingSource':
        user_addr = json_data["e621_user_address"]
        user = destination.server.get_user_by_address(user_addr)
        e6_client = hallo.modules.subscriptions.source_e621.e6_client_from_input(user, sub_repo)
        return E621TaggingSource(
            json_data["search"],
            e6_client,
            sub_repo,
            user,
            json_data["tags"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "last_keys": self.last_keys,
            "search": self.search,
            "tags": self.tags,
            "e621_user_address": self.owner.address
        }
