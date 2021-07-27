from hallo.function import Function


class Butts(Function):
    """
    Returns a random butt from e621
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "butts"
        # Names which can be used to address the function
        self.names = {"random butt", "butts", "butts!", "butts."}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            'Returns a random image from e621 for the search "butt". Format: butts'
        )

    def run(self, event):
        function_dispatcher = event.server.hallo.function_dispatcher
        e621_class = function_dispatcher.get_function_by_name("e621")
        e621_obj = function_dispatcher.get_function_object(e621_class)  # type: E621
        search_result = e621_obj.get_random_link_result("butt")
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
            return event.create_response(
                'e621 search for "butt" returned: {} {}'.format(link, rating)
            )