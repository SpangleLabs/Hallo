from abc import ABCMeta


class Event(metaclass=ABCMeta):

    is_inbound = True
    """ :type : bool"""
    send_time = None
    """ :type : """


class EventSecond(Event):
    pass


class EventMinute(Event):
    pass


class EventHour(Event):
    pass


class EventDay(Event):
    pass


class EventPing(Event):
    server = None
    """ :type : Server.Server"""


class EventMessage(Event):
    server = None
    """ :type : Server.Server"""
    from_user = None
    """ :type : Destination.User"""
    to_destination = None
    """ :type : Destination.Channel | Destination.User"""
    text = None
    """ :type : str"""


class EventJoin(Event):
    server = None
    """ :type : Server.Server"""
    user = None
    """ :type : Destination.User"""
    channel = None
    """ :type : Destination.Channel"""


class EventLeave(Event):
    server = None
    """ :type : Server.Server"""
    user = None
    """ :type : Destination.User"""
    channel = None
    """ :type : Destination.Channel"""
    leave_message = None
    """ :type : str"""


class EventQuit(Event):
    server = None
    """ :type : Server.Server"""
    user = None
    """ :type : Destination.User"""
    quit_message = None
    """ :type : str"""


class EventNameChange(Event):
    server = None
    """ :type : Server.Server"""
    user = None
    """ :type : Destination.User"""
    old_name = None
    """ :type : str"""
    new_name = None
    """ :type : str"""


class EventKick(Event):
    server = None
    """ :type : Server.Server"""
    channel = None
    """ :type : Destination.Channel"""
    kicked_user = None
    """ :type : Destination.User"""
    kicking_user = None
    """ :type : Destination.User"""
    kick_message = None
    """:type : str"""


class EventInvite(Event):
    server = None
    """ :type : Server.Server"""
    channel = None
    """ :type : Destination.Channel"""
    invited_user = None
    """ :type : Destination.User"""
    inviting_user = None
    """ :type : Destination.User"""


class EventNotice(Event):
    server = None
    """ :type : Server.Server"""
    from_user = None
    """ :type : Destination.User"""
    to_destination = None
    """ :type : Destination.Channel | Destination.User"""
    text = None
    """ :type : str"""


class EventMode(Event):
    server = None
    """ :type : Server.Server"""
    channel = None
    """ :type : Destination.Channel"""
    mode_changer = None
    """ :type : Destination.User"""
    mode_changes = None
    """ :type : str"""


class EventCTCP(Event):
    server = None
    """ :type : Server.Server"""
    from_user = None
    """ :type : Destination.User"""
    to_destination = None
    """ :type : Destination.Channel | Destination.User"""
    text = None
    """ :type : str"""


# EVENT_NUMERIC = "numeric"      # Event constant signifying a numeric message from a server (IRC only)
#EVENT_RAW = "raw"              # Event constant signifying raw data received from server which doesn't fit the above