import re
from typing import Dict, List, Optional

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.commons import Commons
from hallo.modules.new_subscriptions.stream_source import StreamSource, Key
from hallo.server import Server


class RedditSource(StreamSource[Dict]):
    names: List[str] = ["reddit", "subreddit"]
    type_name: str = "subreddit"

    def __init__(self, subreddit: str, last_keys: Optional[List[Key]] = None):
        super().__init__(last_keys)
        self.subreddit = subreddit

    def current_state(self) -> List[Dict]:
        url = "https://www.reddit.com/r/{}/new.json".format(self.subreddit)
        results = Commons.load_url_json(url)
        return results["data"]["children"]

    def item_to_key(self, item: Dict) -> Key:
        return item["data"]["name"]

    def item_to_event(
            self, server: Server, channel: Optional[Channel], user: Optional[User],
            item: Dict
    ) -> EventMessage:
        link = "https://reddit.com/r/{}/comments/{}/".format(
            self.subreddit, item["data"]["id"]
        )
        title = item["data"]["title"]
        author = item["data"]["author"]
        author_link = "https://www.reddit.com/user/{}".format(author)
        url = item["data"]["url"]
        # Check if link is direct to a media file, if so, add photo to output message
        file_extension = url.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "bmp", "gif", "mp4", "gifv"]:
            if file_extension == "gifv":
                url = url[:-4] + "mp4"
            # Make output message
            output = (
                f"Update on /r/{Commons.html_escape(self.subreddit)}/ subreddit. "
                f'<a href="{link}">{Commons.html_escape(title)}</a> by '
                f'"<a href="{author_link}">u/{Commons.html_escape(author)}</a>"'
            )
            output_evt = EventMessageWithPhoto(
                server, channel, user, output, url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Handle gfycat links as photos
        gfycat_regex = re.compile(
            r"(?:https?://)?(?:www\.)?gfycat\.com/([a-z]+)", re.IGNORECASE
        )
        gfycat_match = gfycat_regex.match(url)
        if gfycat_match is not None:
            direct_url = "https://giant.gfycat.com/{}.mp4".format(gfycat_match.group(1))
            # Make output message
            output = (
                f"Update on /r/{Commons.html_escape(self.subreddit)}/ subreddit. "
                f'"<a href="{link}">{Commons.html_escape(title)}</a>" by '
                f'"<a href="{author_link}">u/{Commons.html_escape(author)}</a>"'
            )
            output_evt = EventMessageWithPhoto(
                server, channel, user, output, direct_url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Handle reddit video links
        vreddit_regex = re.compile(r"https?://v.redd.it/[a-z0-9]+")
        vreddit_match = vreddit_regex.match(url)
        if vreddit_match is not None:
            if item["data"]["secure_media"] is None:
                direct_url = item["data"]["crosspost_parent_list"][0]["secure_media"][
                    "reddit_video"
                ]["fallback_url"]
            else:
                direct_url = item["data"]["secure_media"]["reddit_video"][
                    "fallback_url"
                ]
            # Make output message
            output = (
                f"Update on /r/{Commons.html_escape(self.subreddit)}/ subreddit. "
                f'"<a href="{link}">{link}</a>" by '
                f'"<a href="{author_link}">u/{Commons.html_escape(author)}</a>"'
            )
            output_evt = EventMessageWithPhoto(
                server, channel, user, output, direct_url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Make output message if the link isn't direct to a media file
        if item["data"]["selftext"] != "":
            output = (
                f"Update on /r/{Commons.html_escape(self.subreddit)}/ subreddit. "
                f'"<a href="{link}">{Commons.html_escape(title)}</a>" by '
                f'"<a href="{author_link}">u/{Commons.html_escape(author)}</a>"'
            )
        else:
            output = (
                f"Update on /r/{Commons.html_escape(self.subreddit)}/ subreddit. "
                f'"<a href="{link}">{Commons.html_escape(title)}</a>" by '
                f'"<a href="{author_link}">u/{Commons.html_escape(author)}</a>"\n'
                f'<a href="{url}">{Commons.html_escape(url)}</a>'
            )
        output_evt = EventMessage(server, channel, user, output, inbound=False)
        output_evt.formatting = EventMessage.Formatting.HTML
        return output_evt

    def matches_name(self, name_clean: str) -> bool:
        return (
                self.subreddit == name_clean or f"r/{self.subreddit}" in name_clean
        )

    @property
    def title(self) -> str:
        return f"/r/{self.subreddit}"

    @classmethod
    def from_input(cls, argument: str, user: User, sub_repo) -> 'RedditSource':
        clean_text = argument.strip().lower()
        sub_regex = re.compile(r"r/([^\s]*)/?")
        sub_name = (
            clean_text
            if sub_regex.search(clean_text) is None
            else sub_regex.search(clean_text).group(1)
        )
        return RedditSource(sub_name)

    @classmethod
    def from_json(cls, json_data: Dict, destination: Destination, sub_repo) -> 'RedditSource':
        return RedditSource(
            json_data["subreddit"],
            json_data["last_keys"]
        )

    def to_json(self) -> Dict:
        return {
            "type": self.type_name,
            "subreddit": self.subreddit,
            "last_keys": self.last_keys
        }
