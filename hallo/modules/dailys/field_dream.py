from typing import TYPE_CHECKING, Type

from hallo.events import EventMessage, Event
from hallo.inc.commons import Commons
import hallo.modules.dailys.dailys_field


if TYPE_CHECKING:
    from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


class DailysDreamField(hallo.modules.dailys.dailys_field.DailysField):
    type_name = "dreams"

    @staticmethod
    async def create_from_input(event: EventMessage, spreadsheet: 'DailysSpreadsheet') -> 'DailysDreamField':
        return DailysDreamField(spreadsheet)

    @staticmethod
    def passive_events() -> list[Type[Event]]:
        return [EventMessage]

    async def passive_trigger(self, evt: Event) -> None:
        if not isinstance(evt, EventMessage):
            return
        if not evt.text.lower().startswith("dream"):
            return
        data_date = evt.get_send_time().date()
        dream_text = evt.text
        new_dream = {"text": dream_text}
        dream_data = await self.load_data(data_date)
        if dream_data is None:
            dream_data = {"dreams": []}
        dream_data["dreams"].append(new_dream)
        dream_count = len(dream_data["dreams"])
        await self.save_data(dream_data, data_date)
        # Send date to destination
        dream_ordinal = Commons.ordinal(dream_count)
        await evt.reply(evt.create_response(f"Logged dream. {dream_ordinal} of the day."))
        return

    def to_json(self) -> dict:
        return {
            "type_name": self.type_name,
        }

    @staticmethod
    async def from_json(json_obj: dict, spreadsheet: 'DailysSpreadsheet') -> 'DailysDreamField':
        return DailysDreamField(spreadsheet)
