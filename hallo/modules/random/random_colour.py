from hallo.function import Function
from hallo.inc.commons import Commons


class RandomColour(Function):
    """
    Returns a random colour, hex code and name
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "random colour"
        # Names which can be used to address the function
        self.names = {"random colour", "random color", "colour", "color"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns a random colour. Format: random colour"

    def run(self, event):
        rgb_list = Commons.get_random_int(0, 255, 3)
        hex_code = "{}{}{}".format(
            hex(rgb_list[0])[2:].zfill(2),
            hex(rgb_list[1])[2:].zfill(2),
            hex(rgb_list[2])[2:].zfill(2),
        ).upper()
        url = "https://www.thecolorapi.com/id?hex={}".format(hex_code)
        human_url = "{}&format=html".format(url)
        colour_data = Commons.load_url_json(url)
        colour_name = colour_data["name"]["value"]
        output = "Randomly chosen colour is: {} #{} or rgb({},{},{}) {}".format(
            colour_name, hex_code, rgb_list[0], rgb_list[1], rgb_list[2], human_url
        )
        return event.create_response(output)