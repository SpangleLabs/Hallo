import logging
import re
import socket
import time
from threading import RLock, Lock, Thread

from hallo.destination import ChannelMembership, Channel, User
from hallo.errors import MessageError, ExceptionError
from hallo.events import (
    EventPing,
    EventQuit,
    EventNameChange,
    EventJoin,
    EventLeave,
    EventKick,
    EventInvite,
    EventMode,
    EventCTCP,
    EventNotice,
    EventMessage,
    ChannelUserTextEvent,
    RawDataIRC,
)
from hallo.permission_mask import PermissionMask
from hallo.server import Server, ServerException
from hallo.inc.commons import Commons

endl = Commons.END_LINE
logger = logging.getLogger(__name__)


class ServerIRC(Server):
    MAX_MSG_LENGTH = 462
    type = Server.TYPE_IRC

    def __init__(self, hallo, server_name=None, server_url=None, server_port=6667):
        """
        Constructor for server object
        :param hallo: Hallo instance which owns this server
        :type hallo: hallo.Hallo
        :param server_name: Name of the IRC server
        :type server_name: str
        :param server_url: URL of the IRC server
        :type server_url: str
        :param server_port: port of the IRC server
        :type server_port: int
        """
        super().__init__(hallo)
        # IRC specific variables
        self.server_address = None  # Address to connect to server
        self.server_port = None  # Port to connect to server
        self.nickserv_pass = None  # Password to identify with nickserv
        self.nickserv_nick = (
            "nickserv"  # Nickserv's nick, None if nickserv does not exist
        )
        self.nickserv_ident_command = (
            "STATUS"  # Command to send to nickserv to check if a user is identified
        )
        self.nickserv_ident_response = "\\b3\\b"  # Regex to search for to validate identity in response to IdentCommand
        # IRC specific dynamic variables
        self._socket = None  # Socket to communicate to the server
        self._welcome_message = (
            ""  # Server's welcome message when connecting. MOTD and all.
        )
        self._check_channeluserlist_lock = (
            Lock()
        )  # Thread lock for checking a channel's user list
        self._check_channeluserlist_channel = None  # Channel to check user list of
        self._check_channeluserlist_done = False  # Whether the check is complete
        self._check_usersonline_lock = (
            Lock()
        )  # Thread lock for checking which users are online
        self._check_usersonline_check_list = None  # List of users' names to check
        self._check_usersonline_online_list = (
            None  # List of users' names who are online
        )
        self._check_useridentity_lock = (
            Lock()
        )  # Thread lock for checking if a user is identified with nickserv
        self._check_useridentity_user = None  # User name which is being checked
        self._check_useridentity_result = (
            None  # Boolean, whether or not the user is identified
        )
        self._connect_lock = RLock()
        if server_name is not None:
            self.name = server_name
        if server_url is not None:
            self.server_address = server_url
            self.server_port = server_port

    def start(self):
        """
        Starts up the server and launches the new thread
        """
        if self.state != Server.STATE_CLOSED:
            raise ServerException("Already started.")
        self.state = Server.STATE_CONNECTING
        with self._connect_lock:
            Thread(target=self.run).start()

    def connect(self):
        """
        Internal method, connects to the IRC server, attempting as many times as is necessary.
        """
        try:
            self.raw_connect()
            return
        except ServerException as e:
            error = ExceptionError(
                'Failed to connect to "{}" IRC server on first attempt. Attempting reconnect.'.format(
                    self.name
                ),
                e,
                self,
            )
            logger.error(error.get_log_line())
            while self.state == Server.STATE_CONNECTING:
                try:
                    self.raw_connect()
                    return
                except ServerException as e:
                    error = ExceptionError(
                        'Failed to connect to "{}" IRC server. Waiting 3 seconds to reconnect.'.format(
                            self.name
                        ),
                        e,
                        self,
                    )
                    logger.error(error.get_log_line())
                    time.sleep(3)
                    continue

    def raw_connect(self):
        """
        Internal method, does the actual connection logic to try connecting to the server once.
        """
        # Create new socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(5)
        try:
            # Connect to socket
            self._socket.connect((self.server_address, self.server_port))
        except Exception as e:
            error = ExceptionError(
                'Connection error on "{}" IRC server'.format(self.name), e, self
            )
            logger.error(error.get_log_line())
            self.state = Server.STATE_CLOSED
            return
        # Wait for the first message back from the server.
        self.hallo.printer.output(
            "Waiting for first message from server: {}".format(self.name)
        )
        first_line = self.read_line_from_socket()
        # If first line is null, that means connection was closed.
        if first_line is None:
            raise ServerException
        self._welcome_message = first_line + "\n"
        # Send nick and full name to server
        self.hallo.printer.output(
            "Sending nick and user info to server: {}".format(self.name)
        )
        self.send_raw("NICK {}".format(self.get_nick()))
        self.send_raw("USER {}".format(self.get_full_name()))
        # Wait for MOTD to end
        while self.state == Server.STATE_CONNECTING:
            next_welcome_line = self.read_line_from_socket()
            if next_welcome_line is None:
                raise ServerException
            self._welcome_message += next_welcome_line + "\n"
            if (
                "376" in next_welcome_line
                or "endofmessage" in next_welcome_line.replace(" ", "").lower()
            ):
                break
            if next_welcome_line.split()[0] == "PING":
                self.parse_line_ping(next_welcome_line)
            if (
                len(next_welcome_line.split()[1]) == 3
                and next_welcome_line.split()[1].isdigit()
            ):
                self.parse_line_numeric(next_welcome_line, False)
        # Check we're still connecting
        if self.state != Server.STATE_CONNECTING:
            return
        # Identify with nickserv
        if self.nickserv_pass:
            ident_evt = EventMessage(
                self,
                None,
                self.get_user_by_address(
                    self.nickserv_nick.lower(), self.nickserv_nick
                ),
                "IDENTIFY {}".format(self.nickserv_pass),
                inbound=False,
            )
            self.send(ident_evt)
        # Join channels
        self.hallo.printer.output(
            "Joining channels on {}, identifying.".format(self.name)
        )
        # Join relevant channels
        for channel in self.channel_list:
            if channel.auto_join:
                self.join_channel(channel)
        self.state = Server.STATE_OPEN

    def disconnect(self, force=False):
        """
        Disconnect from the server, ensuring the run thread is ended.
        """
        if force:
            self.state = Server.STATE_CLOSED
        else:
            quit_message = "Will I dream?"
            if self.state in [Server.STATE_DISCONNECTING, Server.STATE_CLOSED]:
                print(
                    "Cannot disconnect {} server as it is not connected.".format(
                        self.name
                    )
                )
                return
            self.state = Server.STATE_DISCONNECTING
            # Logging
            for channel in self.channel_list:
                if channel.in_channel:
                    channel.set_in_channel(False)
            for user in self.user_list:
                user.set_online(False)
            try:
                quit_evt = EventQuit(self, None, quit_message, inbound=False)
                self.send(quit_evt)
            except Exception as e:
                error = ExceptionError(
                    'Failed to send quit message on "{}" IRC server'.format(self.name),
                    e,
                    self,
                )
                logger.error(error.get_log_line())
                pass
        with self._connect_lock:
            if self._socket is not None:
                self._socket.close()
            self._socket = None
        self.state = Server.STATE_CLOSED

    def reconnect(self):
        """
        Reconnect to a given server. No changes from Server base, just here for clarity
        """
        super().reconnect()

    def run(self):
        """
        Internal method
        Method to read from stream and process. Will connect and call internal parsing methods or whatnot.
        Needs to be started in it's own thread, only exits when the server connection ends
        """
        with self._connect_lock:
            self.connect()
            while self.state == Server.STATE_OPEN:
                next_line = None
                try:
                    next_line = self.read_line_from_socket()
                except ServerException as e:
                    error = ExceptionError(
                        "Server {} disconnected. Reconnecting.".format(self.name),
                        e,
                        self,
                    )
                    logger.error(error.get_log_line())
                    time.sleep(10)
                    if self.state == Server.STATE_OPEN:
                        self.disconnect()
                        self.connect()
                        print("Reconnected.")
                    continue
                if next_line is None:
                    if self.state == Server.STATE_OPEN:
                        self.disconnect()
                        self.connect()
                    continue
                else:
                    # Parse line
                    Thread(target=self.parse_line, args=(next_line,)).start()
        self.disconnect()

    def send(self, event):
        if isinstance(event, EventPing):
            self.send_raw("PONG {}".format(event.ping_number))
            event.log()
            return
        if isinstance(event, EventQuit):
            self.send_raw("QUIT :{}".format(event.quit_message))
            event.log()
            return
        if isinstance(event, EventNameChange):
            self.send_raw("NICK {}".format(event.new_name))
            event.log()
            return
        if isinstance(event, EventJoin):
            if event.password is not None:
                self.send_raw(
                    "JOIN {} {}".format(event.channel.address, event.password)
                )
            else:
                self.send_raw("JOIN {}".format(event.channel.address))
            event.log()
            return
        if isinstance(event, EventLeave):
            if event.leave_message is not None:
                self.send_raw(
                    "PART {} {}".format(event.channel.address, event.leave_message)
                )
            else:
                self.send_raw("PART {}".format(event.channel.address))
            event.log()
            return
        if isinstance(event, EventKick):
            self.send_raw(
                "KICK {} {} {}".format(
                    event.channel.address, event.kicked_user.address, event.kick_message
                )
            )
            event.log()
            return
        if isinstance(event, EventInvite):
            self.send_raw(
                "INVITE {} {}".format(event.user.address, event.channel.address)
            )
            event.log()
            return
        if isinstance(event, EventMode):
            self.send_raw(
                "MODE {} {}".format(event.channel.address, event.mode_changes)
            )
            event.log()
            return
        if isinstance(event, ChannelUserTextEvent):
            msg_type_name = "PRIVMSG"
            msg_text = event.text
            dest_addr = (
                event.user.address if event.channel is None else event.channel.address
            )
            use_caps = (
                event.user.use_caps_lock
                if event.channel is None
                else event.channel.use_caps_lock
            )
            event_class = EventMessage
            if use_caps:
                msg_text = Commons.upper(msg_text)
            if isinstance(event, EventNotice):
                event_class = EventNotice
                msg_type_name = "NOTICE"
            max_line_length = self.MAX_MSG_LENGTH - len(
                "{} {} :{}".format(msg_type_name, dest_addr, endl)
            )
            if isinstance(event, EventCTCP):
                event_class = EventCTCP
                max_line_length -= 2
            # Split and send
            for data_line in msg_text.split("\n"):
                data_line_split = Commons.chunk_string_dot(data_line, max_line_length)
                for data_line_line in data_line_split:
                    if isinstance(event, EventCTCP):
                        data_line_line = "\x01{}\x01".format(data_line_line)
                    self.send_raw(
                        "{} {} :{}".format(msg_type_name, dest_addr, data_line_line)
                    )
                    # Log sent data, if it's not message or notice
                    event = event_class(
                        event.server,
                        event.channel,
                        event.user,
                        data_line_line,
                        inbound=False,
                    )
                    event.log()
            return
        error = MessageError(
            "This event type, {}, is not currently supported to send on IRC servers".format(
                event.__class__.__name__
            )
        )
        logger.error(error.get_log_line())
        raise NotImplementedError()

    def reply(self, old_event, new_event):
        super().reply(old_event, new_event)
        # We can't do any fancy reply mechanics on IRC, so just send the event.
        self.send(new_event)

    def send_raw(self, data):
        """Sends raw data to the server
        :param data: Data to send to server
        :type data: str
        """
        if self.state != Server.STATE_CLOSED:
            self._socket.send((data + endl).encode("utf-8"))

    def join_channel(self, channel_obj):
        """Joins a specified channel
        :param channel_obj: Channel to join
        :type channel_obj: destination.Channel
        """
        # If channel isn't in channel list, add it
        if channel_obj not in self.channel_list:
            self.add_channel(channel_obj)
        # Set channel to AutoJoin, for the future
        channel_obj.auto_join = True
        # Send JOIN command
        join_evt = EventJoin(
            self, channel_obj, None, channel_obj.password, inbound=False
        )
        self.send(join_evt)

    def leave_channel(self, channel_obj):
        """
        Leaves a specified channel
        :param channel_obj: Channel to leave
        :type channel_obj: destination.Channel
        """
        super().leave_channel(channel_obj)
        # Send PART command
        self.send(EventLeave(self, channel_obj, None, None, inbound=False))

    def parse_line(self, new_line):
        """
        Parses a line from the IRC server
        :param new_line: New line of data from the server to parse
        :type new_line; str
        """
        # Cleaning up carriage returns
        new_line = new_line.replace("\r", "")
        # TODO: add stuff about time last ping was seen, for reconnection checking
        if len(new_line) < 5 or (new_line[0] != ":" and new_line[0:4] != "PING"):
            self.parse_line_unhandled(new_line)
            self.parse_line_raw(new_line, "unhandled")
        elif new_line.split()[0] == "PING":
            self.parse_line_ping(new_line)
            self.parse_line_raw(new_line, "ping")
        elif new_line.split()[1] == "PRIVMSG":
            self.parse_line_message(new_line)
            self.parse_line_raw(new_line, "message")
        elif new_line.split()[1] == "JOIN":
            self.parse_line_join(new_line)
            self.parse_line_raw(new_line, "join")
        elif new_line.split()[1] == "PART":
            self.parse_line_part(new_line)
            self.parse_line_raw(new_line, "part")
        elif new_line.split()[1] == "QUIT":
            self.parse_line_quit(new_line)
            self.parse_line_raw(new_line, "quit")
        elif new_line.split()[1] == "MODE":
            self.parse_line_mode(new_line)
            self.parse_line_raw(new_line, "mode")
        elif new_line.split()[1] == "NOTICE":
            self.parse_line_notice(new_line)
            self.parse_line_raw(new_line, "notice")
        elif new_line.split()[1] == "NICK":
            self.parse_line_nick(new_line)
            self.parse_line_raw(new_line, "nick")
        elif new_line.split()[1] == "INVITE":
            self.parse_line_invite(new_line)
            self.parse_line_raw(new_line, "invite")
        elif new_line.split()[1] == "KICK":
            self.parse_line_kick(new_line)
            self.parse_line_raw(new_line, "kick")
        elif len(new_line.split()[1]) == 3 and new_line.split()[1].isdigit():
            self.parse_line_numeric(new_line)
            self.parse_line_raw(new_line, "numeric")
        else:
            self.parse_line_unhandled(new_line)
            self.parse_line_raw(new_line, "unhandled")
        return

    def parse_line_ping(self, ping_line):
        """
        Parses a PING message from the server
        :param ping_line: Raw line to be parsed into ping event from the server
        :type ping_line: str
        """
        # Get data
        ping_number = ping_line.split()[1]
        ping_evt = EventPing(self, ping_number).with_raw_data(RawDataIRC(ping_line))
        # Respond
        pong_evt = ping_evt.get_pong()
        self.send(pong_evt)
        # Print and log
        ping_evt.log()
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(ping_evt)

    def parse_line_message(self, message_line):
        """
        Parses a PRIVMSG message from the server
        :param message_line: full privmsg line to parse from server
        :type message_line: str
        """
        # Parse out the message text
        message_text = ":".join(message_line.split(":")[2:])
        # Parse out the message sender
        message_sender_name = message_line.split("!")[0].replace(":", "")
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        message_destination_name = message_line.split()[2].lower()
        # Test for CTCP message, hand to CTCP parser if so.
        message_ctcp_bool = message_text[0] == "\x01"
        if message_ctcp_bool:
            self.parse_line_ctcp(message_line)
            return
        # Test for private message or public message.
        message_private_bool = (
            message_destination_name.lower() == self.get_nick().lower()
        )
        # Get relevant objects.
        message_sender = self.get_user_by_address(
            message_sender_name.lower(), message_sender_name
        )
        message_sender.update_activity()
        message_channel = None
        if not message_private_bool:
            message_channel = self.get_channel_by_address(
                message_destination_name.lower(), message_destination_name
            )
        # Create message event
        message_evt = EventMessage(
            self,
            None if message_private_bool else message_channel,
            message_sender,
            message_text,
        ).with_raw_data(RawDataIRC(message_line))
        # Print and Log the message
        message_evt.log()
        # Get function dispatcher ready
        function_dispatcher = self.hallo.function_dispatcher
        if message_private_bool:
            function_dispatcher.dispatch(message_evt)
        else:
            # Update channel activity
            message_channel.update_activity()
            # Send to function dispatcher, or passive dispatcher
            if message_evt.is_prefixed:
                if message_evt.is_prefixed is True:
                    function_dispatcher.dispatch(message_evt)
                else:
                    function_dispatcher.dispatch(message_evt, [message_evt.is_prefixed])
            else:
                function_dispatcher.dispatch_passive(message_evt)

    def parse_line_ctcp(self, ctcp_line):
        """
        Parses a CTCP message from the server
        :param ctcp_line: line of CTCP data to parse from the server
        :type ctcp_line: str
        """
        # Parse out the ctcp message text
        message_text = ":".join(ctcp_line.split(":")[2:])[1:-1]
        # Parse out the message sender
        message_sender_name = ctcp_line.split("!")[0].replace(":", "")
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        message_destination_name = ctcp_line.split()[2].lower()
        # Parse out the CTCP command and arguments
        message_ctcp_command = message_text.split()[0]
        message_ctcp_arguments = " ".join(message_text.split()[1:])
        # Test for private message or public message
        message_private_bool = (
            message_destination_name.lower() == self.get_nick().lower()
        )
        # Get relevant objects.
        message_channel = None
        if not message_private_bool:
            message_channel = self.get_channel_by_address(
                message_destination_name, message_destination_name
            )
            message_channel.update_activity()
        message_sender = self.get_user_by_address(
            message_sender_name.lower(), message_sender_name
        )
        message_sender.update_activity()
        ctcp_evt = EventCTCP(self, message_channel, message_sender, message_text)
        # Print and log the message
        ctcp_evt.log()
        # Reply to certain types of CTCP command
        if message_ctcp_command.lower() == "version":
            ctcp_evt.reply(
                ctcp_evt.create_response(
                    "\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01",
                    event_class=EventNotice,
                )
            )
        elif message_ctcp_command.lower() == "time":
            time_text = "\x01TIME Fribsday 15 Nov 2024 {:02d}:{:02d}:{:02d} GMT\x01".format(
                time.gmtime()[3] + 100,
                time.gmtime()[4] + 20,
                time.gmtime()[5],
            )
            ctcp_evt.reply(ctcp_evt.create_response(time_text, event_class=EventNotice))
        elif message_ctcp_command.lower() == "ping":
            ctcp_evt.reply(
                ctcp_evt.create_response(
                    "\x01PING {}\x01".format(message_ctcp_arguments),
                    event_class=EventNotice,
                )
            )
        elif message_ctcp_command.lower() == "userinfo":
            hallo_info = (
                "\x01Hello, I'm hallo, I'm a robot who does a few different things,"
                " mostly roll numbers and choose things,"
                " dr-spangle built me, if you have any questions he tends to be better at replying than I.\x01"
            )
            ctcp_evt.reply(
                ctcp_evt.create_response(hallo_info, event_class=EventNotice)
            )
        elif message_ctcp_command.lower() == "clientinfo":
            ctcp_evt.reply(
                ctcp_evt.create_response(
                    "\x01VERSION, NOTICE, TIME, USERINFO and obviously "
                    "CLIENTINFO are supported.\x01",
                    event_class=EventNotice,
                )
            )
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(ctcp_evt)

    def parse_line_join(self, join_line):
        """
        Parses a JOIN message from the server
        :param join_line: Raw line from server for the JOIN event
        :type join_line: str
        """
        # Parse out the channel and client from the JOIN data
        join_channel_name = ":".join(join_line.split(":")[2:]).lower()
        join_client_name = join_line.split("!")[0][1:]
        # Get relevant objects
        join_channel = self.get_channel_by_address(
            join_channel_name.lower(), join_channel_name
        )
        join_client = self.get_user_by_address(
            join_client_name.lower(), join_client_name
        )
        join_client.update_activity()
        # Create join event
        join_evt = EventJoin(self, join_channel, join_client).with_raw_data(
            RawDataIRC(join_line)
        )
        # Print and log
        join_evt.log()
        # TODO: Apply automatic flags as required
        # If hallo has joined a channel, get the user list and apply automatic flags as required
        if join_client.name.lower() == self.get_nick().lower():
            join_channel.set_in_channel(True)
        else:
            # If it was not hallo joining a channel, add nick to user list
            join_channel.add_user(join_client)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(join_evt)

    def parse_line_part(self, part_line):
        """
        Parses a PART message from the server
        :param part_line: Raw line from the server to parse for part event
        :type part_line: str
        """
        # Parse out channel, client and message from PART data
        part_channel_name = part_line.split()[2]
        part_client_name = part_line.split("!")[0][1:]
        part_message = ":".join(part_line.split(":")[2:])
        # Get channel and user object
        part_channel = self.get_channel_by_address(
            part_channel_name.lower(), part_channel_name
        )
        part_client = self.get_user_by_address(
            part_client_name.lower(), part_client_name
        )
        # Create leave event
        leave_evt = EventLeave(
            self, part_channel, part_client, part_message
        ).with_raw_data(RawDataIRC(part_line))
        # Print and log
        leave_evt.log()
        # Remove user from channel's user list
        part_channel.remove_user(part_client)
        # Try to work out if the user is still on the server
        # TODO: this needs to be nicer
        user_still_on_server = False
        for channel_server in self.channel_list:
            if part_client in channel_server.get_user_list():
                user_still_on_server = True
        if not user_still_on_server:
            part_client.set_online(False)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(leave_evt)

    def parse_line_quit(self, quit_line):
        """
        Parses a QUIT message from the server
        :param quit_line: Raw line from server to parse for quit event
        :type quit_line: str
        """
        # Parse client and message
        quit_client_name = quit_line.split("!")[0][1:]
        quit_message = ":".join(quit_line.split(":")[2:])
        # Get client object
        quit_client = self.get_user_by_address(
            quit_client_name.lower(), quit_client_name
        )
        # Create quit event
        quit_evt = EventQuit(self, quit_client, quit_message).with_raw_data(
            RawDataIRC(quit_line)
        )
        # Print and Log to all channels on server
        quit_evt.log()
        # Remove user from user list on all channels
        for channel in self.channel_list:
            channel.remove_user(quit_client)
        # Remove auth stuff from user
        quit_client.set_online(False)
        # If it was hallo which quit, set all channels to out of channel and all users to offline
        if quit_client.address == self.get_nick().lower():
            for channel in self.channel_list:
                channel.set_in_channel(False)
            for user in self.user_list:
                user.set_online(False)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(quit_evt)

    def parse_line_mode(self, mode_line):
        """
        Parses a MODE message from the server
        :param mode_line: Raw line of mode event to be parsed.
        :type mode_line: str
        """
        # Parsing out MODE data
        mode_channel_name = mode_line.split()[2].lower()
        mode_client_name = mode_line.split()[0][1:]
        if "!" in mode_client_name:
            mode_client_name = mode_client_name.split("!")[0]
        mode_mode = mode_line.split()[3]
        if mode_mode[0] == ":":
            mode_mode = mode_mode[1:]
        if len(mode_line.split()) >= 4:
            mode_args = " ".join(mode_line.split()[4:])
        else:
            mode_args = ""
        # Get client and channel objects
        mode_channel = self.get_channel_by_address(
            mode_channel_name.lower(), mode_channel_name
        )
        mode_client = self.get_user_by_address(
            mode_client_name.lower(), mode_client_name
        )
        # # Handling
        # If a channel password has been set, store it
        if mode_mode == "-k":
            mode_channel.password = None
        elif mode_mode == "+k":
            mode_channel.password = mode_args
        # Handle op changes
        if "o" in mode_mode:
            mode_user_name = mode_args.split()[0]
            mode_args_client = self.get_user_by_address(
                mode_user_name.lower(), mode_user_name
            )
            mode_channel.get_membership_by_user(mode_args_client).is_op = (
                mode_mode[0] == "+"
            )
        # Handle voice changes
        if "v" in mode_mode:
            mode_user_name = mode_args.split()[0]
            mode_args_client = self.get_user_by_address(
                mode_user_name.lower(), mode_user_name
            )
            mode_channel.get_membership_by_user(mode_args_client).is_voice = (
                mode_mode[0] == "+"
            )
        # Create mode event
        mode_full = mode_mode
        if mode_args != "":
            mode_full = "{} {}".format(mode_mode, mode_args)
        mode_evt = EventMode(self, mode_channel, mode_client, mode_full).with_raw_data(
            RawDataIRC(mode_line)
        )
        # # Printing and logging
        mode_evt.log()
        # # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(mode_evt)

    def parse_line_notice(self, notice_line):
        """
        Parses a NOTICE message from the server
        :param notice_line: Raw line of the NOTICE event from the server
        :type notice_line: str
        """
        # Parsing out NOTICE data
        notice_channel_name = notice_line.split()[2]
        notice_client_name = notice_line.split("!")[0][1:]
        notice_message = ":".join(notice_line.split(":")[2:])
        # Get client and channel objects
        notice_channel = self.get_channel_by_address(
            notice_channel_name.lower(), notice_channel_name
        )
        notice_channel.update_activity()
        notice_client = self.get_user_by_address(
            notice_client_name.lower(), notice_client_name
        )
        notice_client.update_activity()
        # Create notice event
        notice_event = EventNotice(
            self, notice_channel, notice_client, notice_message
        ).with_raw_data(RawDataIRC(notice_line))
        # Print to console, log to file
        notice_event.log()
        # Checking if user is registered
        if (
            notice_client.address == self.nickserv_nick
            and self._check_useridentity_user is not None
            and self.nickserv_ident_command is not None
        ):
            # check if notice message contains command and user name
            if (
                self._check_useridentity_user in notice_message
                and self.nickserv_ident_command in notice_message
            ):
                # Make regex query of identity response
                regex_ident_response = re.compile(
                    self.nickserv_ident_response, re.IGNORECASE
                )
                # check if response is in notice message
                if regex_ident_response.search(notice_message) is not None:
                    self._check_useridentity_result = True
                else:
                    self._check_useridentity_result = False
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(notice_event)

    def parse_line_nick(self, nick_line):
        """
        Parses a NICK message from the server
        :param nick_line: Line from server specifying nick change
        :type nick_line: str
        """
        # Parse out NICK change data
        nick_client_name = nick_line.split("!")[0][1:]
        if nick_line.count(":") > 1:
            nick_new_nick = nick_line.split(":")[2]
        else:
            nick_new_nick = nick_line.split()[2]
        # Get user object
        nick_client = self.get_user_by_address(
            nick_client_name.lower(), nick_client_name
        )
        # If it was the bots nick that just changed, update that.
        if nick_client.name == self.get_nick():
            self.nick = nick_new_nick
        # TODO: Check whether this verifies anything that means automatic flags need to be applied
        # Update name for user object
        nick_client.name = nick_new_nick
        nick_client.address = nick_new_nick.lower()
        # Create name change event
        chname_evt = EventNameChange(
            self, nick_client, nick_client_name, nick_new_nick
        ).with_raw_data(RawDataIRC(nick_line))
        # Printing and logging
        chname_evt.log()
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(chname_evt)

    def parse_line_invite(self, invite_line):
        """
        Parses an INVITE message from the server
        :param invite_line: Line from the server specifying invite event
        :type invite_line: str
        """
        # Parse out INVITE data
        inviter_client_name = invite_line.split("!")[0][1:]
        invite_channel_name = ":".join(invite_line.split(":")[2:])
        invited_client_name = invite_line.split()[2]
        # Get destination objects
        inviter_client = self.get_user_by_address(
            inviter_client_name.lower(), inviter_client_name
        )
        inviter_client.update_activity()
        invited_client = self.get_user_by_address(
            invited_client_name.lower(), invited_client_name
        )
        invite_channel = self.get_channel_by_address(
            invite_channel_name.lower(), invite_channel_name
        )
        # Create invite event
        invite_evt = EventInvite(
            self, invite_channel, inviter_client, invited_client
        ).with_raw_data(RawDataIRC(invite_line))
        # Printing and logging
        invite_evt.log()
        # Check if they are an op, then join the channel.
        if (
            inviter_client.rights_check("invite_channel", invite_channel)
            and invited_client_name == self.get_nick()
        ):
            self.join_channel(invite_channel)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(invite_evt)

    def parse_line_kick(self, kick_line):
        """
        Parses a KICK message from the server
        :param kick_line: Line from the server specifying kick event
        :type kick_line: str
        """
        # Parse out KICK data
        kick_channel_name = kick_line.split()[2]
        kicked_client_name = kick_line.split()[3]
        kick_message = ":".join(kick_line.split(":")[2:])
        kicking_user_name = kick_line.split("!")[0][1:]
        # GetObjects
        kick_channel = self.get_channel_by_address(
            kick_channel_name.lower(), kick_channel_name
        )
        kicked_client = self.get_user_by_address(
            kicked_client_name.lower(), kicked_client_name
        )
        kicking_client = self.get_user_by_address(
            kicking_user_name.lower(), kicking_user_name
        )
        # Create kick event
        kick_evt = EventKick(
            self, kick_channel, kicking_client, kicked_client, kick_message
        ).with_raw_data(RawDataIRC(kick_line))
        # Log, if applicable
        kick_evt.log()
        # Remove kicked user from user list
        kick_channel.remove_user(kicked_client)
        # If it was the bot who was kicked, set "in channel" status to False
        if kicked_client.name == self.get_nick():
            kick_channel.set_in_channel(False)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(kick_evt)

    def parse_line_numeric(self, numeric_line, motd_ended=True):
        """
        Parses a numeric message from the server
        :param numeric_line: Numeric type line from server.
        :type numeric_line: str
        :param motd_ended: Whether MOTD has ended.
        :type motd_ended: bool
        """
        # Parse out numeric line data
        numeric_code = numeric_line.split()[1]
        # Print to console
        self.hallo.printer.output(
            "[{}] Numeric server info: {}".format(self.name, numeric_line)
        )
        # TODO: add logging?
        # Check for a 433 "ERR_NICKNAMEINUSE"
        if numeric_code == "433":
            nick_num_suffixes = [
                self.nick[x:]
                for x in range(len(self.nick))
                if Commons.is_float_string(self.nick[x:])
            ]
            nick_numstr = nick_num_suffixes[0] if len(nick_num_suffixes) > 0 else None
            if nick_numstr is None:
                nick_number = 0
                nick_word = self.nick
            else:
                nick_word = self.nick[: -len(nick_numstr)]
                nick_number = float(nick_numstr)
            new_nick = nick_word + str(nick_number + 1)
            self.set_nick(new_nick)
            return
        # Only process further numeric codes if motd has ended
        if not motd_ended:
            return
        # Check for ISON response, telling you which users are online
        if numeric_code == "303":
            # Parse out data
            users_online = ":".join(numeric_line.split(":")[2:])
            users_online_list = users_online.split()
            # Mark them all as online
            for user_name in users_online_list:
                user_obj = self.get_user_by_address(user_name.lower(), user_name)
                user_obj.set_online(True)
            # Check if users are being checked
            if all([users_online_list in self._check_usersonline_check_list]):
                self._check_usersonline_online_list = users_online_list
        # Check for NAMES request reply, telling you who is in a channel.
        elif numeric_code == "353":
            # Parse out data
            channel_name = numeric_line.split(":")[1].split()[-1].lower()
            channel_user_list = ":".join(numeric_line.split(":")[2:])
            # Get channel object
            channel_obj = self.get_channel_by_address(
                channel_name.lower(), channel_name
            )
            # Set all users online and in channel
            self.handle_user_list(channel_obj, channel_user_list)
            # Check if channel is being checked
            if channel_obj == self._check_channeluserlist_channel:
                # Check is complete
                self._check_channeluserlist_done = True

    def parse_line_unhandled(self, unhandled_line):
        """
        Parses an unhandled message from the server
        :param unhandled_line: Otherwise unhandled line from the server
        :type unhandled_line: str
        """
        # Print it to console
        error = MessageError(
            'Unhandled data received on "{}" IRC server: {}'.format(
                self.name, unhandled_line
            )
        )
        logger.error(error.get_log_line())

    def parse_line_raw(self, raw_line, line_type):
        """Handed all raw data, along with the type of message
        :param raw_line: Raw line from the server
        :type raw_line: str
        :param line_type: Event or type of the line
        :type line_type: str
        """
        pass

    def read_line_from_socket(self):
        """
        Private method to read a line from the IRC socket.
        :return: A line of text from the socket
        :rtype: str
        """
        next_line = b""
        while self.state != Server.STATE_CLOSED:
            next_byte = None
            try:
                next_byte = self._socket.recv(1)
            except socket.timeout as e:
                if e.args[0] != "timed out":
                    raise ServerException("Failed to receive byte. {}".format(e))
            except Exception as e:
                # Raise an exception, to reconnect.
                raise ServerException("Failed to receive byte. {}".format(e))
            if next_byte is None:
                continue
            if len(next_byte) != 1:
                raise ServerException(
                    "Length of next byte incorrect: {}".format(next_byte)
                )
            next_line += next_byte
            if next_line.endswith(endl.encode()):
                return self.decode_line(next_line[: -len(endl)])

    def decode_line(self, raw_bytes):
        """
        Decodes a line of bytes, trying a couple character sets
        :param raw_bytes: Array bytes to be decoded to string.
        :type raw_bytes: bytearray | bytes
        """
        try:
            output_line = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                output_line = raw_bytes.decode("iso-8859-1")
            except UnicodeDecodeError:
                output_line = raw_bytes.decode("cp1252")
        return output_line

    def check_channel_user_list(self, channel_obj):
        """
        Checks and updates the user list of a specified channel
        :param channel_obj: Channel to check user list of
        :type channel_obj: destination.Channel
        """
        # get lock
        self._check_channeluserlist_lock.acquire()
        try:
            self._check_channeluserlist_channel = channel_obj
            self._check_channeluserlist_done = False
            # send request
            self.send_raw("NAMES {}".format(channel_obj.name))
            # loop for 5 seconds
            for _ in range(10):
                # sleep 0.5seconds
                time.sleep(0.5)
                # if reply is here
                if self._check_channeluserlist_done:
                    break
            # return
            return
        finally:
            self._check_channeluserlist_channel = None
            self._check_channeluserlist_done = False
            self._check_channeluserlist_lock.release()

    def check_users_online(self, check_user_list):
        """
        Checks a list of users to see which are online, returns a list of online users
        :param check_user_list: List of names of users to check online status of
        :type check_user_list: list
        """
        # get lock
        self._check_usersonline_lock.acquire()
        try:
            self._check_usersonline_check_list = check_user_list
            self._check_usersonline_online_list = None
            # send request
            self.send_raw("ISON {}".format(" ".join(check_user_list)))
            # loop for 5 seconds
            for _ in range(10):
                # if reply is here
                if self._check_usersonline_online_list is not None:
                    # use response
                    for user_name in self._check_usersonline_check_list:
                        user_obj = self.get_user_by_address(
                            user_name.lower(), user_name
                        )
                        if user_name in self._check_usersonline_online_list:
                            user_obj.set_online(True)
                        else:
                            user_obj.set_online(False)
                    # return response
                    response = self._check_usersonline_online_list
                    return response
                # sleep 0.5 seconds
                time.sleep(0.5)
            # return empty list
            return []
        finally:
            # release lock
            self._check_usersonline_check_list = None
            self._check_usersonline_online_list = None
            self._check_usersonline_lock.release()

    def check_user_identity(self, user_obj):
        """
        Check if a user is identified and verified
        :param user_obj: User to check identity and verification for
        """
        if self.nickserv_nick is None or self.nickserv_ident_command is None:
            return False
        # get nickserv object
        nickserv_obj = self.get_user_by_address(
            self.nickserv_nick.lower(), self.nickserv_nick
        )
        # get check user lock
        self._check_useridentity_lock.acquire()
        try:
            self._check_useridentity_user = user_obj.address
            self._check_useridentity_result = None
            # send whatever request
            self.send(
                EventMessage(
                    self,
                    None,
                    nickserv_obj,
                    "{} {}".format(self.nickserv_ident_command, user_obj.address),
                    inbound=False,
                )
            )
            # loop for 5 seconds
            for _ in range(10):
                # if response
                if self._check_useridentity_result is not None:
                    # return
                    response = self._check_useridentity_result
                    return response
                # sleep 0.5
                time.sleep(0.5)
            # return false
            return False
        finally:
            # release lock
            self._check_useridentity_user = None
            self._check_useridentity_result = None
            self._check_useridentity_lock.release()

    def handle_user_list(self, channel, user_name_list):
        """
        Takes a user list line from the server, either by NAMES response or after joining a channel, and processes it,
        setting the right users in the right channel.
        :param channel: Channel the user list is for
        :type channel: Channel
        :param user_name_list: string containing a list of users, space separated, with flags
        :type user_name_list: str
        """
        user_object_list = set()
        for user_name in user_name_list.split():
            # Strip flags from user name
            flags = ""
            while user_name[0] in ["~", "&", "@", "%", "+"]:
                user_name = user_name[1:]
                flags += user_name[0]
            # Add user if not exists.
            user_obj = self.get_user_by_address(user_name.lower(), user_name)
            user_obj.set_online(True)
            chan_membership = ChannelMembership(channel, user_obj)
            channel.memberships_list.add(chan_membership)
            # Set voice and op on membership
            channel.get_membership_by_user(user_obj).is_voice = "+" in flags
            channel.get_membership_by_user(user_obj).is_op = "@" in flags
            # Add to list of users in channel
            user_object_list.add(user_obj)
        # Remove all users from channel membership which are not in user list
        remove_users = [
            user for user in channel.get_user_list() if user not in user_object_list
        ]
        for user in remove_users:
            channel.remove_user(user)

    def set_nick(self, nick):
        """
        Nick setter
        :param nick: New nickname to use on the server
        """
        old_nick = self.get_nick()
        # Update my user object
        hallo_user = self.get_user_by_address(old_nick.lower(), old_nick)
        hallo_user.name = nick
        hallo_user.address = nick.lower()
        self.nick = nick
        if nick != old_nick:
            nick_evt = EventNameChange(self, hallo_user, old_nick, nick, inbound=False)
            self.send(nick_evt)

    def get_server_port(self):
        """server_port getter"""
        return self.server_port

    def get_nickserv_nick(self):
        """nickserv_nick getter"""
        return self.nickserv_nick

    def set_nickserv_nick(self, nickserv_nick):
        """
        nickserv_nick setter
        :param nickserv_nick: Nickname of the nickserv service on this server
        :type nickserv_nick: str | None
        """
        self.nickserv_nick = nickserv_nick

    def get_nickserv_ident_command(self):
        """nickserv_ident_command getter"""
        return self.nickserv_ident_command

    def set_nickserv_ident_command(self, nickserv_ident_command):
        """
        nickserv_ident_command setter
        :param nickserv_ident_command: Command to identify to nickserv service on this server
        :type nickserv_ident_command: str
        """
        self.nickserv_ident_command = nickserv_ident_command

    def get_nickserv_ident_response(self):
        """nickserv_ident_response getter"""
        return self.nickserv_ident_response

    def set_nickserv_ident_response(self, nickserv_ident_response):
        """
        nickserv_ident_response setter
        :param nickserv_ident_response: Regex to search for to validate identity in response to identify command
        :type nickserv_ident_response: str
        """
        self.nickserv_ident_response = nickserv_ident_response

    def get_nickserv_pass(self):
        """nickserv_pass getter"""
        return self.nickserv_pass

    def set_nickserv_pass(self, nickserv_pass):
        """
        nickserv_pass setter
        :param nickserv_pass: Nickserv password for hallo to identify
        :type nickserv_pass: str | None
        """
        self.nickserv_pass = nickserv_pass
        if self.nickserv_pass is not None:
            nickserv_obj = self.get_user_by_address(
                self.nickserv_nick.lower(), self.nickserv_nick
            )
            self.send(
                EventMessage(
                    self,
                    None,
                    nickserv_obj,
                    "IDENTIFY {}".format(self.nickserv_pass),
                    inbound=False,
                )
            )

    def get_name_by_address(self, address):
        return address

    def to_json(self):
        json_obj = dict()
        json_obj["type"] = Server.TYPE_IRC
        json_obj["name"] = self.name
        json_obj["auto_connect"] = self.auto_connect
        json_obj["channels"] = []
        for channel in self.channel_list:
            json_obj["channels"].append(channel.to_json())
        json_obj["users"] = []
        for user in self.user_list:
            json_obj["users"].append(user.to_json())
        if self.nick is not None:
            json_obj["nick"] = self.nick
        if self.prefix is not None:
            json_obj["prefix"] = self.prefix
        if not self.permission_mask.is_empty():
            json_obj["permission_mask"] = self.permission_mask.to_json()
        json_obj["address"] = self.server_address
        json_obj["port"] = self.server_port
        if self.full_name is not None:
            json_obj["full_name"] = self.full_name
        if self.nickserv_pass is not None:
            json_obj["nickserv"] = {}  # TODO
            json_obj["nickserv"]["nick"] = self.nickserv_nick
            json_obj["nickserv"]["password"] = self.nickserv_pass
            json_obj["nickserv"]["identity_command"] = self.nickserv_ident_command
            json_obj["nickserv"]["identity_response"] = self.nickserv_ident_response
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        name = json_obj["name"]
        address = json_obj["address"]
        port = json_obj["port"]
        new_server = ServerIRC(hallo, name, address, port)
        new_server.auto_connect = json_obj["auto_connect"]
        if "full_name" in json_obj:
            new_server.full_name = json_obj["full_name"]
        if "nickserv" in json_obj:
            new_server.nickserv_nick = json_obj["nickserv"]["nick"]
            new_server.nickserv_pass = json_obj["nickserv"]["password"]
            new_server.nickserv_ident_command = json_obj["nickserv"]["identity_command"]
            new_server.nickserv_ident_response = json_obj["nickserv"][
                "identity_response"
            ]
        if "nick" in json_obj:
            new_server.nick = json_obj["nick"]
        if "prefix" in json_obj:
            new_server.prefix = json_obj["prefix"]
        for channel in json_obj["channels"]:
            new_server.add_channel(Channel.from_json(channel, new_server))
        for user in json_obj["users"]:
            new_server.add_user(User.from_json(user, new_server))
        if "permission_mask" in json_obj:
            new_server.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        return new_server
