from hallo.function import Function
from hallo.inc.commons import Commons


class CatGif(Function):
    """
    Returns a random cat gif
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "catgif"
        # Names which can be used to address the function
        self.names = {
            "catgif",
            "cat gif",
            "random cat",
            "random cat gif",
            "random catgif",
            "cat.gif",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random cat gif Format: cat gif"

    def run(self, event):
        api_key = event.server.hallo.get_api_key("thecatapi")
        if api_key is None:
            return event.create_response("No API key loaded for cat api.")
        url = "http://thecatapi.com/api/images/get?format=json&api_key={}&type=gif".format(
            api_key
        )
        cat_obj = Commons.load_url_json(url)[0]
        cat_url = cat_obj["url"]
        return event.create_response(cat_url)