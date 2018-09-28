import os
from threading import Lock
import datetime

from Events import EventSecond, EventMinute, EventHour, EventDay, EventPing, EventQuit, EventNameChange, EventJoin, \
    EventLeave, EventKick, EventInvite, EventMode, EventNotice, EventCTCP, EventMessage, ChannelEvent
from inc.Commons import Commons


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

    def log(self, event):
        """The function which actually writes the logs."""
        # If channel is set, check logging
        if isinstance(event, ChannelEvent) and \
                event.channel is not None and \
                not event.channel.logging:
            return
        # If channel not set, but user is set, check their logging settings.
        if isinstance(event, ChannelEvent) and \
                event.channel is None and \
                event.user is not None and \
                not event.user.logging:
            return
        # Log the event
        self.log_event(event)
    
    def log_from_self(self):
        raise NotImplementedError()

    def log_event(self, event):
        if isinstance(event, EventSecond):
            return self.log_second(event)
        if isinstance(event, EventMinute):
            return self.log_minute(event)
        if isinstance(event, EventHour):
            return self.log_hour(event)
        if isinstance(event, EventDay):
            return self.log_day(event)
        if isinstance(event, EventPing):
            return self.log_ping(event)
        if isinstance(event, EventQuit):
            return self.log_quit(event)
        if isinstance(event, EventNameChange):
            return self.log_name_change(event)
        if isinstance(event, EventJoin):
            return self.log_join(event)
        if isinstance(event, EventLeave):
            return self.log_leave(event)
        if isinstance(event, EventKick):
            return self.log_kick(event)
        if isinstance(event, EventInvite):
            return self.log_invite(event)
        if isinstance(event, EventMode):
            return self.log_mode_change(event)
        if isinstance(event, EventNotice):
            return self.log_notice(event)
        if isinstance(event, EventCTCP):
            return self.log_ctcp(event)
        if isinstance(event, EventMessage):
            return self.log_message(event)
        raise NotImplementedError("Printer doesn't support this event type")
    
    def log_second(self, event):
        return
    
    def log_minute(self, event):
        return
    
    def log_hour(self, event):
        return
    
    def log_day(self, event):
        return
    
    def log_ping(self, event):
        return

    def log_quit(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} {} has quit.".format(Commons.current_timestamp(), user_name)
        if event.quit_message.strip() != "":
            output += " ({})".format(event.quit_message)
        # Log to every channel user is in
        channel_list = event.server.channel_list if event.user is None else event.user.get_channel_list()
        for channel in channel_list:
            self.add_log_line(output, event.server.name, user_name, channel.name)

    def log_name_change(self, event):
        output = "{} Nick change: {} -> {}".format(Commons.current_timestamp(), event.old_name, event.new_name)
        # Log to every channel user is in
        channel_list = event.server.channel_list if event.user is None else event.user.get_channel_list()
        for channel in channel_list:
            self.add_log_line(output, event.server.name, event.old_name, channel.name)

    def log_join(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} {} joined {}".format(Commons.current_timestamp(), user_name, event.channel.name)
        self.add_log_line(output, event.server.name, user_name, event.channel.name)

    def log_leave(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} {} left {}".format(Commons.current_timestamp(), user_name, event.channel.name)
        if event.leave_message.strip() != "":
            output += " ({})".format(event.leave_message)
        self.add_log_line(output, event.server.name, user_name, event.channel.name)

    def log_kick(self, event):
        kicking_user_name = event.user if event.is_inbound else event.server.get_nick()
        output = "{} {} was kicked from {} by {}".format(Commons.current_timestamp(), event.kicked_user.name,
                                                         event.channel.name, kicking_user_name)
        if event.kick_message.strip() != "":
            output += " ({})".format(event.kick_message)
        self.add_log_line(output, event.server.name, kicking_user_name, event.channel.name)

    def log_invite(self, event):
        inviting_user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} was invited to {} by {}".format(Commons.current_timestamp(), event.invited_user.name,
                                                     event.channel.name, inviting_user_name)
        self.add_log_line(output, event.server.name, inviting_user_name, event.channel.name)

    def log_mode_change(self, event):
        channel_name = event.channel.name if event.channel is not None else "??"
        user_name = event.user.name if event.user is not None else event.server.get_nick()
        output = "{} {} set {} on {}".format(Commons.current_timestamp(), user_name, event.mode_changes, channel_name)
        self.add_log_line(output, event.server.name, user_name, event.channel.name)
    
    def log_message(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        chan_name = None if event.channel is None else event.channel.name
        output = "{} <{}> {}".format(Commons.current_timestamp(), user_name, event.text)
        self.add_log_line(output, event.server.name, user_name, chan_name)
    
    def log_notice(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        chan_name = None if event.channel is None else event.channel.name
        output = "{} Notice from {}: {}".format(Commons.current_timestamp(), user_name, event.text)
        self.add_log_line(output, event.server.name, event.user.name, chan_name)
    
    def log_ctcp(self, event):
        ctcp_command = event.text.split()[0]
        ctcp_arguments = ' '.join(event.text.split()[1:])
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        chan_name = None if event.channel is None else event.channel.name
        if ctcp_command.lower() == "action":
            output = "{} **{} {}**".format(Commons.current_timestamp(), user_name, ctcp_arguments)
        else:
            output = "{} <{} (CTCP)> {}".format(Commons.current_timestamp(), user_name, event.text)
        self.add_log_line(output, event.server.name, event.user.name, chan_name)

    def add_log_line(self, output, server_name, user_name, channel_name):
        file_name = self.get_file_name(server_name, user_name, channel_name)
        self.add_line(file_name, output)
    
    def get_file_name(self, server_name, user_name, channel_name):
        """
        Finds the file name of the file to write the log to.
        :type server_name: str | None
        :type user_name: str | None
        :type channel_name: str | None
        """
        file_name = "logs/"
        file_date = datetime.datetime.now().strftime("%Y-%m-%d")
        file_ext = ".txt"
        # If no server specified
        if server_name is None:
            file_name += "@/"
            file_name += file_date+file_ext
            return file_name
        # Otherwise, go into server directory
        file_name += server_name + "/"
        # Check if channel object is specified
        if channel_name is None:
            if user_name is None:
                # No channel or user
                file_name += "@/"
                file_name += file_date+file_ext
                return file_name
            # No channel, but there is a user
            file_name += user_name + "/"
            file_name += file_date+file_ext
            return file_name
        # Channel object is set
        file_name += channel_name + "/"
        file_name += file_date+file_ext
        return file_name

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
            log_file.write(line+"\n")
            log_file.close()
