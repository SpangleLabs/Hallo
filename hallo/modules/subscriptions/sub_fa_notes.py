from datetime import datetime, timedelta
from typing import Dict, List, Optional

import isodate

from hallo.destination import Destination, Channel, User
from hallo.events import EventMessage
from hallo.hallo import Hallo
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscriptions
from hallo.server import Server


class FANotificationNotesSub(hallo.modules.subscriptions.subscriptions.Subscription[Dict]):
    names: List[str] = ["fa notes notifications", "fa notes", "furaffinity notes"]
    type_name: str = "fa_notif_notes"

    NEW_INBOX_NOTE = "new_note"
    READ_OUTBOX_NOTE = "note_read"

    def __init__(
        self,
        server: Server,
        destination: Destination,
        fa_key: 'hallo.modules.subscriptions.common_fa_key.FAKey',
        last_check: Optional[datetime] = None,
        update_frequency: Optional[timedelta] = None,
        inbox_note_ids: Optional[List[str]] = None,
        outbox_note_ids: Optional[List[str]] = None,
    ):
        """
        :param inbox_note_ids: List of id strings of notes in the inbox
        :param outbox_note_ids: List of id strings of unread notes in the outbox
        """
        super().__init__(server, destination, last_check, update_frequency)
        self.fa_key: hallo.modules.subscriptions.common_fa_key.FAKey = fa_key
        self.inbox_note_ids: List[str] = [] if inbox_note_ids is None else inbox_note_ids
        self.outbox_note_ids: List[str] = [] if outbox_note_ids is None else outbox_note_ids

    @classmethod
    def create_from_input(
            cls,
            input_evt: EventMessage,
            sub_repo
    ) -> 'FANotificationNotesSub':
        user = input_evt.user
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Cannot create FA note notification subscription without cookie details. "
                "Please set up FA cookies with "
                "`setup FA user data a=<cookie_a>;b=<cookie_b>` "
                "and your cookie values."
            )
        server = input_evt.server
        destination = (
            input_evt.channel if input_evt.channel is not None else input_evt.user
        )
        # See if user gave us an update period
        try:
            search_delta = isodate.parse_duration(input_evt.command_args)
        except isodate.isoerror.ISO8601Error:
            search_delta = isodate.parse_duration("PT300S")
        notes_sub = FANotificationNotesSub(
            server, destination, fa_key, update_frequency=search_delta
        )
        notes_sub.check()
        return notes_sub

    def matches_name(self, name_clean: str) -> bool:
        return name_clean in [s.lower().strip() for s in self.names + ["notes"]]

    def get_name(self) -> str:
        return "FA notes for {}".format(self.fa_key.user.name)

    def check(self, *, ignore_result: bool = False) -> List[Dict]:
        fa_reader = self.fa_key.get_fa_reader()
        results = []
        # Check inbox and outbox
        inbox_notes_page = fa_reader.get_notes_page(
            hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.NOTES_INBOX
        )
        outbox_notes_page = fa_reader.get_notes_page(
            hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.NOTES_OUTBOX
        )
        # Check for newly received notes in inbox
        for inbox_note in inbox_notes_page.notes:
            note_id = inbox_note.note_id
            if note_id not in self.inbox_note_ids and (
                len(self.inbox_note_ids) == 0
                or int(note_id) > int(self.inbox_note_ids[-1])
            ):
                # New note
                results.append({"type": self.NEW_INBOX_NOTE, "note": inbox_note})
        # Check for newly read notes in outbox
        for outbox_note in outbox_notes_page.notes:
            if outbox_note.note_id in self.outbox_note_ids and outbox_note.is_read:
                # Newly read note
                results.append({"type": self.READ_OUTBOX_NOTE, "note": outbox_note})
        # Reset inbox note ids and outbox note ids
        self.inbox_note_ids = [note.note_id for note in inbox_notes_page.notes]
        self.outbox_note_ids = [
            note.note_id for note in outbox_notes_page.notes if not note.is_read
        ]
        # Update last check time
        self.last_check = datetime.now()
        # Return results
        return results[::-1]

    def format_item(self, item: Dict) -> EventMessage:
        # Construct output
        output = "Err, notes did something?"
        note = item["note"]  # type: hallo.modules.subscriptions.common_fa_key.FAKey.FAReader.FANote
        if item["type"] == self.NEW_INBOX_NOTE:
            output = \
                f"You have a new note. Subject: {note.subject}, From: {note.name}, " \
                f"Link: https://www.furaffinity.net/viewmessage/{note.note_id}/"
        if item["type"] == self.READ_OUTBOX_NOTE:
            output = "An outbox note has been read. Subject: {}, To: {}".format(
                note.subject, note.name
            )
        channel = self.destination if isinstance(self.destination, Channel) else None
        user = self.destination if isinstance(self.destination, User) else None
        output_evt = EventMessage(self.server, channel, user, output, inbound=False)
        return output_evt

    def to_json(self) -> Dict:
        json_obj = super().to_json()
        json_obj["sub_type"] = self.type_name
        json_obj["fa_key_user_address"] = self.fa_key.user.address
        json_obj["inbox_note_ids"] = []
        for note_id in self.inbox_note_ids:
            json_obj["inbox_note_ids"].append(note_id)
        json_obj["outbox_note_ids"] = []
        for note_id in self.outbox_note_ids:
            json_obj["outbox_note_ids"].append(note_id)
        return json_obj

    @staticmethod
    def from_json(
            json_obj: Dict, hallo_obj: Hallo, sub_repo
    ) -> 'FANotificationNotesSub':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                'Could not find server with name "{}"'.format(json_obj["server_name"])
            )
        # Load channel or user
        if "channel_address" in json_obj:
            destination = server.get_channel_by_address(json_obj["channel_address"])
        else:
            if "user_address" in json_obj:
                destination = server.get_user_by_address(json_obj["user_address"])
            else:
                raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                    "Channel or user must be defined."
                )
        if destination is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException("Could not find chanel or user.")
        # Load last check
        last_check = None
        if "last_check" in json_obj:
            last_check = datetime.strptime(
                json_obj["last_check"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Load update frequency
        update_frequency = isodate.parse_duration(json_obj["update_frequency"])
        # Load last update
        last_update = None
        if "last_update" in json_obj:
            last_update = datetime.strptime(
                json_obj["last_update"], "%Y-%m-%dT%H:%M:%S.%f"
            )
        # Type specific loading
        # Load fa_key
        user_addr = json_obj["fa_key_user_address"]
        user = server.get_user_by_address(user_addr)
        if user is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Could not find user matching address `{}`".format(user_addr)
            )
        fa_keys = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        assert isinstance(fa_keys, hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_key = fa_keys.get_key_by_user(user)
        if fa_key is None:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Could not find fa key for user: {}".format(user.name)
            )
        # Load inbox_note_ids
        inbox_ids = []
        for note_id in json_obj["inbox_note_ids"]:
            inbox_ids.append(note_id)
        # Load outbox_note_ids
        outbox_ids = []
        for note_id in json_obj["outbox_note_ids"]:
            outbox_ids.append(note_id)
        new_sub = FANotificationNotesSub(
            server,
            destination,
            fa_key,
            last_check=last_check,
            update_frequency=update_frequency,
            inbox_note_ids=inbox_ids,
            outbox_note_ids=outbox_ids,
        )
        new_sub.last_update = last_update
        return new_sub
