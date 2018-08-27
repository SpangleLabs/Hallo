from abc import ABCMeta
from datetime import datetime


class Event(metaclass=ABCMeta):

    def __init__(self):
        self.is_inbound = True
        """ :type : bool"""
        self.send_time = datetime.now()
        """ :type : datetime"""


class EventSecond(Event):
    pass


class EventMinute(Event):
    pass


class EventHour(Event):
    pass


class EventDay(Event):
    pass


class ServerEvent(Event, metaclass=ABCMeta):

    def __init__(self, server):
        """
        :type server: Server.Server
        """
        super().__init__()
        self.server = server
        """ :type : Server.Server"""


class EventPing(ServerEvent):

    def __init__(self, server, ping_number):
        """
        :type server: Server.Server
        :type ping_number: str
        """
        super().__init__(server)
        self.ping_number = ping_number
        """ :type : str"""


class UserEvent(ServerEvent, metaclass=ABCMeta):

    def __init__(self, server, user):
        """
        :type server: Server.Server
        :type user: Destination.User | None
        """
        super().__init__(server)
        self.user = user
        """ :type : Destination.User | None"""


class EventQuit(UserEvent):

    def __init__(self, server, user, message):
        """
        :type server: Server.Server
        :type user: Destination.User
        :type message: str
        """
        super().__init__(server, user)
        self.quit_message = message
        """ :type : str"""


class EventNameChange(UserEvent):

    def __init__(self, server, user, old_name, new_name):
        """
        :type server: Server.Server
        :type user: Destination.User
        :type old_name: str
        :type new_name: str
        """
        super().__init__(server, user)
        self.old_name = old_name
        """ :type : str"""
        self.new_name = new_name
        """ :type : str"""


class ChannelEvent(ServerEvent, metaclass=ABCMeta):

    def __init__(self, server, channel):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        """
        super().__init__(server)
        self.channel = channel
        """ :type : Destination.Channel | None"""


class ChannelUserEvent(ChannelEvent, UserEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, user):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type user: Destination.User | None
        """
        ChannelEvent.__init__(self, server, channel)
        UserEvent.__init__(self, server, user)


class EventJoin(ChannelUserEvent):

    def __init__(self, server, channel, user):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :type user: Destination.User
        """
        super().__init__(server, channel, user)


class EventLeave(ChannelUserEvent):

    def __init__(self, server, channel, user, message):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :type user: Destination.User
        :type message: str | None
        """
        super().__init__(server, channel, user)
        self.leave_message = message
        """ :type : str | None"""


class EventKick(ChannelUserEvent):

    def __init__(self, server, channel, kicking_user, kicked_user, kick_message):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :type kicking_user: Destination.User
        :type kicked_user: Destination.User
        :type kick_message: str | None
        """
        super().__init__(server, channel, kicking_user)
        self.kicked_user = kicked_user
        """ :type : Destination.User"""
        self.kick_message = kick_message
        """:type : str | None"""


class EventInvite(ChannelUserEvent):

    def __init__(self, server, channel, inviting_user, invited_user):
        """
        :type server: Server.Server
        :type channel: Destination.Channel
        :type inviting_user: Destination.User
        :type invited_user: Destination.User
        """
        super().__init__(server, channel, inviting_user)
        self.invited_user = invited_user
        """ :type : Destination.User"""


class EventMode(ChannelUserEvent):

    def __init__(self, server, channel, user, mode_changes):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type user: Destination.User | None
        :type mode_changes: str
        """
        super().__init__(server, channel, user)
        self.mode_changes = mode_changes  # TODO: maybe have flags, arguments/users as separate?
        """ :type : str"""


class ChannelUserTextEvent(ChannelUserEvent, metaclass=ABCMeta):

    def __init__(self, server, channel, user, text):
        """
        :type server: Server.Server
        :type channel: Destination.Channel | None
        :type user: Destination.User | None
        :type text: str
        """
        super().__init__(server, channel, user)
        self.text = text
        """ :type : str"""


class EventMessage(ChannelUserTextEvent):

    # Flags, can be passed as a list to function dispatcher, and will change how it operates.
    FLAG_HIDE_ERRORS = "hide_errors"  # Hide all errors that result from running the function.

    def __init__(self, server, channel, user, text):
        super().__init__(server, channel, user, text)
        self.command_text = None
        """ :type : str | None"""
        self.is_prefixed = None
        """ :type : bool | str"""
        self.check_prefix()

    def check_prefix(self):
        if self.channel is None:
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


class EventNotice(ChannelUserTextEvent):
    pass


class EventCTCP(ChannelUserTextEvent):
    pass
