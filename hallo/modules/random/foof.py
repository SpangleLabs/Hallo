import re
import time

from hallo.events import EventMessage
from hallo.function import Function
from hallo.inc.commons import Commons


class Foof(Function):
    """
    FOOOOOOOOOF DOOOOOOOOOOF
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.help_name = "foof"  # Name for use in help listing
        self.names = {
            "foof",
            "fooof",
            "foooof",
        }  # Names which can be used to address the function
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "FOOOOOOOOOF. Format: foof"

    def run(self, event):
        """FOOOOOOOOOF. Format: foof"""
        rand = Commons.get_random_int(0, 60)[0]
        if rand <= 20:
            return event.create_response("doof")
        elif rand <= 40:
            return event.create_response("doooooof")
        else:
            if rand == 40 + 15:
                server_obj = event.server
                server_obj.send(event.create_response("Powering up..."))
                time.sleep(5)
                return event.create_response(
                    "d" * 100 + "o" * 1000 + "f" * 200 + "!" * 50
                )
            else:
                return event.create_response("ddddoooooooooooooooooooooffffffffff.")

    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names = set(["f" + "o" * x + "f" for x in range(2, 20)])
        self.names.add(self.help_name)
        return self.names

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot."""
        if not isinstance(event, EventMessage):
            return
        # Check if message matches any variation of foof
        if re.search(r"foo[o]*f[!]*", event.text, re.I):
            # Return response
            return self.run(event)

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return {EventMessage}
