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
        if isinstance(event, EventSecond):
            return self.print_second(event)
        if isinstance(event, EventMinute):
            return self.print_minute(event)
        if isinstance(event, EventHour):
            return self.print_hour(event)
        if isinstance(event, EventDay):
            return self.print_day(event)
        if isinstance(event, EventPing):
            return self.print_ping(event)
        if isinstance(event, EventQuit):
            return self.print_quit(event)
        if isinstance(event, EventNameChange):
            return self.print_name_change(event)
        if isinstance(event, EventJoin):
            return self.print_join(event)
        if isinstance(event, EventLeave):
            return self.print_leave(event)
        if isinstance(event, EventKick):
            return self.print_kick(event)
        if isinstance(event, EventInvite):
            return self.print_invite(event)
        if isinstance(event, EventMode):
            return self.print_mode_change(event)
        if isinstance(event, EventNotice):
            return self.print_notice(event)
        if isinstance(event, EventCTCP):
            return self.print_ctcp(event)
        if isinstance(event, EventMessage):
            return self.print_message(event)
        raise NotImplementedError("Printer doesn't support this event type")

    def output_raw(self, raw_text):
        print_line = self.print_raw(raw_text)
        print(print_line)
    
    def print_second(self, event):
        return None
    
    def print_minute(self, event):
        return None
    
    def print_hour(self, event):
        return None
    
    def print_day(self, event):
        output = "{} Day changed: {}".format(Commons.current_timestamp(), datetime.datetime.now().strftime("%Y-%m-%d"))
        return output
    
    def print_ping(self, event):
        output = "{} [{}] {}".format(Commons.current_timestamp(), event.server.name,
                                     "PING" if event.is_inbound is None else "PONG")
        return output

    def print_quit(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} [{}] {} has quit.".format(Commons.current_timestamp(), event.server.name, user_name)
        if event.quit_message.strip() != "":
            output += " ({})".format(event.quit_message)
        return output

    def print_name_change(self, event):
        output = "{} [{}] Nick change: {} -> {}".format(Commons.current_timestamp(), event.server.name,
                                                        event.old_name, event.new_name)
        return output

    def print_join(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} [{}] {} joined {}".format(Commons.current_timestamp(), event.server.name,
                                               user_name, event.channel.name)
        return output

    def print_leave(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} [{}] {} left {}".format(Commons.current_timestamp(), event.server.name,
                                             user_name, event.channel)
        if event.leave_message is not None:
            output += " ({})".format(event.leave_message)
        return output

    def print_kick(self, event):
        """
        :param event: EventKick
        :rtype: str
        """
        kicking_user_name = event.user if event.is_inbound else event.server.get_nick()
        output = "{} [{}] {} was kicked from {} by {}".format(Commons.current_timestamp(), event.server.name,
                                                              event.kicked_user.name, event.channel.name,
                                                              kicking_user_name)
        if event.kick_message is not None:
            output += " ({})".format(event.kick_message)
        return output

    def print_invite(self, event):
        inviting_user_name = event.user.name if event.is_inbound else event.server.get_nick()
        output = "{} [{}] {} was invited to {} by {}".format(Commons.current_timestamp(), event.server.name,
                                                             event.invited_user.name, event.channel.name,
                                                             inviting_user_name)
        return output

    def print_mode_change(self, event):
        channel_name = event.channel.name if event.channel is not None else "??"
        user_name = event.user.name if event.user is not None else event.server.get_nick()
        output = "{} [{}] {} set {} on {}".format(Commons.current_timestamp(), event.server.name,
                                                  user_name, event.mode_changes, channel_name)
        return output
    
    def print_message(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        dest_name = event.channel.name if event.channel is not None else event.user.name
        output = "{} [{}] {} <{}> {}".format(Commons.current_timestamp(), event.server.name,
                                             dest_name, user_name, event.text)
        return output
    
    def print_notice(self, event):
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        dest_name = event.channel.name if event.channel is not None else event.user.name
        output = "{} [{}] Notice in {} from {}: {}".format(Commons.current_timestamp(), event.server.name, dest_name,
                                                           user_name, event.text)
        return output
    
    def print_ctcp(self, event):
        # Get useful data and objects
        ctcp_command = event.text.split()[0]
        ctcp_arguments = ' '.join(event.text.split()[1:])
        user_name = event.user.name if event.is_inbound else event.server.get_nick()
        dest_name = event.channel.name if event.channel is not None else event.user.name
        # Print CTCP actions differently to other CTCP commands
        if ctcp_command.lower() == "action":
            output = "{} [{}] {} **{} {}**".format(Commons.current_timestamp(), event.server.name, dest_name,
                                                   user_name, ctcp_arguments)
            return output
        output = "{} [{}] {} <{} (CTCP)> {}".format(Commons.current_timestamp(), event.server.name, dest_name,
                                                    user_name, event.text)
        return output

    def print_raw(self, raw_text):
        output = "{} {}".format(Commons.current_timestamp(), raw_text)
        return output
