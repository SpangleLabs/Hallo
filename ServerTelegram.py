from threading import Lock, Thread
from xml.dom import minidom

import telegram
from telegram.ext import Updater, Filters
import logging
from telegram.ext import MessageHandler
from telegram.utils.request import Request

from Destination import User, Channel
from Function import Function
from PermissionMask import PermissionMask
from Server import Server, ServerException
from inc.Commons import Commons


class ServerTelegram(Server):

    def __init__(self, hallo, api_key):
        super().__init__(hallo)
        """
        Constructor for server object
        :param hallo: Hallo Instance of hallo that contains this server object
        :type hallo: Hallo.Hallo
        """
        self.hallo = hallo  # The hallo object that created this server
        # Persistent/saved class variables
        self.api_key = api_key
        self.name = "Telegram"  # Server name
        self.auto_connect = True  # Whether to automatically connect to this server when hallo starts
        self.channel_list = []  # List of channels on this server (which may or may not be currently active)
        self.user_list = []  # Users on this server (not all of which are online)
        self.nick = None  # Nickname to use on this server
        self.prefix = None  # Prefix to use with functions on this server
        self.full_name = None  # Full name to use on this server
        self.permission_mask = PermissionMask()  # PermissionMask for the server
        # Dynamic/unsaved class variables
        self.state = Server.STATE_CLOSED  # Current state of the server, replacing open
        self._connect_lock = Lock()
        request = Request(con_pool_size=8)
        self.bot = telegram.Bot(token=self.api_key, request=request)
        self.bot.logger.setLevel(logging.INFO)
        self.updater = Updater(bot=self.bot)
        self.dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
        self.core_msg_handler = MessageHandler(Filters.all, self.parse_update, channel_post_updates=True)
        self.dispatcher.add_handler(self.core_msg_handler)

    def start(self):
        """
        Starts up the server and launches the new thread
        """
        if self.state != Server.STATE_CLOSED:
            raise ServerException("Already started.")
        self.state = Server.STATE_CONNECTING
        with self._connect_lock:
            Thread(target=self.connect).start()

    def connect(self):
        """
        Internal method
        Method to read from stream and process. Will connect and call internal parsing methods or whatnot.
        Needs to be started in it's own thread, only exits when the server connection ends
        """
        with self._connect_lock:
            self.updater.start_polling()
            self.state = Server.STATE_OPEN

    def disconnect(self, force=False):
        self.state = Server.STATE_DISCONNECTING
        with self._connect_lock:
            self.updater.stop()
            self.state = Server.STATE_CLOSED

    def reconnect(self):
        super().reconnect()

    def parse_update(self, bot, update):
        if update.message is not None:
            # Check if it's a normal message
            if update.message.text is not None:
                return self.parse_message(bot, update)
            # Check if it's a group add
            if update.message.new_chat_members is not None and len(update.message.new_chat_members) == 0:
                return self.parse_join(bot, update)
        # TODO Else log to file and report maybe?

    def parse_message(self, bot, update):
        """
        Handles a new update object from the server
        :param bot: telegram bot object
        :type bot: telegram.Bot
        :param update: Update object from telegram API
        :type update: telegram.Update
        """
        # Parse out the message text
        message_text = update.message.text
        # Parse out the message sender
        message_sender_name = update.message.chat.username
        # Test for private message or public message.
        message_private_bool = update.message.chat.type == "private"
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        message_destination_name = None
        if not message_private_bool:
            message_destination_name = update.message.chat.title
        # Get relevant objects.
        message_sender = self.get_user_by_name(message_sender_name)
        message_sender.update_activity()
        message_sender.telegram_chat_id = update.message.chat.id
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

    def parse_join(self, bot, update):
        # TODO
        pass

    def send(self, data, destination_obj=None, msg_type=Server.MSG_MSG):
        if destination_obj.is_channel():
            # TODO
            pass
        else:
            self.bot.send_message(chat_id=destination_obj.telegram_chat_id, text=data)

    @staticmethod
    def from_xml(xml_string, hallo):
        """
        Constructor to build a new server object from xml
        :param xml_string: XML string representation of telegram server configuration
        :param hallo: Hallo object which is connected to this server
        """
        doc = minidom.parseString(xml_string)
        api_key = doc.getElementsByTagName("server_api_key")[0].firstChild.data
        new_server = ServerTelegram(hallo, api_key)
        new_server.auto_connect = Commons.string_from_file(doc.getElementsByTagName("auto_connect")[0].firstChild.data)
        if len(doc.getElementsByTagName("server_nick")) != 0:
            new_server.nick = doc.getElementsByTagName("server_nick")[0].firstChild.data
        if len(doc.getElementsByTagName("server_prefix")) != 0:
            new_server.prefix = doc.getElementsByTagName("server_prefix")[0].firstChild.data
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
        # create server API key element
        key_elem = doc.createElement("server_api_key")
        key_elem.appendChild(doc.createTextNode(self.api_key))
        root.appendChild(key_elem)
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
        # create permission_mask element
        if not self.permission_mask.is_empty():
            permission_mask_elem = minidom.parse(self.permission_mask.to_xml()).firstChild
            root.appendChild(permission_mask_elem)
        # output XML string
        return doc.toxml()

    def join_channel(self, channel_obj):
        pass
        # TODO

    def check_user_identity(self, user_obj):
        return True
