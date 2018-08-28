from abc import ABCMeta

from Events import EventSecond, EventMinute, EventHour, EventDay, EventPing, EventMessage, EventJoin, EventLeave, \
    EventQuit, EventNameChange, EventKick, EventInvite, EventNotice, EventMode, EventCTCP


class Function(metaclass=ABCMeta):
    """
    Generic function object. All functions inherit from this.
    """
    # Static constants
    EVENT_SECOND = EventSecond      # Event which happens every second
    EVENT_MINUTE = EventMinute      # Event which happens every minute
    EVENT_HOUR = EventHour          # Event which happens every hour
    EVENT_DAY = EventDay            # Event which happens every day
    EVENT_PING = EventPing          # Event constant signifying a server ping has been received
    EVENT_MESSAGE = EventMessage    # Event constant signifying a standard message
    EVENT_JOIN = EventJoin          # Event constant signifying someone joined a channel
    EVENT_LEAVE = EventLeave        # Event constant signifying someone left a channel
    EVENT_QUIT = EventQuit          # Event constant signifying someone disconnected
    EVENT_CHNAME = EventNameChange  # Event constant signifying someone changed their name
    EVENT_KICK = EventKick          # Event constant signifying someone was forcibly removed from the channel
    EVENT_INVITE = EventInvite      # Event constant signifying someone has invited hallo to a channel
    EVENT_NOTICE = EventNotice      # Event constant signifying a notice was received. (IRC only?)
    EVENT_MODE = EventMode          # Event constant signifying a channel mode change. (IRC only?)
    EVENT_CTCP = EventCTCP          # Event constant signifying a CTCP message received (IRC only)
    # EVENT_NUMERIC = "numeric"      # Event constant signifying a numeric message from a server (IRC only)
    # EVENT_RAW = "raw"           # Event constant signifying raw data received from server which doesn't fit the above

    def __init__(self):
        self.help_name = None  # Name for use in help listing
        self.names = set()  # Set of names which can be used to address the function
        self.help_docs = None  # Help documentation, if it's just a single line, can be set here
    
    def run(self, line, user_obj, destination_obj):
        """Runs the function when it is called directly
        :param line: User supplied arguments for this function call
        :type line: str
        :param user_obj: User who called the function
        :type user_obj: Destination.User
        :param destination_obj: Channel the function was called from, is None if private message
        :type destination_obj: Destination.Channel | None
        """
        raise NotImplementedError

    @staticmethod
    def is_persistent():
        """Returns boolean representing whether this function is supposed to be persistent or not"""
        return False
    
    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return Function()
    
    def save_function(self):
        """Saves the function, persistent functions only."""
        return None
    
    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return set()

    def passive_run(self, event, hallo_obj):
        """Replies to an event not directly addressed to the bot.
        :param event: Event which has called the function
        :type event: Events.Event
        :param hallo_obj: Hallo object which fired the event.
        :type hallo_obj: Hallo.Hallo
        """
        pass
        
    def get_help_name(self):
        """Returns the name to be printed for help documentation"""
        if self.help_name is None:
            raise NotImplementedError
        return self.help_name
    
    def get_help_docs(self):
        """
        Returns the help documentation, specific to given arguments, if supplied
        """
        if self.help_docs is None:
            raise NotImplementedError
        return self.help_docs
    
    def get_names(self):
        """Returns the list of names for directly addressing the function"""
        self.names.add(self.help_name)
        return self.names
