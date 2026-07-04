import logging
from typing import TYPE_CHECKING

from hallo.modules.dailys.dailys_field_factory import DailysFieldFactory
from hallo.events import EventMessage, Event, ServerEvent
from hallo.function import Function
from hallo.modules.dailys.dailys_repo import DailysRepo

if TYPE_CHECKING:
    from hallo.hallo import Hallo


logger = logging.getLogger(__name__)


class Dailys(Function):
    def __init__(self) -> None:
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "dailys"
        # Names which can be used to address the function
        self.names = {"dailys"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = (
            "Core dailys method, does all the dailys processing passively."
            " Doesn't do anything (currently) when called actively."
        )
        self.dailys_repo = None
        """ :type : DailysRepo | None"""

    async def get_dailys_repo(self, hallo_obj: 'Hallo') -> 'DailysRepo':
        if self.dailys_repo is None:
            self.dailys_repo = await DailysRepo.load_json(hallo_obj)
        return self.dailys_repo

    @staticmethod
    def is_persistent() -> bool:
        return True

    @staticmethod
    def load_function() -> 'Dailys':
        """Loads the function, persistent functions only."""
        return Dailys()

    def save_function(self) -> None:
        """Saves the function, persistent functions only."""
        if self.dailys_repo is not None:
            self.dailys_repo.save_json()

    def get_passive_events(self) -> set[Event]:
        """Returns a list of events which this function may want to respond to in a passive way"""
        return set(
            [
                event
                for field in DailysFieldFactory.fields
                for event in field.passive_events()
            ]
        )

    async def run(self, event: EventMessage) -> EventMessage:
        evt_cmd = event.text.strip().removeprefix("dailys").strip().lower()
        if evt_cmd in ["reload", "redeploy", "refresh"]:
            self.dailys_repo.save_json()
            self.dailys_repo = None
            await self.get_dailys_repo(event.server.hallo)
            return event.create_response("Dailys repository reloaded.")
        return event.create_response("Dailys system does not understand this command.")

    async def passive_run(self, event: Event, hallo_obj: 'Hallo') -> ServerEvent | None:
        repo = await self.get_dailys_repo(hallo_obj)
        spreadsheets = repo.spreadsheets
        if isinstance(event, EventMessage):
            msg_spreadsheet = repo.get_by_location(event)
            if msg_spreadsheet is None:
                return
            spreadsheets = [msg_spreadsheet]
        for spreadsheet in spreadsheets:
            for field in spreadsheet.fields_list:
                if event.__class__ in field.passive_events():
                    try:
                        await field.passive_trigger(event)
                    except Exception as e:
                        logger.error("Dailys failure: ", exc_info=e)
