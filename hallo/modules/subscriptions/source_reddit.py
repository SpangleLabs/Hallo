import logging
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from hallo.destination import Destination, User, Channel
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.inc.commons import Commons
import hallo.modules.subscriptions.stream_source
from hallo.server import Server

logger = logging.getLogger(__name__)

def _direct_url_gfycat(url: str) -> Optional[str]:
    gfycat_regex = re.compile(
        r"(?:https?://)?(?:www\.)?gfycat\.com/([a-z]+)", re.IGNORECASE
    )
    gfycat_match = gfycat_regex.match(url)
    if gfycat_match is None:
        return None
    return "https://giant.gfycat.com/{}.mp4".format(gfycat_match.group(1))


def _direct_url_vreddit(url: str, item: Dict) -> Optional[str]:
    vreddit_regex = re.compile(r"https?://v.redd.it/[a-z0-9]+")
    vreddit_match = vreddit_regex.match(url)
    if vreddit_match is None:
        return None
    try:
        if item["data"]["secure_media"] is None:
            return item["data"]["crosspost_parent_list"][0]["secure_media"]["reddit_video"]["fallback_url"]
        return item["data"]["secure_media"]["reddit_video"]["fallback_url"]
    except KeyError as e:
        logger.warning("KeyError in vreddit parsing: ", exc_info=e)
        return None


def _direct_url_red(url: str) -> Optional[str]:
    redgifs_regex = re.compile(r"(?:https?://)?(?:www\.)?redgifs\.com/watch/([a-z]+)", re.IGNORECASE)
    redgifs_match = redgifs_regex.match(url)
    if redgifs_match is None:
        return None
    page_source = Commons.load_url_string(redgifs_match.group(0))
    page_soup = BeautifulSoup(page_source, "html.parser")
    sources = page_soup.select(".video-player-wrapper video source")
    if not sources:
        return None
    best_sources = [
        source["src"]
        for source
        in sources
        if source["type"] == "video/mp4" and not source["src"].endswith("-mobile.mp4")
    ]
    if best_sources:
        return best_sources[0]
    mp4_sources = [source["src"] for source in sources if source["type"] == "video/mp4"]
    if mp4_sources:
        return mp4_sources[0]
    return sources[0]["src"]


def _get_direct_url(url: str, item: Dict) -> Optional[str]:
    gfycat_direct = _direct_url_gfycat(url)
    if gfycat_direct is not None:
        return gfycat_direct
    vreddit_direct = _direct_url_vreddit(url, item)
    if vreddit_direct is not None:
        return vreddit_direct
    redgif_direct = _direct_url_red(url)
    if redgif_direct is not None:
        return redgif_direct
    return None


class RedditSource(hallo.modules.subscriptions.stream_source.StreamSource[Dict]):
    type_name: str = "subreddit"
    type_names: List[str] = ["reddit", "subreddit"]

    def __init__(
            self, subreddit: str,
            last_keys: Optional[List[hallo.modules.subscriptions.stream_source.Key]] = None
    ):
        super().__init__(last_keys)
        self.subreddit = subreddit

    def current_state(self) -> List[Dict]:
        url = "https://www.reddit.com/r/{}/new.json".format(self.subreddit)
        results = Commons.load_url_json(url)
        return results["data"]["children"]

    def item_to_key(self, item: Dict) -> hallo.modules.subscriptions.stream_source.Key:
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
        # Handle external sites we can embed
        direct_url = _get_direct_url(url, item)
        # If a direct url was found, send that
        if direct_url is not None:
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


if __name__ == "__main__":
    s = RedditSource("happycowgifs")
    state = s.current_state()
    for item in state:
        s.item_to_event(None, None, None, item)
