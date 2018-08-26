from abc import ABCMeta


class Event(metaclass=ABCMeta):

    is_inbound = True
    """ :type : bool"""
    send_time = None
    """ :type : """


class EventSecond(Event):  # TODO: implement
    pass


class EventMinute(Event):  # TODO: implement
    pass


class EventHour(Event):  # TODO: implement
    pass


class EventDay(Event):  # TODO: implement
    pass


class ServerEvent(Event, metaclass=ABCMeta):
    server = None
    """ :type : Server.Server"""


class EventPing(ServerEvent):  # TODO: implement
    ping_number = None
    """ :type : str"""


class UserEvent(ServerEvent, metaclass=ABCMeta):
    user = None
    """ :type : Destination.User"""


class EventQuit(UserEvent):  # TODO: implement
    quit_message = None
    """ :type : str"""


class EventNameChange(UserEvent):  # TODO: implement
    old_name = None
    """ :type : str"""
    new_name = None
    """ :type : str"""


class ChannelEvent(ServerEvent, metaclass=ABCMeta):
    channel = None
    """ :type : Destination.Channel | None"""


class ChannelUserEvent(ChannelEvent, UserEvent, metaclass=ABCMeta):
    pass


class EventJoin(ChannelUserEvent):  # TODO: implement
    pass


class EventLeave(ChannelUserEvent):  # TODO: implement
    leave_message = None
    """ :type : str"""


class EventKick(ChannelUserEvent):  # TODO: implement
    kicked_user = None
    """ :type : Destination.User"""
    kick_message = None
    """:type : str"""


class EventInvite(ChannelUserEvent):  # TODO: implement
    invited_user = None
    """ :type : Destination.User"""


class EventMode(ChannelUserEvent):  # TODO: implement
    mode_changes = None  # TODO: maybe have flags, arguments/users as separate?
    """ :type : str"""


class ChannelUserTextEvent(ChannelUserEvent, metaclass=ABCMeta):
    text = None
    """ :type : str"""


class EventMessage(ChannelUserTextEvent):  # TODO: implement
    pass


class EventNotice(ChannelUserTextEvent):  # TODO: implement
    pass


class EventCTCP(ChannelUserTextEvent):  # TODO: implement
    pass
