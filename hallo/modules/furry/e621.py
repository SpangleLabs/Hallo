from hallo.function import Function
from hallo.inc.commons import Commons


class E621(Function):
    """
    Returns a random image from e621
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "e621"
        # Names which can be used to address the function
        self.names = {"e621"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random e621 result using the search you specify. Format: e621 <tags>"

    def run(self, event):
        search_result = self.get_random_link_result(event.command_args)
        if search_result is None:
            return event.create_response("No results.")
        else:
            link = "https://e621.net/posts/{}".format(search_result["id"])
            if search_result["post"]["rating"] == "e":
                rating = "(Explicit)"
            elif search_result["post"]["rating"] == "q":
                rating = "(Questionable)"
            elif search_result["post"]["rating"] == "s":
                rating = "(Safe)"
            else:
                rating = "(Unknown)"
            line_response = event.command_args.strip()
            return event.create_response(
                'e621 search for "{}" returned: {} {}'.format(
                    line_response, link, rating
                )
            )

    def get_random_link_result(self, search):
        """Gets a random link from the e621 api."""
        line_clean = search.replace(" ", "%20")
        url = "https://e621.net/posts.json?tags=order:random%20score:%3E0%20{}%20&limit=1".format(
            line_clean
        )
        return_list = Commons.load_url_json(url)
        if len(return_list["posts"]) == 0:
            return None
        else:
            result = return_list["posts"][0]
            return result