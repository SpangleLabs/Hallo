from hallo.function import Function
from hallo.inc.commons import Commons


class TimestampToDate(Function):
    """
    Converts an unix timestamp to a date
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "date"
        # Names which can be used to address the function
        self.names = {
            "timestamp to date",
            "unix timestamp",
            "unix",
            "unix timestamp to date",
        }
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Returns the date from a given unix timestamp. Format: date <timestamp>"
        )

    def run(self, event):
        try:
            line = int(event.command_args)
        except ValueError:
            return event.create_response("Invalid timestamp")
        return event.create_response(Commons.format_unix_time(line) + ".")