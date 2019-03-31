from Events import EventSecond, EventMinute, EventHour, EventDay, EventPing, EventQuit, EventNameChange, EventJoin, \
    EventLeave, EventKick, EventInvite, EventMode, EventNotice, EventCTCP, EventMessage
from inc.Commons import Commons
import datetime


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

    def output(self, event):
        """The function which actually prints the messages."""
        print_line = self.get_print_line(event)
        # Output the log line
        print(print_line)

    def get_print_line(self, event):
        output = "{} {}".format(Commons.current_timestamp(event.get_send_time()), event.get_print_line())
        return output

    def output_raw(self, raw_text):
        print_line = self.print_raw(raw_text)
        print(print_line)

    def print_raw(self, raw_text):
        output = "{} {}".format(Commons.current_timestamp(), raw_text)
        return output
