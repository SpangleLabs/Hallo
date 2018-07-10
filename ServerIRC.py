import re
import socket
import time
from threading import RLock, Lock, Thread
from typing import Optional
from xml.dom import minidom

from Destination import ChannelMembership, Channel, User
from Function import Function
from PermissionMask import PermissionMask
from Server import Server, ServerException
from inc.Commons import Commons

endl = Commons.END_LINE


class ServerIRC(Server):
    MAX_MSG_LENGTH = 462
    type = Server.TYPE_IRC

    def __init__(self, hallo, server_name=None, server_url=None, server_port=6667):
        """
        Constructor for server object
        :param hallo: Hallo instance which owns this server
        :type hallo: Hallo.Hallo
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
        self.nickserv_nick = "nickserv"  # Nickserv's nick, None if nickserv does not exist
        self.nickserv_ident_command = "STATUS"  # Command to send to nickserv to check if a user is identified
        self.nickserv_ident_response = "\\b3\\b"  # Regex to search for to validate identity in response to IdentCommand
        # IRC specific dynamic variables
        self._socket = None  # Socket to communicate to the server
        self._welcome_message = ""  # Server's welcome message when connecting. MOTD and all.
        self._check_channeluserlist_lock = Lock()  # Thread lock for checking a channel's user list
        self._check_channeluserlist_channel = None  # Channel to check user list of
        self._check_channeluserlist_done = False  # Whether the check is complete
        self._check_usersonline_lock = Lock()  # Thread lock for checking which users are online
        self._check_usersonline_check_list = None  # List of users' names to check
        self._check_usersonline_online_list = None  # List of users' names who are online
        self._check_useridentity_lock = Lock()  # Thread lock for checking if a user is identified with nickserv
        self._check_useridentity_user = None  # User name which is being checked
        self._check_useridentity_result = None  # Boolean, whether or not the user is identified
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
            while self.state == Server.STATE_CONNECTING:
                try:
                    self.raw_connect()
                    return
                except ServerException as e:
                    print("Failed to connect. ("+str(e)+") Waiting 3 seconds before reconnect.")
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
            print("CONNECTION ERROR: " + str(e))
            self.state = Server.STATE_CLOSED
        # Wait for the first message back from the server.
        print(Commons.current_timestamp() + " waiting for first message from server: " + self.name)
        first_line = self.read_line_from_socket()
        # If first line is null, that means connection was closed.
        if first_line is None:
            raise ServerException
        self._welcome_message = first_line + "\n"
        # Send nick and full name to server
        print(Commons.current_timestamp() + " sending nick and user info to server: " + self.name)
        self.send('NICK ' + self.get_nick(), None, self.MSG_RAW)
        self.send('USER ' + self.get_full_name(), None, self.MSG_RAW)
        # Wait for MOTD to end
        while self.state == Server.STATE_CONNECTING:
            next_welcome_line = self.read_line_from_socket()
            if next_welcome_line is None:
                raise ServerException
            self._welcome_message += next_welcome_line + "\n"
            if "376" in next_welcome_line or "endofmessage" in next_welcome_line.replace(' ', '').lower():
                break
            if next_welcome_line.split()[0] == "PING":
                self.parse_line_ping(next_welcome_line)
            if len(next_welcome_line.split()[1]) == 3 and next_welcome_line.split()[1].isdigit():
                self.parse_line_numeric(next_welcome_line, False)
        # Check we're still connecting
        if self.state != Server.STATE_CONNECTING:
            return
        # Identify with nickserv
        if self.nickserv_pass:
            self.send('IDENTIFY ' + self.nickserv_pass, self.get_user_by_name("nickserv"))
        # Join channels
        print(Commons.current_timestamp() + " joining channels on " + self.name + ", identifying.")
        # Join relevant channels
        for channel in self.channel_list:
            if channel.is_auto_join():
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
                print("Cannot disconnect "+str(self.name)+" server as it is not connected.")
                return
            self.state = Server.STATE_DISCONNECTING
            # Logging
            for channel in self.channel_list:
                if channel.is_in_channel():
                    self.hallo.get_logger().log(Function.EVENT_QUIT,
                                                quit_message,
                                                self,
                                                self.get_user_by_name(self.get_nick()),
                                                channel)
                    channel.set_in_channel(False)
            for user in self.user_list:
                user.set_online(False)
            try:
                self.send("QUIT :" + quit_message, None, self.MSG_RAW)
            except Exception as e:
                print("Failed to send quit message. "+str(e))
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
                    print("Server \""+str(self.name)+"\" disconnected. ("+str(e)+") Reconnecting.")
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

    def send(self, data, destination_obj=None, msg_type=Server.MSG_MSG):
        """
        Sends a message to the server, or a specific channel in the server
        :param data: Line of data to send to server
        :type data: str
        :param destination_obj: Destination to send data to
        :type destination_obj: Destination.Destination or None
        :param msg_type: Type of message which is being sent
        :type msg_type: str
        """
        if msg_type not in [self.MSG_MSG, self.MSG_NOTICE, self.MSG_RAW]:
            msg_type = self.MSG_MSG
        # If it's raw data, just send it.
        if destination_obj is None or msg_type == self.MSG_RAW:
            for data_line in data.split("\n"):
                self.send_raw(data_line)
            return
        # Get message type
        if msg_type == self.MSG_NOTICE:
            msg_type_name = "NOTICE"
        else:
            msg_type_name = "PRIVMSG"
        # Get channel or user name and data
        destination_name = destination_obj.get_name()
        channel_obj = None
        user_obj = destination_obj
        if destination_obj.is_channel():
            channel_obj = destination_obj
            user_obj = None
        # Find out if destination wants caps lock
        if destination_obj.is_upper_case():
            data = Commons.upper(data)
        # Get max line length
        max_line_length = self.MAX_MSG_LENGTH - len(msg_type_name + ' ' + destination_name + ' :' + endl)
        # Split and send
        for data_line in data.split("\n"):
            data_line_split = Commons.chunk_string_dot(data_line, max_line_length)
            for date_line_line in data_line_split:
                self.send_raw(msg_type_name + ' ' + destination_name + ' :' + date_line_line)
                # Log sent data, if it's not message or notice
                if msg_type == self.MSG_MSG:
                    self.hallo.get_printer().output_from_self(Function.EVENT_MESSAGE, date_line_line, self, user_obj,
                                                              channel_obj)
                    self.hallo.get_logger().log_from_self(Function.EVENT_MESSAGE, date_line_line, self, user_obj,
                                                          channel_obj)
                elif msg_type == self.MSG_NOTICE:
                    self.hallo.get_printer().output_from_self(Function.EVENT_NOTICE, date_line_line, self, user_obj,
                                                              channel_obj)
                    self.hallo.get_logger().log_from_self(Function.EVENT_NOTICE, date_line_line, self, user_obj,
                                                          channel_obj)

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
        :type channel_obj: Destination.Channel
        """
        # If channel isn't in channel list, add it
        if channel_obj not in self.channel_list:
            self.add_channel(channel_obj)
        # Set channel to AutoJoin, for the future
        channel_obj.set_auto_join(True)
        # Send JOIN command
        if channel_obj.get_password() is None:
            self.send('JOIN ' + channel_obj.get_name(), None, self.MSG_RAW)
        else:
            self.send('JOIN ' + channel_obj.get_name() + ' ' + channel_obj.get_password(), None, self.MSG_RAW)

    def leave_channel(self, channel_obj):
        """
        Leaves a specified channel
        :param channel_obj: Channel to leave
        :type channel_obj: Destination.Channel
        """
        super().leave_channel(channel_obj)
        # Send PART command
        self.send('PART ' + channel_obj.get_name(), None, self.MSG_RAW)

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
        # Respond
        self.send("PONG " + ping_number, None, self.MSG_RAW)
        # Print and log
        self.hallo.get_printer().output(Function.EVENT_PING, ping_number, self, None, None)
        self.hallo.get_printer().output_from_self(Function.EVENT_PING, ping_number, self, None, None)
        self.hallo.get_logger().log(Function.EVENT_PING, ping_number, self, None, None)
        self.hallo.get_logger().log_from_self(Function.EVENT_PING, ping_number, self, None, None)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_PING, ping_number, self, None, None)

    def parse_line_message(self, message_line):
        """
        Parses a PRIVMSG message from the server
        :param message_line: full privmsg line to parse from server
        :type message_line: str
        """
        # Parse out the message text
        message_text = ':'.join(message_line.split(':')[2:])
        # Parse out the message sender
        message_sender_name = message_line.split('!')[0].replace(':', '')
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        message_destination_name = message_line.split()[2].lower()
        # Test for CTCP message, hand to CTCP parser if so.
        message_ctcp_bool = message_text[0] == '\x01'
        if message_ctcp_bool:
            self.parse_line_ctcp(message_line)
            return
        # Test for private message or public message.
        message_private_bool = message_destination_name.lower() == self.get_nick().lower()
        # Get relevant objects.
        message_sender = self.get_user_by_name(message_sender_name)
        message_sender.update_activity()
        message_destination = message_sender
        # Get function dispatcher ready
        function_dispatcher = self.hallo.get_function_dispatcher()
        if message_private_bool:
            # Print and Log the private message
            self.hallo.get_printer().output(Function.EVENT_MESSAGE, message_text, self, message_sender, None)
            self.hallo.get_logger().log(Function.EVENT_MESSAGE, message_text, self, message_sender, None)
            function_dispatcher.dispatch(message_text, message_sender, message_destination)
        else:
            message_channel = self.get_channel_by_name(message_destination_name)
            # Print and Log the public message
            self.hallo.get_printer().output(Function.EVENT_MESSAGE, message_text, self, message_sender, message_channel)
            self.hallo.get_logger().log(Function.EVENT_MESSAGE, message_text, self, message_sender, message_channel)
            # Update channel activity
            message_channel.update_activity()
            # Get acting command prefix
            acting_prefix = message_channel.get_prefix()
            # Figure out if the message is a command, Send to FunctionDispatcher
            if acting_prefix is False:
                acting_prefix = self.get_nick().lower()
                # Check if directly addressed
                if any(message_text.lower().startswith(acting_prefix+x) for x in [":", ","]):
                    message_text = message_text[len(acting_prefix) + 1:]
                    function_dispatcher.dispatch(message_text,
                                                 message_sender,
                                                 message_channel)
                elif message_text.lower().startswith(acting_prefix):
                    message_text = message_text[len(acting_prefix):]
                    function_dispatcher.dispatch(message_text,
                                                 message_sender,
                                                 message_channel,
                                                 [function_dispatcher.FLAG_HIDE_ERRORS])
                else:
                    # Pass to passive function checker
                    function_dispatcher.dispatch_passive(Function.EVENT_MESSAGE,
                                                         message_text,
                                                         self,
                                                         message_sender,
                                                         message_channel)
            elif message_text.lower().startswith(acting_prefix):
                message_text = message_text[len(acting_prefix):]
                function_dispatcher.dispatch(message_text,
                                             message_sender,
                                             message_channel)
            else:
                # Pass to passive function checker
                function_dispatcher.dispatch_passive(Function.EVENT_MESSAGE,
                                                     message_text,
                                                     self,
                                                     message_sender,
                                                     message_channel)

    def parse_line_ctcp(self, ctcp_line):
        """
        Parses a CTCP message from the server
        :param ctcp_line: line of CTCP data to parse from the server
        :type ctcp_line: str
        """
        # Parse out the ctcp message text
        message_text = ':'.join(ctcp_line.split(':')[2:])[1:-1]
        # Parse out the message sender
        message_sender_name = ctcp_line.split('!')[0].replace(':', '')
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        message_destination_name = ctcp_line.split()[2].lower()
        # Parse out the CTCP command and arguments
        message_ctcp_command = message_text.split()[0]
        message_ctcp_arguments = ' '.join(message_text.split()[1:])
        # Test for private message or public message
        message_private_bool = message_destination_name.lower() == self.get_nick().lower()
        message_public_bool = not message_private_bool
        # Get relevant objects.
        message_channel = None
        if message_public_bool:
            message_channel = self.get_channel_by_name(message_destination_name)
            message_channel.update_activity()
        message_sender = self.get_user_by_name(message_sender_name)
        message_sender.update_activity()
        # Print and log the message
        if message_private_bool:
            self.hallo.get_printer().output(Function.EVENT_CTCP, message_text, self, message_sender, None)
            self.hallo.get_logger().log(Function.EVENT_CTCP, message_text, self, message_sender, None)
        else:
            self.hallo.get_printer().output(Function.EVENT_CTCP, message_text, self, message_sender, message_channel)
            self.hallo.get_logger().log(Function.EVENT_CTCP, message_text, self, message_sender, message_channel)
        # Reply to certain types of CTCP command
        if message_ctcp_command.lower() == 'version':
            self.send("\x01VERSION Hallobot:vX.Y:An IRC bot by dr-spangle.\x01", message_sender, self.MSG_NOTICE)
        elif message_ctcp_command.lower() == 'time':
            self.send("\x01TIME Fribsday 15 Nov 2024 " + str(time.gmtime()[3] + 100).rjust(2, '0') + ":" + str(
                time.gmtime()[4] + 20).rjust(2, '0') + ":" + str(time.gmtime()[5]).rjust(2, '0') + "GMT\x01",
                      message_sender, self.MSG_NOTICE)
        elif message_ctcp_command.lower() == 'ping':
            self.send('\x01PING ' + message_ctcp_arguments + '\x01', message_sender, self.MSG_NOTICE)
        elif message_ctcp_command.lower() == 'userinfo':
            hallo_info = "Hello, I'm hallo, I'm a robot who does a few different things," \
                         " mostly roll numbers and choose things," \
                         " occasionally giving my input on who is the best pony." \
                         " dr-spangle built me, if you have any questions he tends to be better at replying than I."
            self.send("\x01" + hallo_info + "\x01", message_sender, self.MSG_NOTICE)
        elif message_ctcp_command.lower() == 'clientinfo':
            self.send('\x01VERSION, NOTICE, TIME, USERINFO and obviously CLIENTINFO are supported.\x01', message_sender,
                      self.MSG_NOTICE)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_CTCP, message_text, self, message_sender, message_channel)

    def parse_line_join(self, join_line):
        """
        Parses a JOIN message from the server
        :param join_line: Raw line from server for the JOIN event
        :type join_line: str
        """
        # Parse out the channel and client from the JOIN data
        join_channel_name = ':'.join(join_line.split(':')[2:]).lower()
        join_client_name = join_line.split('!')[0][1:]
        # Get relevant objects
        join_channel = self.get_channel_by_name(join_channel_name)
        join_client = self.get_user_by_name(join_client_name)
        join_client.update_activity()
        # Print and log
        self.hallo.get_printer().output(Function.EVENT_JOIN, None, self, join_client, join_channel)
        self.hallo.get_logger().log(Function.EVENT_JOIN, None, self, join_client, join_channel)
        # TODO: Apply automatic flags as required
        # If hallo has joined a channel, get the user list and apply automatic flags as required
        if join_client.name.lower() == self.get_nick().lower():
            join_channel.set_in_channel(True)
        else:
            # If it was not hallo joining a channel, add nick to user list
            join_channel.add_user(join_client)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(Function.EVENT_JOIN, None, self, join_client, join_channel)

    def parse_line_part(self, part_line):
        """
        Parses a PART message from the server
        :param part_line: Raw line from the server to parse for part event
        :type part_line: str
        """
        # Parse out channel, client and message from PART data
        part_channel_name = part_line.split()[2]
        part_client_name = part_line.split('!')[0][1:]
        part_message = ':'.join(part_line.split(':')[2:])
        # Get channel and user object
        part_channel = self.get_channel_by_name(part_channel_name)
        part_client = self.get_user_by_name(part_client_name)
        # Print and log
        self.hallo.get_printer().output(Function.EVENT_LEAVE, part_message, self, part_client, part_channel)
        self.hallo.get_logger().log(Function.EVENT_LEAVE, part_message, self, part_client, part_channel)
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
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_LEAVE, part_message, self, part_client, part_channel)

    def parse_line_quit(self, quit_line):
        """
        Parses a QUIT message from the server
        :param quit_line: Raw line from server to parse for quit event
        :type quit_line: str
        """
        # Parse client and message
        quit_client_name = quit_line.split('!')[0][1:]
        quit_message = ':'.join(quit_line.split(':')[2:])
        # Get client object
        quit_client = self.get_user_by_name(quit_client_name)
        # Print and Log to all channels on server
        self.hallo.get_printer().output(Function.EVENT_QUIT, quit_message, self, quit_client, Commons.ALL_CHANNELS)
        for channel in self.channel_list:
            self.hallo.get_logger().log(Function.EVENT_QUIT, quit_message, self, quit_client, channel)
        # Remove user from user list on all channels
        for channel in self.channel_list:
            channel.remove_user(quit_client)
        # Remove auth stuff from user
        quit_client.set_online(False)
        # If it was hallo which quit, set all channels to out of channel and all users to offline
        if quit_client.get_name().lower() == self.get_nick().lower():
            for channel in self.channel_list:
                channel.set_in_channel(False)
            for user in self.user_list:
                user.set_online(False)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_QUIT, quit_message, self, quit_client, None)

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
            mode_args = ' '.join(mode_line.split()[4:])
        else:
            mode_args = ''
        # Get client and channel objects
        mode_channel = self.get_channel_by_name(mode_channel_name)
        mode_client = self.get_user_by_name(mode_client_name)
        # # Handling
        # If a channel password has been set, store it
        if mode_mode == '-k':
            mode_channel.set_password(None)
        elif mode_mode == '+k':
            mode_channel.set_password(mode_args)
        # Handle op changes
        if "o" in mode_mode:
            mode_user_name = mode_args.split()[0]
            mode_args_client = self.get_user_by_name(mode_user_name)
            mode_channel.get_membership_by_user(mode_args_client).is_op = (mode_mode[0] == "+")
        # Handle voice changes
        if "v" in mode_mode:
            mode_user_name = mode_args.split()[0]
            mode_args_client = self.get_user_by_name(mode_user_name)
            mode_channel.get_membership_by_user(mode_args_client).is_voice = (mode_mode[0] == "+")
        # # Printing and logging
        mode_full = mode_mode
        if mode_args != '':
            mode_full = mode_mode + ' ' + mode_args
        self.hallo.get_printer().output(Function.EVENT_MODE, mode_full, self, mode_client, mode_channel)
        self.hallo.get_logger().log(Function.EVENT_MODE, mode_full, self, mode_client, mode_channel)
        # # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_MODE, mode_full, self, mode_client, mode_channel)

    def parse_line_notice(self, notice_line):
        """
        Parses a NOTICE message from the server
        :param notice_line: Raw line of the NOTICE event from the server
        :type notice_line: str
        """
        # Parsing out NOTICE data
        notice_channel_name = notice_line.split()[2]
        notice_client_name = notice_line.split('!')[0][1:]
        notice_message = ':'.join(notice_line.split(':')[2:])
        # Get client and channel objects
        notice_channel = self.get_channel_by_name(notice_channel_name)
        notice_channel.update_activity()
        notice_client = self.get_user_by_name(notice_client_name)
        notice_client.update_activity()
        # Print to console, log to file
        self.hallo.get_printer().output(Function.EVENT_NOTICE, notice_message, self, notice_client, notice_channel)
        self.hallo.get_logger().log(Function.EVENT_NOTICE, notice_message, self, notice_client, notice_channel)
        # Checking if user is registered
        if notice_client.get_name() == self.nickserv_nick and \
                self._check_useridentity_user is not None and \
                self.nickserv_ident_command is not None:
            # check if notice message contains command and user name
            if self._check_useridentity_user in notice_message and self.nickserv_ident_command in notice_message:
                # Make regex query of identity response
                regex_ident_response = re.compile(self.nickserv_ident_response, re.IGNORECASE)
                # check if response is in notice message
                if regex_ident_response.search(notice_message) is not None:
                    self._check_useridentity_result = True
                else:
                    self._check_useridentity_result = False
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_NOTICE, notice_message, self, notice_client, notice_channel)

    def parse_line_nick(self, nick_line):
        """
        Parses a NICK message from the server
        :param nick_line: Line from server specifying nick change
        :type nick_line: str
        """
        # Parse out NICK change data
        nick_client_name = nick_line.split('!')[0][1:]
        if nick_line.count(':') > 1:
            nick_new_nick = nick_line.split(':')[2]
        else:
            nick_new_nick = nick_line.split()[2]
        # Get user object
        nick_client = self.get_user_by_name(nick_client_name)
        # If it was the bots nick that just changed, update that.
        if nick_client.get_name() == self.get_nick():
            self.nick = nick_new_nick
        # TODO: Check whether this verifies anything that means automatic flags need to be applied
        # Update name for user object
        nick_client.set_name(nick_new_nick)
        # Printing and logging
        self.hallo.get_printer().output(Function.EVENT_CHNAME, nick_client_name, self, nick_client,
                                        Commons.ALL_CHANNELS)
        for channel in self.channel_list:
            self.hallo.get_logger().log(Function.EVENT_CHNAME, nick_client_name, self, nick_client, channel)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_CHNAME, nick_client_name, self, nick_client, None)

    def parse_line_invite(self, invite_line):
        """
        Parses an INVITE message from the server
        :param invite_line: Line from the server specifying invite event
        :type invite_line: str
        """
        # Parse out INVITE data
        invite_client_name = invite_line.split('!')[0][1:]
        invite_channel_name = ':'.join(invite_line.split(':')[2:])
        # Get destination objects
        invite_client = self.get_user_by_name(invite_client_name)
        invite_client.update_activity()
        invite_channel = self.get_channel_by_name(invite_channel_name)
        # Printing and logging
        self.hallo.get_printer().output(Function.EVENT_INVITE, None, self, invite_client, invite_channel)
        self.hallo.get_logger().log(Function.EVENT_INVITE, None, self, invite_client, invite_channel)
        # Check if they are an op, then join the channel.
        if invite_client.rights_check("invite_channel", invite_channel):
            self.join_channel(invite_channel)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_INVITE, None, self, invite_client, invite_channel)

    def parse_line_kick(self, kick_line):
        """
        Parses a KICK message from the server
        :param kick_line: Line from the server specifying kick event
        :type kick_line: str
        """
        # Parse out KICK data
        kick_channel_name = kick_line.split()[2]
        kick_client_name = kick_line.split()[3]
        kick_message = ':'.join(kick_line.split(':')[4:])
        # GetObjects
        kick_channel = self.get_channel_by_name(kick_channel_name)
        kick_client = self.get_user_by_name(kick_client_name)
        # Log, if applicable
        self.hallo.get_printer().output(Function.EVENT_KICK, kick_message, self, kick_client, kick_channel)
        self.hallo.get_logger().log(Function.EVENT_KICK, kick_message, self, kick_client, kick_channel)
        # Remove kicked user from user list
        kick_channel.remove_user(kick_client)
        # If it was the bot who was kicked, set "in channel" status to False
        if kick_client.get_name() == self.get_nick():
            kick_channel.set_in_channel(False)
        # Pass to passive FunctionDispatcher
        function_dispatcher = self.hallo.get_function_dispatcher()
        function_dispatcher.dispatch_passive(Function.EVENT_KICK, kick_message, self, kick_client, kick_channel)

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
        print(Commons.current_timestamp() + ' [' + self.name + '] Numeric server info: ' + numeric_line)
        # TODO: add logging?
        # Check for a 433 "ERR_NICKNAMEINUSE"
        if numeric_code == "433":
            nick_numstr = (
                    [self.nick[x:] for x in range(len(self.nick)) if Commons.is_float_string(self.nick[x:])]
                    + [None])[0]  # type: Optional[str]
            if nick_numstr is None:
                nick_number = 0
                nick_word = self.nick
            else:
                nick_word = self.nick[:-len(nick_numstr)]
                nick_number = float(nick_numstr)
            new_nick = nick_word + str(nick_number + 1)
            self.nick = new_nick
            self.send("NICK" + self.get_nick(), None, self.MSG_RAW)
            return
        # Only process further numeric codes if motd has ended
        if not motd_ended:
            return
        # Check for ISON response, telling you which users are online
        if numeric_code == "303":
            # Parse out data
            users_online = ':'.join(numeric_line.split(':')[2:])
            users_online_list = users_online.split()
            # Mark them all as online
            for user_name in users_online_list:
                user_obj = self.get_user_by_name(user_name)
                user_obj.set_online(True)
            # Check if users are being checked
            if all([users_online_list in self._check_usersonline_check_list]):
                self._check_usersonline_online_list = users_online_list
        # Check for NAMES request reply, telling you who is in a channel.
        elif numeric_code == "353":
            # Parse out data
            channel_name = numeric_line.split(':')[1].split()[-1].lower()
            channel_user_list = ':'.join(numeric_line.split(':')[2:])
            # Get channel object
            channel_obj = self.get_channel_by_name(channel_name)
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
        print(Commons.current_timestamp() + ' [' + self.name + '] Unhandled data: ' + unhandled_line)

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
                    raise ServerException("Failed to receive byte. "+str(e))
            except Exception as e:
                # Raise an exception, to reconnect.
                raise ServerException("Failed to receive byte. "+str(e))
            if next_byte is None:
                continue
            if len(next_byte) != 1:
                raise ServerException("Length of next byte incorrect: " + str(next_byte))
            next_line += next_byte
            if next_line.endswith(endl.encode()):
                return self.decode_line(next_line[:-len(endl)])

    def decode_line(self, raw_bytes):
        """
        Decodes a line of bytes, trying a couple character sets
        :param raw_bytes: Array bytes to be decoded to string.
        :type raw_bytes: bytearray
        """
        try:
            output_line = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                output_line = raw_bytes.decode('iso-8859-1')
            except UnicodeDecodeError:
                output_line = raw_bytes.decode('cp1252')
        return output_line

    def check_channel_user_list(self, channel_obj):
        """
        Checks and updates the user list of a specified channel
        :param channel_obj: Channel to check user list of
        :type channel_obj: Destination.Channel
        """
        # get lock
        self._check_channeluserlist_lock.acquire()
        try:
            self._check_channeluserlist_channel = channel_obj
            self._check_channeluserlist_done = False
            # send request
            self.send("NAMES " + channel_obj.name, None, Server.MSG_RAW)
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
            self.send("ISON " + " ".join(check_user_list), None, Server.MSG_RAW)
            # loop for 5 seconds
            for _ in range(10):
                # if reply is here
                if self._check_usersonline_online_list is not None:
                    # use response
                    for user_name in self._check_usersonline_check_list:
                        user_obj = self.get_user_by_name(user_name)
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
        nickserv_obj = self.get_user_by_name(self.nickserv_nick)
        # get check user lock
        self._check_useridentity_lock.acquire()
        try:
            self._check_useridentity_user = user_obj.get_name()
            self._check_useridentity_result = None
            # send whatever request
            self.send(self.nickserv_ident_command + " " + user_obj.get_name(), nickserv_obj, Server.MSG_MSG)
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
            while user_name[0] in ['~', '&', '@', '%', '+']:
                user_name = user_name[1:]
                flags += user_name[0]
            # Add user if not exists.
            user_obj = self.get_user_by_name(user_name)
            user_obj.set_online(True)
            chan_membership = ChannelMembership(channel, user_obj)
            channel.memberships_list.add(chan_membership)
            # Set voice and op on membership
            channel.get_membership_by_user(user_obj).is_voice = "+" in flags
            channel.get_membership_by_user(user_obj).is_op = "@" in flags
            # Add to list of users in channel
            user_object_list.add(user_obj)
        # Remove all users from channel membership which are not in user list
        remove_users = [user for user in channel.get_user_list() if user not in user_object_list]
        for user in remove_users:
            channel.remove_user(user)

    def to_xml(self):
        """
        Returns an XML representation of the server object
        """
        # create document
        doc = minidom.Document()
        # create root element
        root = doc.createElement("server")
        doc.appendChild(root)
        # create type element
        type_elem = doc.createElement("server_type")
        type_elem.appendChild(doc.createTextNode(self.get_type()))
        root.appendChild(type_elem)
        # create name element
        name_elem = doc.createElement("server_name")
        name_elem.appendChild(doc.createTextNode(self.name))
        root.appendChild(name_elem)
        # create auto connect element
        auto_connect_elem = doc.createElement("auto_connect")
        auto_connect_elem.appendChild(doc.createTextNode(Commons.BOOL_STRING_DICT[self.auto_connect]))
        root.appendChild(auto_connect_elem)
        # create channel list
        channel_list_elem = doc.createElement("channel_list")
        for channel_obj in self.channel_list:
            if channel_obj.is_persistent():
                channel_elem = minidom.parseString(channel_obj.to_xml()).firstChild
                channel_list_elem.appendChild(channel_elem)
        root.appendChild(channel_list_elem)
        # create user list
        user_list_elem = doc.createElement("user_list")
        for user_obj in self.user_list:
            if user_obj.is_persistent():
                user_elem = minidom.parseString(user_obj.to_xml()).firstChild
                user_list_elem.appendChild(user_elem)
        root.appendChild(user_list_elem)
        # create nick element
        if self.nick is not None:
            nick_elem = doc.createElement("server_nick")
            nick_elem.appendChild(doc.createTextNode(self.nick))
            root.appendChild(nick_elem)
        # create prefix element
        if self.prefix is not None:
            prefix_elem = doc.createElement("server_prefix")
            prefix_elem.appendChild(doc.createTextNode(self.prefix))
            root.appendChild(prefix_elem)
        # create full name element
        if self.full_name is not None:
            full_name_elem = doc.createElement("full_name")
            full_name_elem.appendChild(doc.createTextNode(self.full_name))
            root.appendChild(full_name_elem)
        # create server address element
        server_url_elem = doc.createElement("server_address")
        server_url_elem.appendChild(doc.createTextNode(self.server_address))
        root.appendChild(server_url_elem)
        # create server port element
        server_port_elem = doc.createElement("server_port")
        server_port_elem.appendChild(doc.createTextNode(str(self.server_port)))
        root.appendChild(server_port_elem)
        # Create nickserv element
        if self.nickserv_nick is not None:
            nickserv_elem = doc.createElement("nickserv")
            # Nickserv nick element
            nickserv_nick_elem = doc.createElement("nick")
            nickserv_nick_elem.appendChild(doc.createTextNode(self.nickserv_nick))
            nickserv_elem.appendChild(nickserv_nick_elem)
            # Nickserv password element
            if self.nickserv_pass is not None:
                nickserv_pass_elem = doc.createElement("password")
                nickserv_pass_elem.appendChild(doc.createTextNode(self.nickserv_pass))
                nickserv_elem.appendChild(nickserv_pass_elem)
            # Nickserv identity check command element
            if self.nickserv_ident_command is not None:
                nickserv_ident_command_elem = doc.createElement("identity_command")
                nickserv_ident_command_elem.appendChild(doc.createTextNode(self.nickserv_ident_command))
                nickserv_elem.appendChild(nickserv_ident_command_elem)
                # Nickserv identity check response element
                nickserv_ident_response_elem = doc.createElement("identity_response")
                nickserv_ident_response_elem.appendChild(doc.createTextNode(self.nickserv_ident_response))
                nickserv_elem.appendChild(nickserv_ident_response_elem)
            # Add nickserv element to document
            root.appendChild(nickserv_elem)
        # create permission_mask element
        if not self.permission_mask.is_empty():
            permission_mask_elem = minidom.parse(self.permission_mask.to_xml()).firstChild
            root.appendChild(permission_mask_elem)
        # output XML string
        return doc.toxml()

    def set_nick(self, nick):
        """
        Nick setter
        :param nick: New nickname to use on the server
        """
        old_nick = self.get_nick()
        self.nick = nick
        if nick != old_nick:
            self.send("NICK " + self.nick, None, self.MSG_RAW)
            hallo_user_obj = self.get_user_by_name(nick)
            # Log in all channel Hallo is in.
            for channel in self.channel_list:
                if not channel.is_in_channel():
                    continue
                self.hallo.get_logger().log_from_self(Function.EVENT_CHNAME, old_nick, self, hallo_user_obj, channel)

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
            self.send('IDENTIFY ' + self.nickserv_pass, self.get_user_by_name("nickserv"))

    @staticmethod
    def from_xml(xml_string, hallo):
        """
        Constructor to build a new server object from xml
        :param xml_string: XML string representation of IRC server configuration
        :param hallo: Hallo object which is connected to this server
        """
        doc = minidom.parseString(xml_string)
        new_server = ServerIRC(hallo)
        new_server.name = doc.getElementsByTagName("server_name")[0].firstChild.data
        new_server.auto_connect = Commons.string_from_file(doc.getElementsByTagName("auto_connect")[0].firstChild.data)
        if len(doc.getElementsByTagName("server_nick")) != 0:
            new_server.nick = doc.getElementsByTagName("server_nick")[0].firstChild.data
        if len(doc.getElementsByTagName("server_prefix")) != 0:
            new_server.prefix = doc.getElementsByTagName("server_prefix")[0].firstChild.data
        if len(doc.getElementsByTagName("full_name")) != 0:
            new_server.full_name = doc.getElementsByTagName("full_name")[0].firstChild.data
        new_server.server_address = doc.getElementsByTagName("server_address")[0].firstChild.data
        new_server.server_port = int(doc.getElementsByTagName("server_port")[0].firstChild.data)
        if len(doc.getElementsByTagName("nickserv")) == 0:
            new_server.nickserv_nick = None
            new_server.nickserv_pass = None
            new_server.nickserv_ident_command = None
            new_server.nickserv_ident_response = None
        else:
            nickserv_elem = doc.getElementsByTagName("nickserv")[0]
            new_server.nickserv_nick = nickserv_elem.getElementsByTagName("nick")[0].firstChild.data
            if len(nickserv_elem.getElementsByTagName("identity_command")) == 0:
                new_server.nickserv_ident_command = None
                new_server.nickserv_ident_response = None
            else:
                new_server.nickserv_ident_command = nickserv_elem.getElementsByTagName("identity_command")[
                    0].firstChild.data
                new_server.nickserv_ident_response = nickserv_elem.getElementsByTagName("identity_response")[
                    0].firstChild.data
            if len(nickserv_elem.getElementsByTagName("password")) != 0:
                new_server.nickserv_pass = nickserv_elem.getElementsByTagName("password")[0].firstChild.data
        # Load channels
        channel_list_elem = doc.getElementsByTagName("channel_list")[0]
        for channel_elem in channel_list_elem.getElementsByTagName("channel"):
            channel_obj = Channel.from_xml(channel_elem.toxml(), new_server)
            new_server.add_channel(channel_obj)
        # Load users
        user_list_elem = doc.getElementsByTagName("user_list")[0]
        for user_elem in user_list_elem.getElementsByTagName("user"):
            user_obj = User.from_xml(user_elem.toxml(), new_server)
            new_server.add_user(user_obj)
        if len(doc.getElementsByTagName("permission_mask")) != 0:
            new_server.permission_mask = PermissionMask.from_xml(doc.getElementsByTagName("permission_mask")[0].toxml())
        return new_server

