from threading import Lock, Thread
from xml.dom import minidom

import telegram
from telegram import Chat
from telegram.ext import Updater, Filters, BaseFilter
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
        self.name = "Telegram"  # Server name #TODO: needs to be configurable!
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
        # Message handlers
        self.private_msg_handler = MessageHandler(Filters.private, self.parse_private_message)
        self.dispatcher.add_handler(self.private_msg_handler)
        self.group_msg_handler = MessageHandler(Filters.group, self.parse_group_message)
        self.dispatcher.add_handler(self.group_msg_handler)
        # Catch-all message handler for anything not already handled.
        self.core_msg_handler = MessageHandler(Filters.all, self.parse_unhandled, channel_post_updates=True)
        self.dispatcher.add_handler(self.core_msg_handler)

    class ChannelFilter(BaseFilter):
        def filter(self, message):
            return message.chat.type in [Chat.CHANNEL]

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

    def parse_private_message(self, bot, update):
        """
        Handles a new private message
        :param bot: telegram bot object
        :type bot: telegram.Bot
        :param update: Update object from telegram API
        :type update: telegram.Update
        """
        # Parse out the message text
        message_text = update.message.text
        # Parse out the message sender
        message_sender_name = " ".join([update.message.chat.first_name, update.message.chat.last_name])
        # Parser message sender address
        message_sender_addr = update.message.chat.id
        # Get relevant objects.
        message_sender = self.get_user_by_address(message_sender_addr, message_sender_name)
        message_sender.update_activity()
        # Print and Log the private message
        self.hallo.printer.output(Function.EVENT_MESSAGE, message_text, self, message_sender, None)
        self.hallo.logger.log(Function.EVENT_MESSAGE, message_text, self, message_sender, None)
        self.hallo.function_dispatcher.dispatch(message_text, message_sender, message_sender)

    def parse_group_message(self, bot, update):
        """
        Handles a new group or supergroup message (does not handle channel posts)
        :param bot: telegram bot object
        :type bot: telegram.Bot
        :param update: Update object from telegram API
        :type update: telegram.Update
        """
        # Parse out the message text
        message_text = update.message.text
        # Parse out the message sender
        message_sender_name = " ".join([update.message.from_user.first_name, update.message.from_user.last_name])
        # Parser message sender address
        message_sender_addr = update.message.from_user.id
        # Test for private message or public message.
        # Parse out where the message went to (e.g. channel or private message to Hallo)
        message_destination_name = update.message.chat.title
        message_destination_addr = update.message.chat.id
        # Get relevant objects.
        message_sender = self.get_user_by_address(message_sender_addr, message_sender_name)
        message_sender.update_activity()
        # Get function dispatcher ready
        function_dispatcher = self.hallo.function_dispatcher
        message_channel = self.get_channel_by_address(message_destination_addr, message_destination_name)
        message_channel.update_activity()
        # Print and Log the public message
        self.hallo.printer.output(Function.EVENT_MESSAGE, message_text, self, message_sender, message_channel)
        self.hallo.logger.log(Function.EVENT_MESSAGE, message_text, self, message_sender, message_channel)
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

    def parse_unhandled(self, bot, update):
        """
        Parses an unhandled message from the server
        :param bot: telegram bot object
        :type bot: telegram.Bot
        :param update: Update object from telegram API
        :type update: telegram.Update
        """
        # Print it to console
        print("{} [{}] Unhandled data: {}".format(Commons.current_timestamp(), self.name, update))

    def send(self, data, destination_obj=None, msg_type=Server.MSG_MSG):
        self.bot.send_message(chat_id=destination_obj.address, text=data)
        user_obj = destination_obj if isinstance(destination_obj, User) else None
        channel_obj = destination_obj if isinstance(destination_obj, Channel) else None
        self.hallo.printer.output_from_self(Function.EVENT_MESSAGE, data, self, user_obj, channel_obj)
        self.hallo.logger.log_from_self(Function.EVENT_MESSAGE, data, self, user_obj, channel_obj)

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
        type_elem.appendChild(doc.createTextNode(self.type))
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

    def to_json(self):
        """
        Creates a dict of configuration for the server, to store as json
        :return: dict
        """
        json_obj = dict()
        json_obj["type"] = Server.TYPE_TELEGRAM
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
        json_obj["api_key"] = self.api_key
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        api_key = json_obj["api_key"]
        new_server = ServerTelegram(api_key, hallo)
        new_server.name = json_obj["name"]
        new_server.auto_connect = json_obj["auto_connect"]
        if "nick" in json_obj:
            new_server.nick = json_obj["nick"]
        if "prefix" in json_obj:
            new_server.prefix = json_obj["prefix"]
        if "permission_mask" in json_obj:
            new_server.permission_mask = PermissionMask.from_json(json_obj["permission_mask"])
        for channel in json_obj["channels"]:
            new_server.add_channel(Channel.from_json(channel, new_server))
        for user in json_obj["users"]:
            new_server.add_user(User.from_json(user, new_server))
        return new_server

    def join_channel(self, channel_obj):
        pass
        # TODO

    def check_user_identity(self, user_obj):
        return True
