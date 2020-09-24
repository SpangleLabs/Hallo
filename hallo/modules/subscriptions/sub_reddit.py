import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.hallo import Hallo
from hallo.inc.commons import Commons
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class RedditSub(hallo.modules.subscriptions.subscriptions.Subscription[Dict]):
    names: List[str] = ["reddit", "subreddit"]
    type_name: str = "subreddit"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        subreddit: str,
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        latest_ids: Optional[List[str]] = None,
    ):
        super().__init__(server, destination, last_check, update_frequency)
        self.subreddit: str = subreddit
        if latest_ids is None:
            latest_ids = []
        self.latest_ids: List[str] = latest_ids

    @staticmethod
    def create_from_input(
            input_evt: EventMessage, sub_repo
    ) -> 'RedditSub':
        # Get event data
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        clean_text = input_evt.command_args.strip().lower()
        text_split = clean_text.split()
        # Subreddit regex
        sub_regex = re.compile(r"r/([^\s]*)/?")
        if len(text_split) == 1:
            sub_name = (
                clean_text
                if sub_regex.search(clean_text) is None
                else sub_regex.search(clean_text).group(1)
            )
            reddit_sub = RedditSub(server, destination, sub_name)
            reddit_sub.check()
            return reddit_sub
        if len(text_split) > 2:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Too many arguments. Please give a subreddit, and optionally, a check period."
            )
        try:
            search_delta = isodate.parse_duration(text_split[0])
            subreddit = text_split[1]
        except isodate.isoerror.ISO8601Error:
            subreddit = text_split[0]
            search_delta = isodate.parse_duration(text_split[1])
        sub_name = (
            clean_text
            if sub_regex.search(subreddit) is None
            else sub_regex.search(subreddit).group(1)
        )
        reddit_sub = RedditSub(
            server, destination, sub_name, update_frequency=search_delta
        )
        reddit_sub.check()
        return reddit_sub

    def matches_name(self, name_clean: str) -> bool:
        return (
            self.subreddit == name_clean or "r/{}".format(self.subreddit) in name_clean
        )

    def get_name(self) -> str:
        return "/r/{}".format(self.subreddit)

    def check(self, *, ignore_result: bool = False) -> List[Dict]:
        url = "https://www.reddit.com/r/{}/new.json".format(self.subreddit)
        results = Commons.load_url_json(url)
        return_list = []
        new_last_ten = []
        for result in results["data"]["children"]:
            result_id = result["data"]["name"]
            # If post hasn't been seen in the latest ten, add it to returned list.
            if result_id not in self.latest_ids:
                new_last_ten.append(result_id)
                return_list.append(result)
            else:
                break
        self.latest_ids = (self.latest_ids + new_last_ten[::-1])[-10:]
        # Update check time
        self.last_check = datetime.now()
        return return_list

    def format_item(self, item: Dict) -> EventMessage:
        # Event destination
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        # Item data
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
                "Update on /r/{}/ subreddit. "
                '<a href="{}">{}</a> by "<a href="{}">u/{}</a>"\n'
                '<a href="{}">direct image</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    url,
                )
            )
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, url, inbound=False
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
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'
                '<a href="{}">gfycat</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    url,
                )
            )
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, direct_url, inbound=False
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
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'
                '<a href="{}">vreddit</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    direct_url,
                )
            )
            output_evt = EventMessageWithPhoto(
                self.server, channel, user, output, direct_url, inbound=False
            )
            output_evt.formatting = EventMessage.Formatting.HTML
            return output_evt
        # Make output message if the link isn't direct to a media file
        if item["data"]["selftext"] != "":
            output = (
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                )
            )
        else:
            output = (
                "Update on /r/{}/ subreddit. "
                '"<a href="{}">{}</a>" by <a href="{}">u/{}</a>\n'
                '<a href="{}">{}</a>'.format(
                    Commons.html_escape(self.subreddit),
                    link,
                    Commons.html_escape(title),
                    author_link,
                    Commons.html_escape(author),
                    url,
                    Commons.html_escape(url),
                )
            )
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        output_evt.formatting = EventMessage.Formatting.HTML
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["subreddit"] = self.subreddit
        json_obj["latest_ids"] = []
        for latest_id in self.latest_ids:
            json_obj["latest_ids"].append(latest_id)
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'RedditSub':
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
        # Load last items
        latest_ids = []
        for latest_id in json_obj["latest_ids"]:
            latest_ids.append(latest_id)
        # Load search
        subreddit = json_obj["subreddit"]
        new_sub = RedditSub(
            server, destination, subreddit, last_check, update_frequency, latest_ids
        )
        new_sub.last_update = last_update
        return new_sub
