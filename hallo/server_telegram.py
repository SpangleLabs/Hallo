import asyncio
from typing import TYPE_CHECKING, Awaitable

import telethon
import logging
from telethon import TelegramClient, events, Button
from telethon.tl.types import KeyboardButtonCallback

from hallo.destination import User, Channel
from hallo.errors import MessageError
from hallo.events import (
    EventMessage,
    RawDataTelegram,
    EventMessageWithPhoto,
    RawDataTelegramOutbound, EventMenuCallback, ServerEvent
)
from hallo.inc.commons import all_subclasses
from hallo.permission_mask import PermissionMask
from hallo.server import Server, ServerException

if TYPE_CHECKING:
    from hallo.hallo import Hallo


logger = logging.getLogger(__name__)


def event_menu_for_telegram(event: EventMessage) -> list[list[KeyboardButtonCallback]] | None:
    if not event.menu_buttons:
        return None
    menu = []
    for row in event.menu_buttons:
        menu.append([
            Button.inline(button.text, data=button.data)
            for button in row
        ])
    return menu


def formatting_to_telegram_mode(event_formatting: EventMessage.Formatting) -> str | None:
    return {
        EventMessage.Formatting.MARKDOWN: "markdown",
        EventMessage.Formatting.HTML: "html",
    }.get(event_formatting)


def entity_name(entity) -> str:
    if hasattr(entity, "title"):
        return entity.title
    names_list = [entity.first_name, entity.last_name]
    return " ".join([name for name in names_list if name is not None])



class ServerTelegram(Server):

    type = Server.TYPE_TELEGRAM
    image_extensions = ["jpg", "jpeg", "png"]

    def __init__(self, hallo: 'Hallo', api_id: int, api_hash: str, bot_token: str) -> None:
        super().__init__(hallo)
        """
        Constructor for server object
        :param hallo: Hallo Instance of hallo that contains this server object
        :type hallo: Hallo.Hallo
        """
        self.hallo = hallo  # The hallo object that created this server
        # Persistent/saved class variables
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.name = "Telegram"  # Server name #TODO: needs to be configurable!
        # Whether to automatically connect to this server when hallo starts
        self.auto_connect = True
        # List of channels on this server (which may or may not be currently active)
        self.channel_list: list[Channel] = []
        self.user_list: list[User] = []  # Users on this server (not all of which are online)
        self.nick = None  # Nickname to use on this server
        self.prefix = None  # Prefix to use with functions on this server
        self.full_name = None  # Full name to use on this server
        self.permission_mask = PermissionMask()  # PermissionMask for the server
        # Dynamic/unsaved class variables
        self.state = Server.STATE_CLOSED  # Current state of the server connection
        session_name = f"{type(self).__name__}_{self.name}"
        self.client = TelegramClient(session_name, api_id, api_hash)
        # Message handlers
        self.client.add_event_handler(self.parse_private_message, events.NewMessage(incoming=True, pattern=lambda e: e.is_private))
        self.client.add_event_handler(self.parse_group_message, events.NewMessage(incoming=True, pattern=lambda e: not e.is_private))
        self.client.add_event_handler(self.parse_menu_callback, events.CallbackQuery())
        # Catch-all message handler for anything not already handled.
        self.client.add_event_handler(self.parse_unhandled, None)
        # Initialise labels
        for evt_class in all_subclasses(ServerEvent):
            self.incoming.labels(
                server_type=self.__class__.__name__,
                event_type=evt_class.__name__
            )
            self.outgoing.labels(
                server_type=self.__class__.__name__,
                event_type=evt_class.__name__
            )

    def start(self) -> None:
        """
        Starts up the server and launches the new thread
        """
        if self.state != Server.STATE_CLOSED:
            raise ServerException("Already started.")
        self.state = Server.STATE_CONNECTING
        asyncio.create_task(self.connect())

    async def connect(self) -> None:
        """
        Internal method
        Method to read from stream and process. Will connect and call internal parsing methods or whatnot.
        Needs to be started in it's own thread, only exits when the server connection ends
        """
        # noinspection PyUnresolvedReferences
        await self.client.start(bot_token=self.bot_token)
        self.state = Server.STATE_OPEN

    async def disconnect(self, force: bool = False) -> None:
        self.state = Server.STATE_DISCONNECTING
        # noinspection PyUnresolvedReferences
        await self.client.disconnect()
        self.state = Server.STATE_CLOSED

    async def parse_private_message(self, event: events.NewMessage.Event) -> None:
        """
        Handles a new private message
        :param event: Message event object from telegram API
        """
        telegram_chat = await event.message.get_chat()
        # Get sender object
        message_sender_name = entity_name(telegram_chat)
        message_sender_addr = telegram_chat.id
        message_sender = self.get_user_by_address(message_sender_addr, message_sender_name)
        message_sender.update_activity()
        # Create Event object
        if event.message.photo:
            photo_id = event.message.photo.id
            message_text = event.message.text or ""
            message_evt = EventMessageWithPhoto(
                self, None, message_sender, message_text, photo_id
            ).with_raw_data(RawDataTelegram(event))
        else:
            message_text = event.message.text
            message_evt = EventMessage(
                self, None, message_sender, message_text
            ).with_raw_data(RawDataTelegram(event))
        # Print and Log the private message
        message_evt.log()
        self.incoming.labels(
            server_type=self.__class__.__name__,
            event_type=message_evt.__class__.__name__
        ).inc()
        await self.hallo.function_dispatcher.dispatch(message_evt)

    async def parse_group_message(self, event: events.NewMessage.Event) -> None:
        """
        Handles a new group or supergroup message (does not handle channel posts)
        :param event: Message event object from telegram API
        """
        telegram_sender = await event.message.get_sender()
        telegram_chat = await event.message.get_chat()
        # Get sender object
        message_sender_name = entity_name(telegram_sender)
        message_sender_addr = telegram_sender.id
        message_sender = self.get_user_by_address(message_sender_addr, message_sender_name)
        message_sender.update_activity()
        # Get group object
        message_chat_name = entity_name(telegram_chat)
        message_chat_addr = telegram_chat.id
        message_channel = self.get_channel_by_address(message_chat_addr, message_chat_name)
        message_channel.update_activity()
        # Create message event object
        if event.message.photo:
            photo_id = event.message.photo.id
            message_text = event.message.text or ""
            message_evt = EventMessageWithPhoto(
                self, message_channel, message_sender, message_text, photo_id
            ).with_raw_data(RawDataTelegram(event))
        else:
            message_text = event.message.text
            message_evt = EventMessage(
                self, message_channel, message_sender, message_text
            ).with_raw_data(RawDataTelegram(event))
        # Print and log the public message
        message_evt.log()
        self.incoming.labels(
            server_type=self.__class__.__name__,
            event_type=message_evt.__class__.__name__
        ).inc()
        # Send event to function dispatcher or passive dispatcher
        function_dispatcher = self.hallo.function_dispatcher
        if message_evt.is_prefixed:
            if message_evt.is_prefixed is True:
                await function_dispatcher.dispatch(message_evt)
            else:
                await function_dispatcher.dispatch(message_evt, [message_evt.is_prefixed])
        else:
            await function_dispatcher.dispatch_passive(message_evt)

    def parse_join(self, event: events.ChatAction.Event) -> None:
        # TODO
        pass

    async def parse_menu_callback(self, event: events.CallbackQuery.Event) -> None:
        # Get sender object
        message_sender = await event.get_sender()
        message_sender_name = entity_name(message_sender)
        message_sender_addr = message_sender.id
        message_sender = self.get_user_by_address(message_sender_addr, message_sender_name)
        message_sender.update_activity()
        # Get channel object
        message_chat = await event.get_chat()
        message_channel_name = entity_name(message_chat)
        message_channel_addr = message_chat.id
        if message_channel_addr == message_sender_addr:
            message_channel = None
        else:
            message_channel = self.get_channel_by_address(message_channel_addr, message_channel_name)
            message_channel.update_activity()
        # Create message event object
        message_id = event.message_id
        callback_data = event.data
        callback_evt = EventMenuCallback(
            self, message_channel, message_sender, message_id, callback_data
        ).with_raw_data(RawDataTelegram(event))
        # Print and log the public message
        callback_evt.log()
        self.incoming.labels(
            server_type=self.__class__.__name__,
            event_type=callback_evt.__class__.__name__
        ).inc()
        # Send event to function dispatcher or passive dispatcher
        function_dispatcher = self.hallo.function_dispatcher
        await function_dispatcher.dispatch_passive(callback_evt)

    def parse_unhandled(self, event: telethon.events.raw.Raw) -> None:
        """
        Parses an unhandled message from the server
        :param event: Raw event from the telegram API
        """
        # Print it to console
        error = MessageError(
            "Unhandled data received on Telegram server: {}".format(update)
        )
        logger.error(error.get_log_line())
        self.incoming.labels(
            server_type=self.__class__.__name__,
            event_type="other-unhandled"
        ).inc()

    async def send(
            self,
            event: ServerEvent,
            *,
            after_sent_callback: Awaitable[None] | None = None,
            reply_to_id: int | None = None
    ) -> None:
        is_group = False
        if isinstance(event, EventMessage):
            is_group = event.channel is not None
        self.outgoing.labels(
            server_type=self.__class__.__name__,
            event_type=event.__class__.__name__
        ).inc()
        await self._send_raw(event, after_sent_callback=after_sent_callback, reply_to_id=reply_to_id)

    async def _send_raw(
            self,
            event: ServerEvent,
            *,
            after_sent_callback: Awaitable[None] | None = None,
            reply_to_id: int | None = None
    ) -> None:
        if isinstance(event, EventMessageWithPhoto):
            try:
                if isinstance(event.photo_id, list):
                    msgs = await self.client.send_file(
                        entity=event.destination.address,
                        file=event.photo_id,
                        caption=event.text,
                        parse_mode=formatting_to_telegram_mode(event.formatting),
                        reply_to=reply_to_id,
                    )
                    msg = msgs[0]
                elif any(
                    [
                        event.photo_id.lower().endswith("." + x)
                        for x in ServerTelegram.image_extensions
                    ]
                ):
                    msg = await self.client.send_file(
                        entity=event.destination.address,
                        file=event.photo_id,
                        caption=event.text,
                        buttons=event_menu_for_telegram(event),
                        parse_mode=formatting_to_telegram_mode(event.formatting),
                        reply_to=reply_to_id,
                    )
                else:
                    msg = await self.client.send_file(
                        entity=event.destination.address,
                        file=event.photo_id,
                        caption=event.text,
                        buttons=event_menu_for_telegram(event),
                        parse_mode=formatting_to_telegram_mode(event.formatting),
                        reply_to=reply_to_id,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to send message with picture. Sending without. Picture path %s", event.photo_id, exc_info=e
                )
                msg = await self.client.send_message(
                    entity=event.destination.address,
                    message=event.text,
                    buttons=event_menu_for_telegram(event),
                    parse_mode=formatting_to_telegram_mode(event.formatting),
                    reply_to=reply_to_id,
                )
            event.with_raw_data(RawDataTelegramOutbound(msg))
        elif isinstance(event, EventMessage):
            msg = await self.client.send_message(
                entity=event.destination.address,
                message=event.text,
                parse_mode=formatting_to_telegram_mode(event.formatting),
                buttons=event_menu_for_telegram(event),
                reply_to=reply_to_id,
            )
            event.with_raw_data(RawDataTelegramOutbound(msg))
        else:
            error = MessageError(f"Unsupported event type, {event.__class__.__name__}, sent to Telegram server")
            logger.error(error.get_log_line())
            raise NotImplementedError()
        event.log()
        if after_sent_callback is not None:
            await after_sent_callback
        return

    async def reply(self, old_event: EventMessage, new_event: EventMessage) -> EventMessage | None:
        # Do checks
        await super().reply(old_event, new_event)
        if old_event.raw_data is None or not isinstance(old_event.raw_data, RawDataTelegram):
            raise ServerException("Old event has no telegram data associated with it")
        reply_to_id = old_event.message_id
        # Send event
        return await self.send(new_event, reply_to_id=reply_to_id)

    async def edit(self, old_event: EventMessage, new_event: EventMessage) -> EventMessage:
        # Do checks
        await super().edit(old_event, new_event)
        if isinstance(old_event, EventMessageWithPhoto) != isinstance(new_event, EventMessageWithPhoto):
            raise ServerException("Can't change whether a message has a photo when editing.")
        self.outgoing.labels(
            server_type=self.__class__.__name__,
            event_type=new_event.__class__.__name__
        ).inc()
        msg_id = old_event.message_id
        if msg_id is None:
            raise ServerException("Can't edit a message which does not have an associated message ID")
        # Edit event
        return await self.edit_by_id(msg_id, new_event)

    async def edit_by_id(self, message_id: int, new_event: EventMessage) -> EventMessage:
        if not message_id:
            raise ServerException("Old event has no message id specified")
        self.outgoing.labels(
            server_type=self.__class__.__name__,
            event_type=new_event.__class__.__name__
        ).inc()
        return await self._edit_by_id_raw(message_id, new_event)

    async def _edit_by_id_raw(
            self,
            message_id: int,
            new_event: EventMessage,
    ) -> EventMessage:
        destination = new_event.destination
        if isinstance(new_event, EventMessageWithPhoto):
            try:
                msg = await self.client.edit_message(
                    entity=destination.address,
                    message=message_id,
                    text=new_event.text,
                    buttons=event_menu_for_telegram(new_event),
                    parse_mode=formatting_to_telegram_mode(new_event.formatting),
                    file=new_event.photo_id,
                )
            except Exception as e:
                logger.warning(
                    "Failed to edit message with picture. Editing without. Picture path %s",
                    new_event.photo_id, exc_info=e
                )
                msg = await self.client.edit_message(
                    entity=destination.address,
                    message=message_id,
                    text=new_event.text,
                    buttons=event_menu_for_telegram(new_event),
                    parse_mode=formatting_to_telegram_mode(new_event.formatting)
                )
        else:
            msg = await self.client.edit_message(
                entity=destination.address,
                message=message_id,
                text=new_event.text,
                buttons=event_menu_for_telegram(new_event),
                parse_mode=formatting_to_telegram_mode(new_event.formatting)
            )
        new_event.with_raw_data(RawDataTelegramOutbound(msg))
        new_event.log()
        return new_event

    async def get_name_by_address(self, address: str) -> str:
        address_id = int(address)
        input_entity = await self.client.get_input_entity(address_id)
        entity = await self.client.get_entity(input_entity)
        return entity_name(entity)

    def to_json(self) -> dict:
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
        json_obj["api_id"] = self.api_id
        json_obj["api_hash"] = self.api_hash
        json_obj["bot_token"] = self.bot_token
        return json_obj

    @staticmethod
    def from_json(json_obj: dict, hallo: 'Hallo') -> 'ServerTelegram':
        api_id = json_obj["api_id"]
        api_hash = json_obj["api_hash"]
        bot_token = json_obj["bot_token"]
        new_server = ServerTelegram(hallo, api_id, api_hash, bot_token)
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

    async def join_channel(self, channel_obj: Channel) -> None:
        pass
        # TODO

    async def check_user_identity(self, user_obj: User) -> bool:
        return True
