import os
from threading import Lock
import datetime
from Function import Function
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
        self.event_dict = {Function.EVENT_SECOND: self.log_second,
                           Function.EVENT_MINUTE: self.log_minute,
                           Function.EVENT_HOUR: self.log_hour,
                           Function.EVENT_DAY: self.log_day,
                           Function.EVENT_PING: self.log_ping,
                           Function.EVENT_MESSAGE: self.log_message,
                           Function.EVENT_JOIN: self.log_join,
                           Function.EVENT_LEAVE: self.log_leave,
                           Function.EVENT_QUIT: self.log_quit,
                           Function.EVENT_CHNAME: self.log_name_change,
                           Function.EVENT_KICK: self.log_kick,
                           Function.EVENT_INVITE: self.log_invite,
                           Function.EVENT_NOTICE: self.log_notice,
                           Function.EVENT_MODE: self.log_mode_change,
                           Function.EVENT_CTCP: self.log_ctcp}

    def log(self, event, full_line, server_obj=None, user_obj=None, channel_obj=None):
        """The function which actually writes the logs."""
        # If channel is set, check logging
        if channel_obj is not None and not channel_obj.get_logging():
            return None
        # If channel not set, but user is set, check their logging settings.
        if channel_obj is None and user_obj is not None and not user_obj.get_logging():
            return None
        # Check what type of event and pass to that to create line
        if event not in self.event_dict:
            return None
        log_function = self.event_dict[event]
        log_line = log_function(full_line, server_obj, user_obj, channel_obj)
        # If log_line is null, do nothing.
        if log_line is None:
            return None
        # Create file name
        file_name = self.get_file_name(server_obj, user_obj, channel_obj)
        # Write the log line
        self.add_line(file_name, log_line)
        return None
    
    def log_from_self(self, event, full_line, server_obj=None, user_obj=None, channel_obj=None):
        """Writes a log line for a message from hallo."""
        # If channel is set, check logging
        if channel_obj is not None and not channel_obj.get_logging():
            return None
        # If channel not set, but user is set, check their logging settings.
        if channel_obj is None and user_obj is not None and not user_obj.get_logging():
            return None
        # Check what type of event and pass to that to create line
        if event not in self.event_dict:
            return None
        log_function = self.event_dict[event]
        hallo_user_obj = server_obj.get_user_by_address(server_obj.get_nick().lower(), server_obj.get_nick())
        log_line = log_function(full_line, server_obj, hallo_user_obj, channel_obj)
        # If log_line is null, do nothing.
        if log_line is None:
            return None
        # Create file name
        file_name = self.get_file_name(server_obj, user_obj, channel_obj)
        # Write the log line
        self.add_line(file_name, log_line)
        return None
    
    def log_second(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def log_minute(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def log_hour(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def log_day(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def log_ping(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def log_message(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += '<' + user_obj.get_name() + '> ' + full_line
        return output
    
    def log_join(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += user_obj.get_name() + " joined " + channel_obj.get_name()
        return output
    
    def log_leave(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += user_obj.get_name() + " left " + channel_obj.get_name()
        if full_line.strip() != "":
            output += " (" + full_line + ")"
        return output
    
    def log_quit(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += user_obj.get_name() + " has quit."
        if full_line.strip() != "":
            output += " (" + full_line + ")"
        return output
    
    def log_name_change(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "Nick change: " + full_line + " -> " + user_obj.get_name()
        return output
    
    def log_kick(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += user_obj.get_name() + " was kicked from " + channel_obj.get_name()
        if full_line.strip() != "":
            output += " (" + full_line + ")"
        return output
    
    def log_invite(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "Invite to " + channel_obj.get_name() + ' from ' + user_obj.get_name()
        return output
    
    def log_notice(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "Notice from " + user_obj.get_name() + ": " + full_line
        return output
    
    def log_mode_change(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += user_obj.get_name() + ' set ' + full_line + ' on ' + channel_obj.get_name()
        return output
    
    def log_ctcp(self, full_line, server_obj, user_obj, channel_obj):
        ctcp_command = full_line.split()[0]
        ctcp_arguments = ' '.join(full_line.split()[1:])
        if ctcp_command.lower() == "action":
            output = Commons.current_timestamp() + " "
            output += "**" + user_obj.get_name() + ' ' + ctcp_arguments + '**'
            return output
        output = Commons.current_timestamp() + " "
        output += "<" + user_obj.get_name() + ' (CTCP)> ' + full_line
        return output
    
    def get_file_name(self, server_obj, user_obj, channel_obj):
        """Finds the file name of the file to write the log to."""
        file_name = "logs/"
        file_date = datetime.datetime.now().strftime("%Y-%m-%d")
        file_ext = ".txt"
        # If no server specified
        if server_obj is None:
            file_name += "@/"
            file_name += file_date+file_ext
            return file_name
        # Otherwise, go into server directory
        file_name += server_obj.get_name() + "/"
        # Check if channel object is specified
        if channel_obj is None:
            if user_obj is None:
                # No channel or user
                file_name += "@/"
                file_name += file_date+file_ext
                return file_name
            # No channel, but there is a user
            file_name += user_obj.get_name() + "/"
            file_name += file_date+file_ext
            return file_name
        # Channel object is set
        file_name += channel_obj.get_name() + "/"
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
