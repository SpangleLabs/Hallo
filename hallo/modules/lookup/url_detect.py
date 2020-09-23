import html
import imghdr
import math
import re
import struct
import urllib.request

from hallo.events import EventMessage
from hallo.function import Function
from hallo.inc.commons import Commons


class UrlDetect(Function):
    """
    URL detection and title printing.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "urldetect"
        # Names which can be used to address the function
        self.names = {"urldetect"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "URL detection."
        self.hallo_obj = None

    def run(self, event):
        return event.create_response("This function does not take input.")

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        # Get hallo object for stuff to use
        self.hallo_obj = hallo_obj
        # Search for a link
        url_regex = re.compile(
            r"\b((https?://|www.)[-A-Z0-9+&?%@#/=~_|$:,.]*[A-Z0-9+&@#/%=~_|$])", re.I
        )
        url_search = url_regex.search(event.text)
        if not url_search:
            return None
        # Get link address
        url_address = url_search.group(1)
        # Add protocol if missing
        if "://" not in url_address:
            url_address = "http://" + url_address
        # Ignore local links.
        if (
            "127.0.0.1" in url_address
            or "192.168." in url_address
            or "10." in url_address
            or "172." in url_address
        ):
            return None
        # Get page info
        page_request = urllib.request.Request(url_address)
        page_request.add_header(
            "User-Agent",
            "Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0",
        )
        page_opener = urllib.request.build_opener()
        page_info = str(page_opener.open(page_request).info())
        if "Content-Type:" in page_info:
            page_type = page_info.split()[page_info.split().index("Content-Type:") + 1]
        else:
            page_type = ""
        # Get the website name
        url_site = Commons.get_domain_name(url_address).lower()
        # Get response if link is an image
        if "image" in page_type:
            return event.create_response(
                self.url_image(url_address, page_opener, page_request, page_type)
            )
        # Get a response depending on the website
        output = None
        site_readers = {
            "ebay": self.site_ebay,
            "imdb": self.site_imdb,
            "imgur": self.site_imgur,
            "speedtest": self.site_speedtest,
            "youtube": self.site_youtube,
            "youtu": self.site_youtube,
        }
        if url_site in site_readers:
            output = site_readers[url_site](url_address, page_opener, page_request)
        # If other url, return generic URL response
        if output is None:
            output = self.url_generic(url_address, page_opener, page_request)
        return None if output is None else event.create_response(output)

    def url_image(self, url_address, page_opener, page_request, page_type):
        """Handling direct image links"""
        # Get the website name
        url_site = Commons.get_domain_name(url_address).lower()
        # If website name is speedtest or imgur, hand over to those handlers
        if url_site == "speedtest":
            return self.site_speedtest(url_address, page_opener, page_type)
        if url_site == "imgur":
            return self.site_imgur(url_address, page_opener, page_type)
        # Image handling
        image_data = page_opener.open(page_request).read()
        image_width, image_height = self.get_image_size(image_data)
        image_size = len(image_data)
        image_size_str = self.file_size_to_string(image_size)
        return "Image: {} ({}px by {}px) {}.".format(
            page_type, image_width, image_height, image_size_str
        )

    def url_generic(self, url_address, page_opener, page_request):
        """Handling for generic links not caught by any other url handling function."""
        page_code = page_opener.open(page_request).read(4096).decode("utf-8", "ignore")
        if page_code.count("</title>") == 0:
            return None
        title_search = re.search(r"<title[^>]*>([^<]*)</title>", page_code, re.I)
        if title_search is None:
            return None
        title_text = title_search.group(1)
        title_clean = html.unescape(title_text).replace("\n", "").strip()
        if title_clean != "":
            return "URL title: {}".format(title_clean.replace("\n", ""))
        return None

    def site_ebay(self, url_address, page_opener, page_request):
        """Handling for ebay links"""
        # Get the ebay item id
        item_id = url_address.split("/")[-1]
        api_key = self.hallo_obj.get_api_key("ebay")
        if api_key is None:
            return None
        # Get API response
        api_url = (
            "http://open.api.ebay.com/shopping?callname=GetSingleItem&responseencoding=JSON&appid={}"
            "&siteid=0&version=515&ItemID={}&IncludeSelector=Details".format(
                api_key, item_id
            )
        )
        api_dict = Commons.load_url_json(api_url)
        # Get item data from api response
        item_title = api_dict["Item"]["Title"]
        item_price = "{} {}".format(
            api_dict["Item"]["CurrentPrice"]["Value"],
            api_dict["Item"]["CurrentPrice"]["CurrencyID"],
        )
        item_end_time = api_dict["Item"]["EndTime"][:19].replace("T", " ")
        # Start building output
        output = "eBay> Title: {} | Price: {} | ".format(item_title, item_price)
        # Check listing type
        if api_dict["Item"]["ListingType"] == "Chinese":
            # Listing type: bidding
            item_bid_count = str(api_dict["Item"]["BidCount"])
            if item_bid_count == "1":
                output += "Auction, {} bid".format(item_bid_count)
            else:
                output += "Auction, {} bids".format(item_bid_count)
        elif api_dict["Item"]["ListingType"] == "FixedPriceItem":
            # Listing type: buy it now
            output += "Buy it now | "
        output += "Ends: {}".format(item_end_time)
        return output

    def site_imdb(self, url_address, page_opener, page_request):
        """Handling for imdb links"""
        # If URL isn't to an imdb title, just do normal url handling.
        if "imdb.com/title" not in url_address:
            return self.url_generic(url_address, page_opener, page_request)
        # Get the imdb movie ID
        movie_id_search = re.search("title/(tt[0-9]*)", url_address)
        if movie_id_search is None:
            return self.url_generic(url_address, page_opener, page_request)
        movie_id = movie_id_search.group(1)
        # Download API response
        api_url = "https://www.omdbapi.com/?i={}".format(movie_id)
        api_dict = Commons.load_url_json(api_url)
        # Get movie information from API response
        movie_title = api_dict["Title"]
        movie_year = api_dict["Year"]
        movie_genre = api_dict["Genre"]
        movie_rating = api_dict["imdbRating"]
        movie_votes = api_dict["imdbVotes"]
        # Construct output
        output = "IMDB> Title: {} ({}) | Rating {}/10, {} votes. | Genres: {}.".format(
            movie_title, movie_year, movie_rating, movie_votes, movie_genre
        )
        return output

    def site_imgur(self, url_address, page_opener, page_request):
        """Handling imgur links"""
        # Hand off imgur album links to a different handler function.
        if "/a/" in url_address:
            return self.site_imgur_album(url_address, page_opener, page_request)
        # Handle individual imgur image links
        imgur_id = url_address.split("/")[-1].split(".")[0]
        api_url = "https://api.imgur.com/3/image/{}".format(imgur_id)
        # Load API response (in json) using Client-ID.
        api_key = self.hallo_obj.get_api_key("imgur")
        if api_key is None:
            return None
        api_dict = Commons.load_url_json(api_url, [["Authorization", api_key]])
        # Get title, width, height, size, and view count from API data
        image_title = str(api_dict["data"]["title"])
        image_width = str(api_dict["data"]["width"])
        image_height = str(api_dict["data"]["height"])
        image_size = int(api_dict["data"]["size"])
        image_size_string = self.file_size_to_string(image_size)
        image_views = api_dict["data"]["views"]
        # Create output and return
        output = "Imgur> Title: {} | Size: {}x{} | Filesize: {} | Views: {:,}.".format(
            image_title, image_width, image_height, image_size_string, image_views
        )
        return output

    def site_imgur_album(self, url_address, page_opener, page_request):
        """Handling imgur albums"""
        imgur_id = url_address.split("/")[-1].split("#")[0]
        api_url = "https://api.imgur.com/3/album/{}".format(imgur_id)
        # Load API response (in json) using Client-ID.
        api_key = self.hallo_obj.get_api_key("imgur")
        if api_key is None:
            return None
        api_dict = Commons.load_url_json(api_url, [["Authorization", api_key]])
        # Get album title and view count from API data
        album_title = api_dict["data"]["title"]
        album_views = api_dict["data"]["views"]
        # Start on output
        output = "Imgur album> Album title: {} | Gallery views: {:,} | ".format(
            album_title, album_views
        )
        if "section" in api_dict["data"]:
            album_section = api_dict["data"]["section"]
            output += "Section: {} | ".format(album_section)
        album_count = api_dict["data"]["images_count"]
        # If an image was specified, show some information about that specific image
        if "#" in url_address:
            image_number = int(url_address.split("#")[-1])
            image_width = api_dict["data"]["images"][image_number]["width"]
            image_height = api_dict["data"]["images"][image_number]["height"]
            image_size = int(api_dict["data"]["images"][image_number]["size"])
            image_size_string = self.file_size_to_string(image_size)
            output += "Image {} of {} | Current image: {}x{}, {}.".format(
                image_number + 1,
                album_count,
                image_width,
                image_height,
                image_size_string,
            )
            return output
        output += "{} images.".format(album_count)
        return output

    def site_speedtest(self, url_address, page_opener, page_request):
        """Handling speedtest links"""
        if url_address[-4:] == ".png":
            url_number = url_address[32:-4]
            url_address = "https://www.speedtest.net/my-result/".format(url_number)
            page_request = urllib.request.Request(url_address)
            page_request.add_header(
                "User-Agent",
                "Mozilla/5.0 (X11; Linux i686; rv:23.0) Gecko/20100101 Firefox/23.0",
            )
            page_opener = urllib.request.build_opener()
        page_code = page_opener.open(page_request).read().decode("utf-8")
        page_code = re.sub(r"\s+", "", page_code)
        download = re.search("<h3>Download</h3><p>([0-9.]*)", page_code).group(1)
        upload = re.search("<h3>Upload</h3><p>([0-9.]*)", page_code).group(1)
        ping = re.search("<h3>Ping</h3><p>([0-9]*)", page_code).group(1)
        return "Speedtest> Download: {}Mb/s | Upload: {}Mb/s | Ping: {}ms".format(
            download, upload, ping
        )

    def site_youtube(self, url_address, page_opener, page_request):
        """Handling for youtube links"""
        # Find video id
        if "youtu.be" in url_address:
            video_id = url_address.split("/")[-1].split("?")[0]
        else:
            video_id = url_address.split("/")[-1].split("=")[1].split("&")[0]
        # Find API url
        api_key = self.hallo_obj.get_api_key("youtube")
        if api_key is None:
            return None
        api_url = (
            "https://www.googleapis.com/youtube/v3/videos?id={}"
            "&part=snippet,contentDetails,statistics&key={}".format(video_id, api_key)
        )
        # Load API response (in json).
        api_dict = Commons.load_url_json(api_url)
        # Get video data from API response.
        video_title = api_dict["items"][0]["snippet"]["title"]
        video_duration = api_dict["items"][0]["contentDetails"]["duration"][2:].lower()
        video_views = api_dict["items"][0]["statistics"]["viewCount"]
        # Create output
        output = "Youtube video> Title: {} | Length {} | Views: {}.".format(
            video_title, video_duration, video_views
        )
        return output

    def get_image_size(self, image_data):
        """
        Determine the image type of fhandle and return its size.
        from draco
        """
        # This function is from here:
        # https://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
        image_head = image_data[:24]
        if len(image_head) != 24:
            return
        if imghdr.what(None, image_data) == "png":
            check = struct.unpack(">i", image_head[4:8])[0]
            if check != 0x0D0A1A0A:
                return
            width, height = struct.unpack(">ii", image_head[16:24])
        elif imghdr.what(None, image_data) == "gif":
            width, height = struct.unpack("<HH", image_head[6:10])
        elif imghdr.what(None, image_data) == "jpeg":
            # try:
            byte_offset = 0
            size = 2
            ftype = 0
            while not 0xC0 <= ftype <= 0xCF:
                byte_offset += size
                byte = image_data[byte_offset]
                byte_offset += 1
                while byte == 0xFF:
                    byte = image_data[byte_offset]
                    byte_offset += 1
                ftype = byte
                size = (
                    struct.unpack(">H", image_data[byte_offset: byte_offset + 2])[0]
                    - 2
                )
                byte_offset += 2
            # We are at a SOFn block
            byte_offset += 1  # Skip `precision' byte.
            height, width = struct.unpack(
                ">HH", image_data[byte_offset: byte_offset + 4]
            )
            byte_offset += 4
        # except Exception:  # IGNORE:W0703
        # return
        else:
            return
        return width, height

    def file_size_to_string(self, size):
        if size < 2048:
            size_string = "{}Bytes".format(size)
        elif size < (2048 * 1024):
            size_string = "{}KiB".format(math.floor(float(size) / 10.24) / 100)
        elif size < (2048 * 1024 * 1024):
            size_string = "{}MiB".format(math.floor(float(size) / (1024 * 10.24)) / 100)
        else:
            size_string = "{}GiB".format(
                math.floor(float(size) / (1024 * 1024 * 10.24)) / 100
            )
        return size_string
