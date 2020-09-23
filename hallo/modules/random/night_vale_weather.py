import urllib.parse

from hallo.events import EventMessage
from hallo.function import Function
from hallo.inc.commons import Commons


class NightValeWeather(Function):
    """
    Returns the current weather, in the style of "welcome to night vale"
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "nightvale weather"
        # Names which can be used to address the function
        self.names = {"night vale weather", "nightvale weather", "nightvale"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Returns the current weather in the style of the podcast 'Welcome to Night Vale' "
            "Format: nightvale weather"
        )
        self.hallo_obj = None

    def run(self, event):
        # Get hallo object
        self.hallo_obj = event.server.hallo
        # Get playlist data from youtube api
        try:
            playlist_data = self.get_youtube_playlist(
                "PL1-VZZ6QMhCdx8eC4R3VlCmSn1Kq2QWGP"
            )
        except Exception as e:
            return event.create_response("No api key loaded for youtube.")
        # Select a video from the playlist
        rand_video = Commons.get_random_choice(playlist_data)[0]
        # Return video information
        return event.create_response(
            "And now, the weather: https://youtu.be/{} {}".format(
                rand_video["video_id"], rand_video["title"]
            )
        )

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        line_clean = event.text.lower().strip()
        # Get hallo's current name
        hallo_name = event.server.get_nick().lower()
        # Check if message matches specified patterns
        if hallo_name + " with the weather" in line_clean:
            # Return response
            return self.run(event)

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def get_youtube_playlist(self, playlist_id, page_token=None):
        """Returns a list of video information for a youtube playlist."""
        list_videos = []
        # Get API key
        api_key = self.hallo_obj.get_api_key("youtube")
        if api_key is None:
            raise Exception("Youtube API key missing.")
        # Find API url
        api_fields = "nextPageToken,items(snippet/title,snippet/resourceId/videoId)"
        api_url = (
            "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={}"
            "&fields={}&key={}".format(
                playlist_id, urllib.parse.quote(api_fields), api_key
            )
        )
        if page_token is not None:
            api_url += "&pageToken={}".format(page_token)
        # Load API response (in json).
        api_dict = Commons.load_url_json(api_url)
        for api_item in api_dict["items"]:
            new_video = {
                "title": api_item["snippet"]["title"],
                "video_id": api_item["snippet"]["resourceId"]["videoId"],
            }
            list_videos.append(new_video)
        # Check if there's another page to add
        if "nextPageToken" in api_dict:
            list_videos.extend(
                self.get_youtube_playlist(playlist_id, api_dict["nextPageToken"])
            )
        # Return list
        return list_videos
