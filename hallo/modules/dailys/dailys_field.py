import datetime
import logging
from abc import ABCMeta
from datetime import date
from typing import Type, TYPE_CHECKING, Awaitable

from hallo.events import Event, EventMessage

if TYPE_CHECKING:
    from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


logger = logging.getLogger(__name__)


class DailysException(Exception):
    pass


class DailysField(metaclass=ABCMeta):
    # An abstract class representing an individual dailys field type.
    # A field can/will be multiple columns, maybe a varying quantity of them by configuration
    type_name = None

    def __init__(self, spreadsheet: 'DailysSpreadsheet') -> None:
        self.spreadsheet: 'DailysSpreadsheet' = spreadsheet

    @staticmethod
    async def create_from_input(event: EventMessage, spreadsheet: 'DailysSpreadsheet') -> 'DailysField':
        raise NotImplementedError()

    @staticmethod
    def passive_events() -> list[Type[Event]]:
        raise NotImplementedError()

    async def passive_trigger(self, evt: Event) -> None:
        raise NotImplementedError()

    def to_json(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    async def from_json(json_obj: dict, spreadsheet: 'DailysSpreadsheet') -> 'DailysField':
        raise NotImplementedError()

    async def save_data(self, data: dict, data_date: datetime.datetime) -> None:
        await self.spreadsheet.save_field(self, data, data_date=data_date)

    async def load_data(self, data_date: date) -> dict | None:
        return await self.spreadsheet.read_field(self, data_date)

    async def message_channel(
            self,
            text: str,
            after_sent_callback: Awaitable[None] | None = None
    ) -> EventMessage:
        evt = EventMessage(
            self.spreadsheet.destination.server,
            self.spreadsheet.destination,
            self.spreadsheet.user,
            text,
            inbound=False,
        )
        await self.spreadsheet.user.server.send(evt, after_sent_callback=after_sent_callback)
        return evt


class DailysAnimalsField(DailysField):
    # Does animal sightings measurements

    def get_animal_list(self) -> list[str]:
        # Return a list of animals which are being logged
        pass


class DailysOField(DailysField):
    pass


class DailysShowerField(DailysField):
    # Temperature, song, whatever
    pass


class DailysCaffeineField(DailysField):
    # At new_day(), can input N, none if there's no entry today
    pass


class DailysGoogleMapsField(DailysField):
    # Get distances/times from google maps?
    # Get work times
    pass


class DailysMyFitnessPalField(DailysField):
    # Weight, maybe food things
    pass


class DailysAlcoholField(DailysField):
    pass


class DailysShutdownField(DailysField):
    # Not sure on this? Teeth, multivitamins, clothes out, maybe diary?, trigger mood measurement?
    # Night is done after shutdown.
    # new_day() triggers N, N, N entries.
    pass
