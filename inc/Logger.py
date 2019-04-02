import os
from threading import Lock

from Errors import Error
from Events import ChannelEvent, UserEvent, Event
from inc.Commons import Commons

ERROR_LOG = "logs/error_log.txt"


def indent_all_but_first_line(text):
    return text.replace("\n", "\n   ")


class Logger:
    """
    Logging class. This is created and stored by the Hallo object.
    It exists in order to provide a single entry point to all logging.
    """

    def __init__(self, hallo):
        """
        Constructor
        """
        self.hallo = hallo
        self.lock = Lock()

    def log(self, loggable):
        """
        The function which actually writes the logs.
        :type loggable: Events.Event | Errors.Error
        """
        # If channel is set, check logging
        if isinstance(loggable, ChannelEvent) and \
                loggable.channel is not None and \
                not loggable.channel.logging:
            return
        # If channel not set, but user is set, check their logging settings.
        if isinstance(loggable, UserEvent) and \
                loggable.user is not None and \
                not loggable.user.logging:
            return
        # Log the event
        if isinstance(loggable, Event):
            self.log_event(loggable)
        if isinstance(loggable, Error):
            self.log_error(loggable)

    def log_error(self, error):
        """
        :type error: Errors.Error
        :return:
        """
        log_line = indent_all_but_first_line(error.get_log_line())
        self.add_line(ERROR_LOG, "{} {}".format(Commons.current_timestamp(error.time), log_line))

    def log_event(self, event):
        """
        :type event: Events.Event
        :return:
        """
        log_line = event.get_log_line()
        if log_line is None:
            return
        output = "{} {}".format(Commons.current_timestamp(event.get_send_time()), log_line)
        log_files = event.get_log_locations()
        for log_file in log_files:
            self.add_line("logs/" + log_file, output)

    def add_line(self, file_name, line):
        """Adds a new line to a specified file."""
        # Acquire thread lock
        with self.lock:
            # Create directories if they don't exist.
            file_name_split = file_name.split("/")
            for file_dir in ["/".join(file_name_split[:x]) for x in range(1, len(file_name_split))]:
                try:
                    os.mkdir(file_dir)
                except OSError:
                    pass
            # Open file and write log
            log_file = open(file_name, "a")
            log_file.write(line + "\n")
            log_file.close()
