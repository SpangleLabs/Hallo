from datetime import timedelta, date, datetime
from typing import TYPE_CHECKING, Type, Any

import isodate

from hallo.events import EventMessage, Event
from hallo.modules.dailys.dailys_field import DailysField

if TYPE_CHECKING:
    from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


class DailysSleepField(DailysField):
    # Does sleep and wake times, sleep notes, dream logs, shower?
    type_name = "sleep"
    WAKE_WORDS = ["morning", "wake", "woke"]
    SLEEP_WORDS = ["goodnight", "sleep", "nini", "night"]
    json_key_wake_time = "wake_time"
    json_key_sleep_time = "sleep_time"
    json_key_interruptions = "interruptions"

    @staticmethod
    async def create_from_input(event: EventMessage, spreadsheet: 'DailysSpreadsheet') -> 'DailysSleepField':
        return DailysSleepField(spreadsheet)

    @staticmethod
    def passive_events() -> list[Type[Event]]:
        return [EventMessage]

    async def passive_trigger(self, evt: Event) -> None:
        if not isinstance(evt, EventMessage):
            return None
        input_clean = evt.text.strip().lower()
        evt_time = evt.get_send_time()
        current_data = await self.load_data(evt_time.date())
        if current_data is None:
            current_data = dict()
        yesterday_date = evt_time.date() - timedelta(1)
        yesterday_data = await self.load_data(yesterday_date)
        if yesterday_data is None:
            yesterday_data = dict()
        # If user is waking up
        if input_clean in DailysSleepField.WAKE_WORDS:
            return await self.parse_wake_message(evt_time, current_data, yesterday_data)
        # If user is going to sleep
        if input_clean in DailysSleepField.SLEEP_WORDS:
            return await self.parse_sleep_message(evt_time, current_data, yesterday_data)
        return None

    async def parse_wake_message(
            self,
            evt_time: datetime,
            current_data: dict,
            yesterday_data: dict,
    ):
        time_str = evt_time.isoformat()
        sleep_date = evt_time.date()
        yesterday_date = evt_time.date() - timedelta(1)
        # If today's data is blank, write in yesterday's sleep data
        if current_data == {}:
            current_data = yesterday_data
            sleep_date = yesterday_date
        # If you already woke in this data, why are you waking again?
        if self.json_key_wake_time in current_data:
            await self.message_channel("Didn't you already wake up?")
            return
        # If not, add a wake time to sleep data
        current_data[self.json_key_wake_time] = time_str
        await self.save_data(current_data, sleep_date)
        await self.message_channel("Good morning!")
        # Check how long they were sleeping
        status_resp = await self.spreadsheet.read_path("/views/sleep_status.json")
        if not status_resp["is_sleeping"]:
            await self.message_channel("Weird, the sleep status endpoint says you're still asleep")
        else:
            time_asleep_str = status_resp["time_asleep"]
            time_asleep = isodate.parse_duration(time_asleep_str)
            total_minutes = time_asleep.total_seconds() // 60
            sleep_hours = total_minutes // 60
            sleep_minutes = total_minutes - (60 * sleep_hours)
            await self.message_channel(f"You were asleep for {sleep_hours} hours and {sleep_minutes} minutes")
        return

    async def parse_sleep_message(
            self,
            evt_time: datetime,
            current_data: dict,
            yesterday_data: dict,
    ):
        time_str = evt_time.isoformat()
        sleep_date = evt_time.date()
        yesterday_date = evt_time.date() - timedelta(1)
        # If it's before 4pm, it's probably yesterday's sleep.
        if evt_time.hour <= 16:
            current_data = yesterday_data
            sleep_date = yesterday_date
        # If they haven't gone to sleep yet, record a sleep
        if self.json_key_sleep_time not in current_data:
            current_data[self.json_key_sleep_time] = time_str
            await self.save_data(current_data, sleep_date)
            await self.message_channel("Goodnight!")
            return
        # Otherwise, they have already gone to sleep
        # If they haven't woken yet, then they're updating their sleep time
        if self.json_key_wake_time not in current_data:
            current_data[self.json_key_sleep_time] = time_str
            await self.save_data(current_data, sleep_date)
            await self.message_channel("Good night again!")
            return
        # Otherwise, they have slept and woke, so this was actually an interruption, not an initial sleep
        # Move the last wake time to interruptions
        interruption = {
            self.json_key_wake_time: current_data.pop(self.json_key_wake_time),
            self.json_key_sleep_time: time_str,
        }
        if self.json_key_interruptions not in current_data:
            current_data[self.json_key_interruptions] = []
        current_data[self.json_key_interruptions].append(interruption)
        await self.save_data(current_data, sleep_date)
        await self.message_channel("Oh, going back to sleep? Sleep well!")
        return

    def to_json(self) -> dict:
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        return json_obj

    @staticmethod
    async def from_json(json_obj: dict, spreadsheet: 'DailysSpreadsheet') -> 'DailysSleepField':
        return DailysSleepField(spreadsheet)
