import enum
import logging
from abc import ABCMeta
from datetime import datetime
from typing import List, Dict, Any, Union, Optional, TYPE_CHECKING, Type, Tuple

if TYPE_CHECKING:
    from telegram import Update, Message
    from hallo.destination import Destination, User, Channel
    from hallo.server import Server


class RawData(metaclass=ABCMeta):
    pass


class RawDataIRC(RawData):
    def __init__(self, line: str) -> None:
        """
        :param line: Line of text direct from the IRC server
        """
        self.line = line


class RawDataTelegram(RawData):
    def __init__(self, update_obj: Update) -> None:
        """
        :param update_obj: Update object from telegram server
        """
        self.update_obj = update_obj


class RawDataTelegramOutbound(RawData):
    def __init__(self, sent_msg_object: Message) -> None:
        """
        :param sent_msg_object: Sent message object returned when sending message on telegram
        :type sent_msg_object: ??
        """
        self.sent_msg_object = sent_msg_object


class Event(metaclass=ABCMeta):
    def __init__(self, inbound: bool = True) -> None:
        self.is_inbound = inbound
        self.send_time = datetime.now()

    def get_send_time(self) -> datetime:
        return self.send_time

    def get_log_line(self) -> Optional[str]:
        """
        :rtype: Optional[str]
        """
        return None

    def _get_log_extras(self) -> List[Dict[str, Any]]:
        return []

    def log(self) -> None:
        if self.get_log_line() is None:
            return
        chat_logger = logging.getLogger("chat")
        for extra in self._get_log_extras():
            chat_logger.info(self.get_log_line(), extra=extra)

    def get_print_line(self) -> Optional[str]:
        return None


class EventSecond(Event):
    pass


class EventMinute(Event):
    pass


class EventHour(Event):
    pass


class EventDay(Event):
    def get_print_line(self) -> str:
        return "Day changed: {}".format(self.send_time.strftime("%Y-%m-%d"))


class ServerEvent(Event, metaclass=ABCMeta):
    def __init__(self, server: Server, inbound: bool = True):
        Event.__init__(self, inbound=inbound)
        self.server = server
        self.raw_data = None

    def with_raw_data(self, raw_data: RawData):
        self.raw_data = raw_data
        return self

    def get_send_time(self) -> datetime:
        if isinstance(self.raw_data, RawDataTelegram):
            return self.raw_data.update_obj.message.date
        return super().get_send_time()

    def _get_log_extras(self) -> List[Dict[str, Any]]:
        return [
            {
                "server": self.server
            }
        ]

    def get_print_line(self) -> str:
        return "[{}] {}".format(self.server.name, self.get_log_line())


class EventPing(ServerEvent):
    def __init__(self, server: 'Server', ping_number: str, inbound: bool = True):
        ServerEvent.__init__(self, server, inbound=inbound)
        self.ping_number = ping_number

    def get_pong(self) -> 'EventPing':
        return EventPing(self.server, self.ping_number, inbound=False)

    def get_print_line(self) -> str:
        return "[{}] {}".format(self.server.name, "PING" if self.is_inbound else "PONG")


class UserEvent(ServerEvent, metaclass=ABCMeta):
    def __init__(self, server: 'Server', user: 'User', inbound: bool = True):
        ServerEvent.__init__(self, server, inbound=inbound)
        self.user = user

    def _get_log_extras(self) -> List[Dict[str, Any]]:
        channel_list = (
            self.user.get_channel_list()
            if self.is_inbound
            else self.server.channel_list
        )
        return [
            {
                "server": self.server,
                "destination": channel
            }
            for channel in channel_list
        ]


class EventQuit(UserEvent):
    def __init__(self, server: 'Server', user: 'User', message: str, inbound: bool = True):
        """
        :param user: User who quit the server, or none if outbound
        """
        UserEvent.__init__(self, server, user, inbound=inbound)
        self.quit_message = message

    def get_log_line(self) -> str:
        output = "{} has quit.".format(
            self.user.name if self.is_inbound else self.server.get_nick()
        )
        if self.quit_message is not None and self.quit_message.strip() != "":
            output += " ({})".format(self.quit_message)
        return output


class EventNameChange(UserEvent):
    def __init__(self, server: 'Server', user: 'User', old_name: str, new_name: str, inbound: bool = True) -> None:
        """
        :param user: User object who has changed their name, or None if outbound
        """
        UserEvent.__init__(self, server, user, inbound=inbound)
        self.old_name = old_name
        self.new_name = new_name

    def get_log_line(self) -> str:
        output = "Nick change: {} -> {}".format(self.old_name, self.new_name)
        return output


class ChannelEvent(ServerEvent, metaclass=ABCMeta):
    def __init__(self, server: 'Server', channel: 'Channel', inbound: bool = True) -> None:
        ServerEvent.__init__(self, server, inbound=inbound)
        self.channel = channel

    def _get_log_extras(self) -> List[Dict[str, Any]]:
        return [
            {
                "server": self.server,
                "destination": self.channel
            }
        ]


class ChannelUserEvent(ChannelEvent, UserEvent, metaclass=ABCMeta):
    def __init__(self, server: 'Server', channel: 'Channel', user: 'User', inbound: bool = True) -> None:
        ChannelEvent.__init__(self, server, channel, inbound=inbound)
        UserEvent.__init__(self, server, user, inbound=inbound)

    def _get_log_extras(self) -> List[Dict[str, Any]]:
        return [
            {
                "server": self.server,
                "destination": self.channel if self.channel is not None else self.user
            }
        ]

    @property
    def destination(self) -> 'Destination':
        return self.user if self.channel is None else self.channel


class EventJoin(ChannelUserEvent):
    def __init__(
            self,
            server: 'Server',
            channel: 'Channel',
            user: 'User',
            password: Optional[str] = None,
            inbound: bool = True
    ):
        """
        :param user: User who joined the channel, or None if outbound
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.password = password

    def get_log_line(self) -> str:
        output = "{} joined {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(),
            self.channel.name,
        )
        return output


class EventLeave(ChannelUserEvent):
    def __init__(
            self,
            server: 'Server',
            channel: 'Channel',
            user: 'User',
            message: Optional[str],
            inbound: bool = True
    ) -> None:
        """
        :param user: User who left the channel, or None if outbound
        """
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.leave_message = message

    def get_log_line(self) -> str:
        output = "{} left {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(),
            self.channel.name,
        )
        if self.leave_message is not None and self.leave_message.strip() != "":
            output += " ({})".format(self.leave_message)
        return output


class EventKick(ChannelUserEvent):
    def __init__(
            self,
            server: 'Server',
            channel: 'Channel',
            kicking_user: Optional['User'],
            kicked_user: 'User',
            kick_message: Optional[str],
            inbound: bool = True
    ) -> None:
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

    def get_log_line(self) -> str:
        output = "{} was kicked from {} by {}".format(
            self.kicked_user.name,
            self.channel.name,
            self.user if self.is_inbound else self.server.get_nick(),
        )
        if self.kick_message is not None and self.kick_message.strip() != "":
            output += " ({})".format(self.kick_message)
        return output


class EventInvite(ChannelUserEvent):
    def __init__(
            self,
            server: 'Server',
            channel: 'Channel',
            inviting_user: 'User',
            invited_user: 'User',
            inbound: bool = True
    ) -> None:
        """
        :param inviting_user: User which is doing the inviting, or None if outbound
        """
        ChannelUserEvent.__init__(self, server, channel, inviting_user, inbound=inbound)
        self.invited_user = invited_user

    def get_log_line(self) -> str:
        output = "{} was invited to {} by {}".format(
            self.invited_user.name,
            self.channel.name,
            self.user.name if self.is_inbound else self.server.get_nick(),
        )
        return output


class EventMode(ChannelUserEvent):
    def __init__(
            self,
            server: 'Server',
            channel: 'Channel',
            user: 'User',
            mode_changes: str,
            inbound: bool = True
    ) -> None:
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.mode_changes = (
            mode_changes  # TODO: maybe have flags, arguments/users as separate?
        )

    def get_log_line(self) -> str:
        channel_name = self.channel.name if self.channel is not None else "??"
        output = "{} set {} on {}".format(
            self.user.name if self.user is not None else self.server.get_nick(),
            self.mode_changes,
            channel_name,
        )
        return output


class ChannelUserTextEvent(ChannelUserEvent, metaclass=ABCMeta):
    def __init__(
            self,
            server: 'Server',
            channel: Optional['Channel'],
            user: 'User',
            text: str,
            inbound: bool = True
    ) -> None:
        ChannelUserEvent.__init__(self, server, channel, user, inbound=inbound)
        self.text = text or ""

    def create_response(
            self,
            text: str,
            event_class: Optional[Type['ChannelUserTextEvent']] = None
    ) -> 'ChannelUserTextEvent':
        if event_class is None:
            event_class = self.__class__
        resp = event_class(self.server, self.channel, self.user, text, inbound=False)
        return resp

    def reply(self, event: 'ChannelUserTextEvent') -> None:
        """
        Shorthand for server.reply(event, event)
        """
        self.server.reply(self, event)


class MenuButton:
    def __init__(self, text: str, data: str) -> None:
        self.text = text
        self.data = data


class EventMessage(ChannelUserTextEvent):

    # Flags, can be passed as a list to function dispatcher, and will change how it operates.
    FLAG_HIDE_ERRORS = (
        "hide_errors"  # Hide all errors that result from running the function.
    )

    class Formatting(enum.Enum):
        PLAIN = 1
        MARKDOWN = 2
        HTML = 3

    def __init__(
            self,
            server: 'Server',
            channel: Optional['Channel'],
            user: 'User',
            text: str,
            inbound: bool = True,
            *,
            menu_buttons: List[List['MenuButton']] = None
    ) -> None:
        """
        :param user: User who sent the event, or None for outbound to channel
        """
        ChannelUserTextEvent.__init__(
            self, server, channel, user, text, inbound=inbound
        )
        self.command_name = None
        self.command_args = None
        self.is_prefixed, self.command_text = self.check_prefix()
        self.formatting = EventMessage.Formatting.PLAIN
        self.menu_buttons = menu_buttons

    @property
    def message_id(self) -> Optional[int]:
        if isinstance(self.raw_data, RawDataTelegram):
            return self.raw_data.update_obj.message.message_id
        if isinstance(self.raw_data, RawDataTelegramOutbound):
            return self.raw_data.sent_msg_object.message_id
        return None

    def check_prefix(self) -> Tuple[Union[bool, str], Optional[str]]:
        """
        Checks whether prefix was given, and if so, parses it out of command text.
        :return: Returns whether prefix is given, and command text
        """
        if self.channel is None:
            return True, self.text
        acting_prefix = self.channel.get_prefix()
        if acting_prefix is False:
            acting_prefix = self.server.get_nick().lower()
            # Check if directly addressed
            if any(self.text.lower().startswith(acting_prefix + x) for x in [":", ","]):
                return True, self.text[len(acting_prefix) + 1:]
            elif self.text.lower().startswith(acting_prefix):
                return EventMessage.FLAG_HIDE_ERRORS, self.text[len(acting_prefix):]
            else:
                return False, None
        elif self.text.lower().startswith(acting_prefix):
            return True, self.text[len(acting_prefix) :]
        else:
            return False, None

    def split_command_text(self, command_name: str, command_args: str):
        self.command_name = command_name
        self.command_args = command_args

    def get_log_line(self) -> str:
        output = "<{}> {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(), self.text
        )
        return output

    def create_response(
            self,
            text: str,
            event_class: Optional['EventMessage'] = None,
            menu_buttons: List[List[MenuButton]] = None
    ) -> 'EventMessage':
        if event_class is None:
            event_class = self.__class__
        resp = event_class(self.server, self.channel, self.user, text, inbound=False, menu_buttons=menu_buttons)
        return resp


class EventNotice(ChannelUserTextEvent):
    def get_log_line(self) -> str:
        output = "Notice from {}: {}".format(
            self.user.name if self.is_inbound else self.server.get_nick(), self.text
        )
        return output


class EventCTCP(ChannelUserTextEvent):
    def get_log_line(self) -> str:
        ctcp_command = self.text.split()[0]
        ctcp_arguments = " ".join(self.text.split()[1:])
        user_name = self.user.name if self.is_inbound else self.server.get_nick()
        if ctcp_command.lower() == "action":
            output = "**{} {}**".format(user_name, ctcp_arguments)
        else:
            output = "<{} (CTCP)> {}".format(user_name, self.text)
        return output


class EventMessageWithPhoto(EventMessage):
    def __init__(
            self,
            server: 'Server',
            channel: Optional['Channel'],
            user: 'User',
            text: str,
            photo_id: Union[str, List[str]],
            inbound: bool = True,
            *,
            menu_buttons: List[List[MenuButton]] = None
    ) -> None:
        """
        :type server: server.Server
        :type channel: destination.Channel | None
        :param user: User who sent the event, or None for outbound to channel
        :type user: destination.User | None
        :type text: str
        :type photo_id: Union[str, List[str]]
        """
        super().__init__(server, channel, user, text, inbound=inbound, menu_buttons=menu_buttons)
        self.photo_id = photo_id


class EventMenuCallback(ChannelUserEvent):

    def __init__(
            self,
            server: 'Server',
            channel: 'Channel',
            user: 'User',
            message_id: int,
            callback_data: str
    ) -> None:
        super().__init__(server, channel, user)
        self.message_id = message_id
        self.callback_data = callback_data
