from threading import Lock, Thread

import telegram
from telegram import Chat
from telegram.ext import Updater, Filters, BaseFilter
import logging
from telegram.ext import MessageHandler
from telegram.utils.request import Request

from Destination import User, Channel
from Events import EventMessage, RawDataTelegram
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
        # Create Event object
        message_evt = EventMessage(self, None, message_sender, message_text).with_raw_data(RawDataTelegram(update))
        # Print and Log the private message
        self.hallo.printer.output(message_evt)
        self.hallo.logger.log(message_evt)
        self.hallo.function_dispatcher.dispatch(message_evt)

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
        # Create message event object
        message_evt = EventMessage(self, message_channel, message_sender, message_text)\
            .with_raw_data(RawDataTelegram(update))
        # Print and Log the public message
        self.hallo.printer.output(message_evt)
        self.hallo.logger.log(message_evt)
        # Send event to function dispatcher or passive dispatcher
        if message_evt.is_prefixed:
            if message_evt.is_prefixed is True:
                function_dispatcher.dispatch(message_evt)
            else:
                function_dispatcher.dispatch(message_evt, [message_evt.is_prefixed])
        else:
            function_dispatcher.dispatch_passive(message_evt)

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

    def send(self, event):
        if isinstance(event, EventMessage):
            destination = event.user if event.channel is None else event.channel
            self.bot.send_message(chat_id=destination.address, text=event.text)
            self.hallo.printer.output(event)
            self.hallo.logger.log(event)
        else:
            print("This event type, {}, is not currently supported to send on Telegram servers",
                  event.__class__.__name__)
            raise NotImplementedError()

    def reply(self, old_event, new_event):
        """
        :type old_event: Events.ChannelUserTextEvent
        :param new_event:
        :return:
        """
        # Do checks
        super().reply(old_event, new_event)
        if old_event.raw_data is None or not isinstance(old_event.raw_data, RawDataTelegram):
            raise ServerException("Old event has no telegram data associated with it")
        if isinstance(new_event, EventMessage):
            old_event.raw_data.update_obj.message.reply_text(new_event.text)
            self.hallo.printer.output(new_event)
            self.hallo.logger.log(new_event)
        else:
            print("This event type, {}, is not currently supported to send on Telegram servers",
                  new_event.__class__.__name__)
            raise NotImplementedError()

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
        new_server = ServerTelegram(hallo, api_key)
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
