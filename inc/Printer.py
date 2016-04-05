from Function import Function
from inc.commons import Commons
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
        self.event_dict = {Function.EVENT_SECOND: self.print_second,
                           Function.EVENT_MINUTE: self.print_minute,
                           Function.EVENT_HOUR: self.print_hour,
                           Function.EVENT_DAY: self.print_day,
                           Function.EVENT_PING: self.print_ping,
                           Function.EVENT_MESSAGE: self.print_message,
                           Function.EVENT_JOIN: self.print_join,
                           Function.EVENT_LEAVE: self.print_leave,
                           Function.EVENT_QUIT: self.print_quit,
                           Function.EVENT_CHNAME: self.print_name_change,
                           Function.EVENT_KICK: self.print_kick,
                           Function.EVENT_INVITE: self.print_invite,
                           Function.EVENT_NOTICE: self.print_notice,
                           Function.EVENT_MODE: self.print_mode_change,
                           Function.EVENT_CTCP: self.print_ctcp}

    def output(self, event, full_line, server_obj=None, user_obj=None, channel_obj=None):
        """The function which actually prints the messages."""
        # If channel or server are set to all, set to None for getting output
        if server_obj == Commons.ALL_SERVERS:
            server_obj = None
        if channel_obj == Commons.ALL_CHANNELS:
            channel_obj = None
        # Check what type of event and pass to that to create line
        if event not in self.event_dict:
            return None
        print_function = self.event_dict[event]
        print_line = print_function(full_line, server_obj, user_obj, channel_obj)
        # Output the log line
        print(print_line)
        return None
    
    def output_from_self(self, event, full_line, server_obj=None, user_obj=None, channel_obj=None):
        """Prints lines for messages from hallo."""
        # Check what type of event and pass to that to create line
        if event not in self.event_dict:
            return None
        print_function = self.event_dict[event]
        hallo_user_obj = server_obj.get_user_by_name(server_obj.get_nick())
        print_line = print_function(full_line, server_obj, hallo_user_obj, channel_obj)
        # Write the log line
        print(print_line)
        return None
    
    def print_second(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def print_minute(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def print_hour(self, full_line, server_obj, user_obj, channel_obj):
        return None
    
    def print_day(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "Day changed: "+datetime.datetime.now().strftime("%Y-%m-%d")
        return output
    
    def print_ping(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        if user_obj is None:
            output += "["+server_obj.get_name() + "] PING"
        else:
            output += "["+server_obj.get_name() + "] PONG"
        return output
    
    def print_message(self, full_line, server_obj, user_obj, channel_obj):
        destination_object = channel_obj
        if channel_obj is None:
            destination_object = user_obj
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += destination_object.getName() + " "
        output += "<" + user_obj.get_name() + "> " + full_line
        return output
    
    def print_join(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += user_obj.get_name() + " joined " + channel_obj.get_name()
        return output
    
    def print_leave(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += user_obj.get_name() + " left " + channel_obj.get_name()
        if full_line.strip() != "":
            output += " (" + full_line + ")"
        return output
    
    def print_quit(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += user_obj.get_name() + " has quit."
        if full_line.strip() != "":
            output += " (" + full_line + ")"
        return output
    
    def print_name_change(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += "Nick change: " + full_line + " -> " + user_obj.get_name()
        return output
    
    def print_kick(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += user_obj.get_name() + " was kicked from " + channel_obj.get_name()
        if full_line.strip() != "":
            output += " (" + full_line + ")"
        return output
    
    def print_invite(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += "Invite to " + channel_obj.get_name() + ' from ' + user_obj.get_name()
        return output
    
    def print_notice(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += "Notice from " + user_obj.get_name() + ": " + full_line
        return output
    
    def print_mode_change(self, full_line, server_obj, user_obj, channel_obj):
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += user_obj.get_name() + ' set ' + full_line + ' on ' + channel_obj.get_name()
        return output
    
    def print_ctcp(self, full_line, server_obj, user_obj, channel_obj):
        # Get useful data and objects
        ctcp_command = full_line.split()[0]
        ctcp_arguments = ' '.join(full_line.split()[1:])
        destination_obj = channel_obj
        if channel_obj is None:
            destination_obj = user_obj
        # Print CTCP actions differently to other CTCP commands
        if ctcp_command.lower() == "action":
            output = Commons.current_timestamp() + " "
            output += "[" + server_obj.get_name() + "] "
            output += destination_obj.getName() + " "
            output += "**" + user_obj.get_name() + " " + ctcp_arguments + "**"
            return output
        output = Commons.current_timestamp() + " "
        output += "[" + server_obj.get_name() + "] "
        output += destination_obj.getName() + " "
        output += "<" + user_obj.get_name() + " (CTCP)> " + full_line
        return output
