from hallo import events, errors
from hallo.inc.commons import Commons


class Printer:
    """
    Printing class. This is created and stored by the Hallo object.
    It exists in order to provide a single entry point to all printing to screen.
    """

    def __init__(self, hallo):
        """
        Constructor
        """
        self.hallo = hallo

    def output(self, obj):
        """
        The function which actually prints the messages.
        :type obj: events.Event | errors.Error | str
        """
        # If event, treat as event
        if isinstance(obj, events.Event):
            print_line = self._get_print_line(obj.get_print_line(), obj.get_send_time())
        elif isinstance(obj, errors.Error):
            print_line = self._get_print_line(obj.get_print_line(), obj.time)
        else:
            # Otherwise, just use as a string
            print_line = self._get_print_line(obj)
        # Output the log line
        print(print_line)

    def _get_print_line(self, raw_text, send_time=None):
        """
        :type raw_text: str
        :type send_time: datetime.datetime | None
        :rtype: str
        """
        output = "{} {}".format(Commons.current_timestamp(send_time), raw_text)
        return output
