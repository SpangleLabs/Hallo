from threading import Lock, Thread
from typing import Optional, TYPE_CHECKING, Dict

import telegram
from telegram import Chat, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, Update, Message, TelegramError
from telegram.ext import Updater, Filters, BaseFilter, CallbackQueryHandler, CallbackContext
import logging
from telegram.ext import MessageHandler
from telegram.utils.request import Request

from hallo.destination import User, Channel
from hallo.errors import MessageError
from hallo.events import (
    EventMessage,
    RawDataTelegram,
    EventMessageWithPhoto,
    RawDataTelegramOutbound, EventMenuCallback, ServerEvent, ChannelUserTextEvent,
)
from hallo.permission_mask import PermissionMask
from hallo.server import Server, ServerException

if TYPE_CHECKING:
    from hallo.hallo import Hallo


logger = logging.getLogger(__name__)


def event_menu_for_telegram(event: EventMessage) -> Optional[InlineKeyboardMarkup]:
    if not event.menu_buttons:
        return None
    menu = []
    for row in event.menu_buttons:
        menu.append([
            InlineKeyboardButton(button.text, callback_data=button.data)
            for button in row
        ])
    return InlineKeyboardMarkup(menu)


def formatting_to_telegram_mode(event_formatting: EventMessage.Formatting) -> Optional[str]:
    return {
        EventMessage.Formatting.MARKDOWN: telegram.ParseMode.MARKDOWN,
        EventMessage.Formatting.HTML: telegram.ParseMode.HTML,
    }.get(event_formatting)


class ServerTelegram(Server):

    type = Server.TYPE_TELEGRAM
    image_extensions = ["jpg", "jpeg", "png"]

    def __init__(self, hallo: 'Hallo', api_key: str) -> None:
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
        self.auto_connect = (
            True  # Whether to automatically connect to this server when hallo starts
        )
        self.channel_list = (
            []
        )  # List of channels on this server (which may or may not be currently active)
        """ :type : list[Destination.Channel]"""
        self.user_list = []  # Users on this server (not all of which are online)
        """ :type : list[Destination.User]"""
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
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.ERROR,
        )
        # Message handlers
        self.private_msg_handler = MessageHandler(
            Filters.private, self.parse_private_message
        )
        self.dispatcher.add_handler(self.private_msg_handler)
        self.group_msg_handler = MessageHandler(Filters.group, self.parse_group_message)
        self.dispatcher.add_handler(self.group_msg_handler)
        callback_handler = CallbackQueryHandler(self.parse_menu_callback)
        self.dispatcher.add_handler(callback_handler)
        # Catch-all message handler for anything not already handled.
        self.core_msg_handler = MessageHandler(
            Filters.all, self.parse_unhandled, channel_post_updates=True
        )
        self.dispatcher.add_handler(self.core_msg_handler)

    class ChannelFilter(BaseFilter):
        def filter(self, message: Message) -> bool:
            return message.chat.type in [Chat.CHANNEL]

    def start(self) -> None:
        """
        Starts up the server and launches the new thread
        """
        if self.state != Server.STATE_CLOSED:
            raise ServerException("Already started.")
        self.state = Server.STATE_CONNECTING
        with self._connect_lock:
            Thread(target=self.connect).start()

    def connect(self) -> None:
        """
        Internal method
        Method to read from stream and process. Will connect and call internal parsing methods or whatnot.
        Needs to be started in it's own thread, only exits when the server connection ends
        """
        with self._connect_lock:
            self.updater.start_polling()
            self.state = Server.STATE_OPEN

    def disconnect(self, force: bool = False) -> None:
        self.state = Server.STATE_DISCONNECTING
        with self._connect_lock:
            self.updater.stop()
            self.state = Server.STATE_CLOSED

    def reconnect(self) -> None:
        super().reconnect()

    def parse_private_message(self, update: Update, context: CallbackContext) -> None:
        """
        Handles a new private message
        :param update: Update object from telegram API
        :type update: telegram.Update
        :param context: Callback Context from the telegram API
        :type context: telegram.CallbackContext
        """
        # Get sender object
        telegram_chat = update.message.chat
        names_list = [telegram_chat.first_name, telegram_chat.last_name]
        message_sender_name = " ".join(
            [name for name in names_list if name is not None]
        )
        message_sender_addr = update.message.chat.id
        message_sender = self.get_user_by_address(
            message_sender_addr, message_sender_name
        )
        message_sender.update_activity()
        # Create Event object
        if update.message.photo:
            photo_id = update.message.photo[-1]["file_id"]
            message_text = update.message.caption or ""
            message_evt = EventMessageWithPhoto(
                self, None, message_sender, message_text, photo_id
            ).with_raw_data(RawDataTelegram(update))
        else:
            message_text = update.message.text
            message_evt = EventMessage(
                self, None, message_sender, message_text
            ).with_raw_data(RawDataTelegram(update))
        # Print and Log the private message
        message_evt.log()
        self.hallo.function_dispatcher.dispatch(message_evt)

    def parse_group_message(self, update: Update, context: CallbackContext) -> None:
        """
        Handles a new group or supergroup message (does not handle channel posts)
        :param update: Update object from telegram API
        :param context: Callback Context from the telegram API
        """
        # Get sender object
        message_sender_name = " ".join(
            [update.message.from_user.first_name, update.message.from_user.last_name]
        )
        message_sender_addr = update.message.from_user.id
        message_sender = self.get_user_by_address(
            message_sender_addr, message_sender_name
        )
        message_sender.update_activity()
        # Get channel object
        message_channel_name = update.message.chat.title
        message_channel_addr = update.message.chat.id
        message_channel = self.get_channel_by_address(
            message_channel_addr, message_channel_name
        )
        message_channel.update_activity()
        # Create message event object
        if update.message.photo:
            photo_id = update.message.photo[-1]["file_id"]
            message_text = update.message.caption or ""
            message_evt = EventMessageWithPhoto(
                self, message_channel, message_sender, message_text, photo_id
            ).with_raw_data(RawDataTelegram(update))
        else:
            message_text = update.message.text
            message_evt = EventMessage(
                self, message_channel, message_sender, message_text
            ).with_raw_data(RawDataTelegram(update))
        # Print and log the public message
        message_evt.log()
        # Send event to function dispatcher or passive dispatcher
        function_dispatcher = self.hallo.function_dispatcher
        if message_evt.is_prefixed:
            if message_evt.is_prefixed is True:
                function_dispatcher.dispatch(message_evt)
            else:
                function_dispatcher.dispatch(message_evt, [message_evt.is_prefixed])
        else:
            function_dispatcher.dispatch_passive(message_evt)

    def parse_join(self, update: Update, context: CallbackContext) -> None:
        # TODO
        pass

    def parse_menu_callback(self, update: Update, context: CallbackContext) -> None:
        # Get sender object
        message_sender_name = update.effective_user.full_name
        message_sender_addr = update.effective_user.id
        message_sender = self.get_user_by_address(
            message_sender_addr, message_sender_name
        )
        message_sender.update_activity()
        # Get channel object
        message_channel_name = update.effective_chat.title
        message_channel_addr = update.effective_chat.id
        if message_channel_addr == message_sender_addr:
            message_channel = None
        else:
            message_channel = self.get_channel_by_address(
                message_channel_addr, message_channel_name
            )
            message_channel.update_activity()
        # Create message event object
        message_id = update.effective_message.message_id
        callback_data = update.callback_query.data
        callback_evt = EventMenuCallback(
            self, message_channel, message_sender, message_id, callback_data
        ).with_raw_data(RawDataTelegram(update))
        # Print and log the public message
        callback_evt.log()
        # Send event to function dispatcher or passive dispatcher
        function_dispatcher = self.hallo.function_dispatcher
        function_dispatcher.dispatch_passive(callback_evt)

    def parse_unhandled(self, update: Update, context: CallbackContext) -> None:
        """
        Parses an unhandled message from the server
        :param update: Update object from telegram API
        :param context: Callback Context from the telegram API
        """
        # Print it to console
        error = MessageError(
            "Unhandled data received on Telegram server: {}".format(update)
        )
        logger.error(error.get_log_line())

    def send(self, event: ServerEvent) -> Optional[ServerEvent]:
        if isinstance(event, EventMessageWithPhoto):
            destination = event.destination
            try:
                if isinstance(event.photo_id, list):
                    media = [InputMediaPhoto(x) for x in event.photo_id]
                    media[0].caption = event.text
                    media[0].parse_mode = formatting_to_telegram_mode(event.formatting)
                    msg = self.bot.send_media_group(
                        chat_id=destination.address, media=media
                    )
                elif any(
                    [
                        event.photo_id.lower().endswith("." + x)
                        for x in ServerTelegram.image_extensions
                    ]
                ):
                    msg = self.bot.send_photo(
                        chat_id=destination.address,
                        photo=event.photo_id,
                        caption=event.text,
                        reply_markup=event_menu_for_telegram(event),
                        parse_mode=formatting_to_telegram_mode(event.formatting),
                    )
                else:
                    msg = self.bot.send_document(
                        chat_id=destination.address,
                        document=event.photo_id,
                        caption=event.text,
                        reply_markup=event_menu_for_telegram(event),
                        parse_mode=formatting_to_telegram_mode(event.formatting),
                    )
            except Exception as e:
                logger.warning(
                    "Failed to send message with picture. Sending without. Picture path %s", event.photo_id, exc_info=e
                )
                msg = self.bot.send_message(
                    chat_id=destination.address,
                    text=event.text,
                    reply_markup=event_menu_for_telegram(event),
                    parse_mode=formatting_to_telegram_mode(event.formatting)
                )
            event.with_raw_data(RawDataTelegramOutbound(msg))
            event.log()
            return event
        if isinstance(event, EventMessage):
            msg = self.bot.send_message(
                chat_id=event.destination.address,
                text=event.text,
                parse_mode=formatting_to_telegram_mode(event.formatting),
                reply_markup=event_menu_for_telegram(event)
            )
            event.with_raw_data(RawDataTelegramOutbound(msg))
            event.log()
            return event
        else:
            error = MessageError(
                "Unsupported event type, {}, sent to Telegram server".format(
                    event.__class__.__name__
                )
            )
            logger.error(error.get_log_line())
            raise NotImplementedError()

    def reply(self, old_event: EventMessage, new_event: EventMessage) -> EventMessage:
        """
        :type old_event: events.ChannelUserTextEvent
        :param new_event:
        :return:
        """
        # Do checks
        super().reply(old_event, new_event)
        if old_event.raw_data is None or not isinstance(
            old_event.raw_data, RawDataTelegram
        ):
            raise ServerException("Old event has no telegram data associated with it")
        # Send event
        if isinstance(new_event, EventMessageWithPhoto):
            destination = new_event.destination
            old_message_id = old_event.raw_data.update_obj.message.message_id
            if any(
                [
                    new_event.photo_id.lower().endswith("." + x)
                    for x in ServerTelegram.image_extensions
                ]
            ):
                msg = self.bot.send_photo(
                    destination.address,
                    new_event.photo_id,
                    caption=new_event.text,
                    reply_to_message_id=old_message_id,
                    reply_markup=event_menu_for_telegram(new_event),
                    parse_mode=formatting_to_telegram_mode(new_event.formatting),
                )
            else:
                msg = self.bot.send_document(
                    destination.address,
                    new_event.photo_id,
                    caption=new_event.text,
                    reply_to_message_id=old_message_id,
                    reply_markup=event_menu_for_telegram(new_event),
                    parse_mode=formatting_to_telegram_mode(new_event.formatting),
                )
            new_event.with_raw_data(RawDataTelegramOutbound(msg))
            new_event.log()
            return new_event
        if isinstance(new_event, EventMessage):
            old_message_id = old_event.raw_data.update_obj.message.message_id
            msg = self.bot.send_message(
                new_event.destination.address,
                new_event.text,
                reply_to_message_id=old_message_id,
                reply_markup=event_menu_for_telegram(new_event),
                parse_mode=formatting_to_telegram_mode(new_event.formatting),
            )
            new_event.with_raw_data(RawDataTelegramOutbound(msg))
            new_event.log()
            return new_event
        else:
            error = MessageError(
                "Unsupported event type, {}, sent as reply to Telegram server".format(
                    new_event.__class__.__name__
                )
            )
            logger.error(error.get_log_line())
            raise NotImplementedError()

    def edit(self, old_event: EventMessage, new_event: EventMessage) -> EventMessage:
        # Do checks
        super().edit(old_event, new_event)
        if isinstance(old_event, EventMessageWithPhoto) != isinstance(new_event, EventMessageWithPhoto):
            raise ServerException("Can't change whether a message has a photo when editing.")
        # Edit event
        return self.edit_by_id(old_event.message_id, new_event, has_photo=isinstance(old_event, EventMessageWithPhoto))

    def edit_by_id(
            self,
            message_id: int,
            new_event: EventMessage,
            *,
            has_photo: bool = False
    ) -> EventMessage:
        if not message_id:
            raise ServerException("Old event has no message id associated with it")
        destination = new_event.destination
        if has_photo or isinstance(new_event, EventMessageWithPhoto):
            try:
                msg = self.bot.edit_message_caption(
                    chat_id=destination.address,
                    message_id=message_id,
                    caption=new_event.text,
                    reply_markup=event_menu_for_telegram(new_event),
                    parse_mode=formatting_to_telegram_mode(new_event.formatting)
                )
            except TelegramError:
                msg = self.bot.edit_message_text(
                    chat_id=destination.address,
                    message_id=message_id,
                    text=new_event.text,
                    reply_markup=event_menu_for_telegram(new_event),
                    parse_mode=formatting_to_telegram_mode(new_event.formatting)
                )
        else:
            msg = self.bot.edit_message_text(
                chat_id=destination.address,
                message_id=message_id,
                text=new_event.text,
                reply_markup=event_menu_for_telegram(new_event),
                parse_mode=formatting_to_telegram_mode(new_event.formatting)
            )
        new_event.with_raw_data(RawDataTelegramOutbound(msg))
        new_event.log()
        return new_event

    def get_name_by_address(self, address: str) -> str:
        chat = self.bot.get_chat(address)
        if chat.type == chat.PRIVATE:
            return " ".join([chat.first_name, chat.last_name])
        if chat.type in [chat.GROUP, chat.SUPERGROUP, chat.CHANNEL]:
            return chat.title

    def to_json(self) -> Dict:
        """
        Creates a dict of configuration for the server, to store as json
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
    def from_json(json_obj: Dict, hallo: 'Hallo') -> 'ServerTelegram':
        api_key = json_obj["api_key"]
        new_server = ServerTelegram(hallo, api_key)
        new_server.name = json_obj["name"]
        new_server.auto_connect = json_obj["auto_connect"]
        if "nick" in json_obj:
            new_server.nick = json_obj["nick"]
        if "prefix" in json_obj:
            new_server.prefix = json_obj["prefix"]
        if "permission_mask" in json_obj:
            new_server.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        for channel in json_obj["channels"]:
            new_server.add_channel(Channel.from_json(channel, new_server))
        for user in json_obj["users"]:
            new_server.add_user(User.from_json(user, new_server))
        return new_server

    def join_channel(self, channel_obj: Channel) -> None:
        pass
        # TODO

    def check_user_identity(self, user_obj: User) -> bool:
        return True
