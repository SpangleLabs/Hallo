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


class EventMessage(ServerEvent):  # TODO: implement
    from_user = None
    """ :type : Destination.User"""
    to_destination = None
    """ :type : Destination.Channel | Destination.User"""
    text = None
    """ :type : str"""


class EventJoin(ServerEvent):  # TODO: implement
    user = None
    """ :type : Destination.User"""
    channel = None
    """ :type : Destination.Channel"""


class EventLeave(ServerEvent):  # TODO: implement
    user = None
    """ :type : Destination.User"""
    channel = None
    """ :type : Destination.Channel"""
    leave_message = None
    """ :type : str"""


class EventQuit(ServerEvent):  # TODO: implement
    user = None
    """ :type : Destination.User"""
    quit_message = None
    """ :type : str"""


class EventNameChange(ServerEvent):  # TODO: implement
    user = None
    """ :type : Destination.User"""
    old_name = None
    """ :type : str"""
    new_name = None
    """ :type : str"""


class EventKick(ServerEvent):  # TODO: implement
    channel = None
    """ :type : Destination.Channel"""
    kicked_user = None
    """ :type : Destination.User"""
    kicking_user = None
    """ :type : Destination.User"""
    kick_message = None
    """:type : str"""


class EventInvite(ServerEvent):  # TODO: implement
    channel = None
    """ :type : Destination.Channel"""
    invited_user = None
    """ :type : Destination.User"""
    inviting_user = None
    """ :type : Destination.User"""


class EventNotice(ServerEvent):  # TODO: implement
    from_user = None
    """ :type : Destination.User"""
    to_destination = None
    """ :type : Destination.Channel | Destination.User"""
    text = None
    """ :type : str"""


class EventMode(ServerEvent):  # TODO: implement
    channel = None
    """ :type : Destination.Channel"""
    mode_changer = None
    """ :type : Destination.User"""
    mode_changes = None
    """ :type : str"""


class EventCTCP(ServerEvent):  # TODO: implement
    from_user = None
    """ :type : Destination.User"""
    to_destination = None
    """ :type : Destination.Channel | Destination.User"""
    text = None
    """ :type : str"""


# EVENT_NUMERIC = "numeric"      # Event constant signifying a numeric message from a server (IRC only)
#EVENT_RAW = "raw"              # Event constant signifying raw data received from server which doesn't fit the above