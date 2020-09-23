from hallo.function import Function
from hallo.inc.commons import Commons


class UrbanDictionary(Function):
    """
    Urban Dictionary lookup function.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "urban dictionary"
        # Names which can be used to address the function
        self.names = {"urban dictionary", "urban", "urbandictionary", "ud"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Gives the top urban dictionary definition for a word. Format: urban dictionary <word>"

    def run(self, event):
        url_line = event.command_args.replace(" ", "+").lower()
        url = "https://api.urbandictionary.com/v0/define?term={}".format(url_line)
        urban_dict = Commons.load_url_json(url)
        if len(urban_dict["list"]) > 0:
            definition = (
                urban_dict["list"][0]["definition"].replace("\r", "").replace("\n", "")
            )
            return event.create_response(definition)
        else:
            return event.create_response(
                "Sorry, I cannot find a definition for {}.".format(event.command_args)
            )