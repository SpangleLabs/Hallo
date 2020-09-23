from hallo.events import EventMessage
from hallo.function import Function
from hallo.inc.commons import Commons


class InSpace(Function):
    """
    Looks up the current amount and names of people in space
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "in space"
        # Names which can be used to address the function
        self.names = {"in space", "inspace", "space"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Returns the number of people in space right now, and their names. Format: in space"

    def run(self, event):
        space_dict = Commons.load_url_json(
            "https://www.howmanypeopleareinspacerightnow.com/space.json"
        )
        space_number = str(space_dict["number"])
        space_names = ", ".join(
            person["name"].strip() for person in space_dict["people"]
        )
        output_string = "There are {} people in space right now. Their names are: {}.".format(
            space_number, space_names
        )
        return event.create_response(output_string)

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        clean_line = event.text.lower()
        if "in space" in clean_line and (
            "who" in clean_line or "how many" in clean_line
        ):
            event.split_command_text("", clean_line)
            return self.run(event)
