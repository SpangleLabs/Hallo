import enum
from abc import ABCMeta
from datetime import datetime


class RawData(metaclass=ABCMeta):
    pass


class RawDataIRC(RawData):

    def __init__(self, line):
        """
        :param line: Line of text direct from the IRC server
        :type line: str
        """
        self.line = line


class RawDataTelegram(RawData):

    def __init__(self, update_obj):
        """
        :param update_obj: Update object from telegram server
        :type update_obj: ??
        """
        self.update_obj = update_obj


class RawDataTelegramOutbound(RawData):

    def __init__(self, sent_msg_object):
        """
        :param sent_msg_object: Sent message object returned when sending message on telegram
        :type sent_msg_object: ??
        """
        self.sent_msg_object = sent_msg_object


# Graphviz graph of Event class relations
# digraph G {
#
# Event[shape = rectangle]
# EventSecond->Event
# EventMinute->Event
# EventHour->Event
# EventDay->Event
#
# ServerEvent[shape = rectangle]
# ServerEvent->Event
# EventPing->ServerEvent
#
# UserEvent[shape = rectangle]
# UserEvent->ServerEvent
# EventQuit->UserEvent
# EventNameChange->EventQuit
#
# ChannelEvent[shape = rectangle]
# ChannelEvent->ServerEvent
#
# ChannelUserEvent[shape = rectangle]
# ChannelUserEvent->ChannelEvent
# ChannelUserEvent->UserEvent
# EventJoin->ChannelUserEvent
# EventLeave->ChannelUserEvent
# EventKick->ChannelUserEvent
# EventInvite->ChannelUserEvent
# EventMode->ChannelUserEvent
#
# ChannelUserTextEvent[shape = rectangle]
# ChannelUserTextEvent->ChannelUserEvent
# EventMessage->ChannelUserTextEvent
# EventNotice->ChannelUserTextEvent
# EventCTCP->ChannelUserTextEvent
# EventMessageWithPhoto->EventMessage
# }

class Event(metaclass=ABCMeta):

    def __init__(self, inbound=True):
        """
        :type inbound: bool
        """
        self.is_inbound = inbound
        """ :type : bool"""
        self.send_time = datetime.now()
        """ :type : datetime"""

    def get_send_time(self):
        """
        :rtype: datetime
        """
        return self.send_time

    def get_log_line(self):
        """
        :rtype: Optional[str]
        """
        return None

    def get_log_locations(self):
        """
        :rtype: list[str]
        """
        return []

    def get_print_line(self):
        """
        :rtype: Optional[str]
        """
        return None


class EventSecond(Event):
    pass


class EventMinute(Event):
    pass


class EventHour(Event):
    pass


class EventDay(Event):

    def get_print_line(self):
        return "Day changed: {}".format(self.send_time.strftime("%Y-%m-%d"))


class ServerEvent(Event, metaclass=ABCMeta):

    def __init__(self, server, inbound=True):
        """
        :type server: server.Server
        :type inbound: bool
        """
        Event.__init__(self, inbound=inbound)
        self.server = server
        """ :type : Server.Server"""
        self.raw_data = None
        """ :type : RawData | None"""

    def with_raw_data(self, raw_data):
        """
        :type raw_data: RawData
        """
        self.raw_data = raw_data
        return self

    def get_send_time(self):
        """
        :rtype: datetime
        """
        if isinstance(self.raw_data, RawDataTelegram):
            return self.raw_data.update_obj.message.date
        return super().get_send_time()

    def get_log_locations(self):
        return ["{}/@/{}.txt".format(
            self.server.name,
            self.get_send_time().strftime("%Y-%m-%d")
        )]

    def get_print_line(self):
        return "[{}] {}".format(self.server.name, self.get_log_line())


class EventPing(ServerEvent):

    def __init__(self, server, ping_number, inbound=True):
        """
        :type server: server.Server
        :type ping_number: str
        :type inbound: bool
        """
        ServerEvent.__init__(self, server, inbound=inbound)
        self.ping_number = ping_number
        """ :type : str"""

    def get_pong(self):
        return EventPing(self.server, self.ping_number, inbound=False)

    def get_print_line(self):
        return "[{}] {}".format(
            self.server.name,
            "PING" if self.is_inbound else "PONG"
        )


class UserEvent(ServerEvent, metaclass=ABCMeta):

    def __init__(self, server, user, inbound=True):
        """
        :type server: server.Server
        :type user: destination.User | None
        :type inbound: bool
        """
        ServerEvent.__init__(self, server, inbound=inbound)
        self.user = user
        """ :type : Destination.User | None"""

    def get_log_locations(self):
        channel_list = self.user.get_channel_list() if self.is_inbound else self.server.channel_list
        log_files = []
        for channel in channel_list:
            log_files.append("{}/{}/{}.txt".format(
                self.server.name,
                channel.name,
                self.get_send_time().strftime("%Y-%m-%d")
            ))
        return log_files


class EventQuit(UserEvent):

    def __init__(self, server, user, message, inbound=True):
        """
        :type server: server.Server
        :param user: User who quit the server, or none if outbound
        :type user: destination.User | None
        :type message: str
        :type inbound: bool
        """
        UserEvent.__init__(self, server, user, inbound=inbound)
        self.quit_message = message
        """ :type : str"""

    def get_log_line(self):
        output = "{} has quit.".format(self.user.name if self.is_inbound else self.server.get_nick())
        if self.quit_message is not None and self.quit_message.strip() != "":
            output += " ({})".format(self.quit_message)
        return output


class EventNameChange(UserEvent):

    def __init__(self, server, user, old_name, new_name, inbound=True):
        """
        :type server: server.Server
        :param user: User object who has changed their name, or None if outbound
        :type user: destination.User | None
        :type old_name: str
        :type new_name: str
        :type inbound: bool
        """
        UserEvent.__init__(self, server, user, inbound=inbound)
        self.old_name = old_name
        """ :type : str"""
        self.new_name = new_name
        """ :type : str"""

    def get_log_line(self):
        output = "Nick change: {} -> {}".format(self.old_name, self.new_name)
        return output


class ChannelEvent(ServerEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :type inbound: bool
        """
        ServerEvent.__init__(self, server, inbound=inbound)
        self.channel = channel
        """ :type : Destination.Channel | None"""

    def get_log_locations(self):
        return ["{}/{}/{}.txt".format(
            self.server.name,
            self.channel.name if self.channel is not None else "@",
            self.get_send_time().strftime("%Y-%m-%d")
        )]


class ChannelUserEvent(ChannelEvent, UserEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, user, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :type user: destination.User | None
        :type inbound: bool
        """
        ChannelEvent.__init__(self, server, channel, inbound=inbound)
        UserEvent.__init__(self, server, user, inbound=inbound)

    def get_log_locations(self):
        return ["{}/{}/{}.txt".format(
            self.server.name,
            self.channel.name if self.channel is not None else self.user.name,
            self.get_send_time().strftime("%Y-%m-%d")
        )]


class EventJoin(ChannelUserEvent):

    def __init__(self, server, channel, user, password=None, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel
        :param user: User who joined the channel, or None if outbound
        :type user: destination.User | None
        :type password: str | None
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.password = password
        """ :type : str | None"""

    def get_log_line(self):
        output = "{} joined {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(),
            self.channel.name)
        return output


class EventLeave(ChannelUserEvent):

    def __init__(self, server, channel, user, message, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel
        :param user: User who left the channel, or None if outbound
        :type user: destination.User | None
        :type message: str | None
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.leave_message = message
        """ :type : str | None"""

    def get_log_line(self):
        output = "{} left {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(),
            self.channel.name)
        if self.leave_message is not None and self.leave_message.strip() != "":
            output += " ({})".format(self.leave_message)
        return output


class EventKick(ChannelUserEvent):

    def __init__(self, server, channel, kicking_user, kicked_user, kick_message, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel
        :param kicking_user: User which sent the kick event, or None if outbound
        :type kicking_user: destination.User | None
        :type kicked_user: destination.User
        :type kick_message: str | None
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, kicking_user, inbound=inbound)
        self.kicked_user = kicked_user
        """ :type : Destination.User"""
        self.kick_message = kick_message
        """:type : str | None"""

    def get_log_line(self):
        output = "{} was kicked from {} by {}".format(
            self.kicked_user.name,
            self.channel.name,
            self.user if self.is_inbound else self.server.get_nick())
        if self.kick_message is not None and self.kick_message.strip() != "":
            output += " ({})".format(self.kick_message)
        return output


class EventInvite(ChannelUserEvent):

    def __init__(self, server, channel, inviting_user, invited_user, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel
        :param inviting_user: User which is doing the inviting, or None if outbound
        :type inviting_user: destination.User | None
        :type invited_user: destination.User
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, inviting_user, inbound=inbound)
        self.invited_user = invited_user
        """ :type : Destination.User"""

    def get_log_line(self):
        output = "{} was invited to {} by {}".format(
            self.invited_user.name,
            self.channel.name,
            self.user.name if self.is_inbound else self.server.get_nick())
        return output


class EventMode(ChannelUserEvent):

    def __init__(self, server, channel, user, mode_changes, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :type user: destination.User | None
        :type mode_changes: str
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.mode_changes = mode_changes  # TODO: maybe have flags, arguments/users as separate?
        """ :type : str"""

    def get_log_line(self):
        channel_name = self.channel.name if self.channel is not None else "??"
        output = "{} set {} on {}".format(
            self.user.name if self.user is not None else self.server.get_nick(),
            self.mode_changes,
            channel_name)
        return output


class ChannelUserTextEvent(ChannelUserEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, user, text, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :type user: destination.User | None
        :type text: str
        :type inbound: bool
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.text = text
        """ :type : str"""

    def create_response(self, text, event_class=None):
        """
        :type text: str
        :type event_class: type | None
        """
        if event_class is None:
            event_class = self.__class__
        resp = event_class(self.server, self.channel, self.user, text, inbound=False)
        return resp

    def reply(self, event):
        """
        Shorthand for server.reply(event, event)
        :type event: ChannelUserTextEvent
        """
        self.server.reply(self, event)


class EventMessage(ChannelUserTextEvent):

    # Flags, can be passed as a list to function dispatcher, and will change how it operates.
    FLAG_HIDE_ERRORS = "hide_errors"  # Hide all errors that result from running the function.

    class Formatting(enum.Enum):
        PLAIN = 1
        MARKDOWN = 2
        HTML = 3

    def __init__(self, server, channel, user, text, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :param user: User who sent the event, or None for outbound to channel
        :type user: destination.User | None
        :type text: str
        :type inbound: bool
        """
        ChannelUserTextEvent.__init__(self, server, channel, user, text, inbound=inbound)
        self.command_text = None
        """ :type : str | None"""
        self.is_prefixed = None
        """ :type : bool | str"""
        self.command_name = None
        """ :type : str | None"""
        self.command_args = None
        """ :type : str | None"""
        self.check_prefix()
        self.formatting = EventMessage.Formatting.PLAIN

    def check_prefix(self):
        if self.channel is None:
            self.is_prefixed = True
            self.command_text = self.text
            return
        acting_prefix = self.channel.get_prefix()
        if acting_prefix is False:
            acting_prefix = self.server.get_nick().lower()
            # Check if directly addressed
            if any(self.text.lower().startswith(acting_prefix+x) for x in [":", ","]):
                self.is_prefixed = True
                self.command_text = self.text[len(acting_prefix) + 1:]
            elif self.text.lower().startswith(acting_prefix):
                self.is_prefixed = EventMessage.FLAG_HIDE_ERRORS
                self.command_text = self.text[len(acting_prefix):]
            else:
                self.is_prefixed = False
                self.command_text = None
        elif self.text.lower().startswith(acting_prefix):
            self.is_prefixed = True
            self.command_text = self.text[len(acting_prefix):]
        else:
            self.is_prefixed = False
            self.command_text = None

    def split_command_text(self, command_name, command_args):
        """
        :type command_name: str
        :type command_args: str
        """
        self.command_name = command_name
        self.command_args = command_args

    def get_log_line(self):
        output = "<{}> {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(),
            self.text)
        return output


class EventNotice(ChannelUserTextEvent):

    def get_log_line(self):
        output = "Notice from {}: {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(),
            self.text)
        return output


class EventCTCP(ChannelUserTextEvent):

    def get_log_line(self):
        ctcp_command = self.text.split()[0]
        ctcp_arguments = ' '.join(self.text.split()[1:])
        user_name = self.user.name if self.is_inbound else self.server.get_nick()
        if ctcp_command.lower() == "action":
            output = "**{} {}**".format(
                user_name,
                ctcp_arguments)
        else:
            output = "<{} (CTCP)> {}".format(
                user_name,
                self.text)
        return output


class EventMessageWithPhoto(EventMessage):

    def __init__(self, server, channel, user, text, photo_id, inbound=True):
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :param user: User who sent the event, or None for outbound to channel
        :type user: destination.User | None
        :type text: str
        :type photo_id: Union[str, List[str]]
        """
        super().__init__(server, channel, user, text, inbound=inbound)
        self.photo_id = photo_id
        """ :type : str"""
