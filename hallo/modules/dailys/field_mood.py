import functools
from abc import ABC, abstractmethod
from datetime import timedelta, datetime, time, date
from threading import RLock
from typing import List, Union, Dict, Optional, TYPE_CHECKING

from hallo.events import EventMessage, EventMinute, RawDataTelegram, RawDataTelegramOutbound, Event
import hallo.modules.dailys.dailys_field
import hallo.modules.dailys.field_sleep

if TYPE_CHECKING:
    import hallo.modules.dailys.dailys_spreadsheet


def probably_instance(obj, cls) -> bool:
    return obj.__class__.__name__ == cls.__name__


@functools.total_ordering
class MoodTime:
    WAKE = "WakeUpTime"
    SLEEP = "SleepTime"

    def __init__(self, mood_time: Union[str, time]):
        self.mood_time = mood_time
        if mood_time not in [self.WAKE, self.SLEEP] and not probably_instance(mood_time, time):
            raise TypeError("Invalid type for MoodTime")

    @classmethod
    def from_str(cls, time_str: str) -> 'MoodTime':
        if time_str in [cls.WAKE, cls.SLEEP]:
            return MoodTime(time_str)
        else:
            return MoodTime(datetime.strptime(time_str, "%H:%M:%S").time())

    def __eq__(self, other):
        return probably_instance(other, MoodTime) and self.mood_time == other.mood_time

    def __hash__(self):
        return hash(self.mood_time)

    def __str__(self):
        return str(self.mood_time)

    def __lt__(self, other) -> bool:
        if not probably_instance(other, MoodTime):
            return NotImplemented
        if self.is_wake():
            return not other.is_wake()
        if self.is_sleep():
            return False
        return self.mood_time < other.mood_time

    @property
    def is_time(self) -> bool:
        return self.mood_time not in [self.WAKE, self.SLEEP]

    def is_wake(self) -> bool:
        return self.mood_time == self.WAKE

    def is_sleep(self) -> bool:
        return self.mood_time == self.SLEEP


class MoodDay:
    def __init__(self, mood_date: date, mood_entries: Dict[MoodTime, 'MoodEntry']):
        self.mood_date = mood_date
        self.mood_entries = mood_entries or {}

    def to_dict(self) -> Dict:
        result = {}
        for time_val, entry in self.mood_entries.items():
            result[str(time_val)] = entry.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Optional[Dict], mood_date: date) -> 'MoodDay':
        if data is None:
            return MoodDay(mood_date, {})
        mood_entries = {}
        for key, val in data.items():
            mood_time = MoodTime.from_str(key)
            mood_entries[mood_time] = MoodEntry.from_data(val, mood_time)
        return MoodDay(
            mood_date,
            mood_entries
        )

    def is_full(self, mood_times: List[MoodTime]) -> bool:
        return all(
            mood_time in self.mood_entries and probably_instance(self.mood_entries[mood_time], MoodMeasurement)
            for mood_time in mood_times
        )

    def is_empty(self) -> bool:
        return len(self.mood_entries) == 0

    def has_time(self, time_val: MoodTime) -> bool:
        return time_val in self.mood_entries

    def has_wake_time(self) -> bool:
        return self.has_time(MoodTime(MoodTime.WAKE))

    def has_sleep_time(self) -> bool:
        return self.has_time(MoodTime(MoodTime.SLEEP))

    def has_all_but_sleep(self, time_list: 'MoodTimeList') -> bool:
        for mood_time in time_list.times:
            if mood_time == MoodTime(MoodTime.SLEEP):
                continue
            if not self.has_time(mood_time):
                return False
        return True

    def awaiting_sleep(self, time_list: 'MoodTimeList') -> bool:
        if not time_list.has_sleep():
            return False
        if self.has_sleep_time():
            return False
        if not time_list.has_non_sleep():
            return True
        return self.has_all_but_sleep(time_list)

    def list_unanswered_requests(self) -> List['MoodRequest']:
        return sorted(
            [m for m in self.mood_entries.values() if probably_instance(m, MoodRequest)],
            key=lambda x: x.mood_time
        )

    def add_request(self, mood_time: MoodTime, message_id: Optional[int]) -> None:
        if message_id is None:
            return None
        request = MoodRequest(mood_time, message_id)
        self.mood_entries[mood_time] = request

    def set_measurement(self, time_val: MoodTime, measurement_data: Dict[str, int]) -> None:
        if self.has_time(time_val):
            current = self.mood_entries[time_val]
            self.mood_entries[time_val] = current.to_measurement(measurement_data)
            return
        self.mood_entries[time_val] = MoodMeasurement(time_val, measurement_data)


class MoodEntry(ABC):
    def __init__(self, mood_time: MoodTime, *, message_id: Optional[int] = None):
        self.mood_time = mood_time
        self.message_id = message_id

    @classmethod
    def from_data(cls, data: Dict, mood_time: MoodTime) -> 'MoodEntry':
        if {"message_id"} == set(data.keys()):
            return MoodRequest.from_data(data, mood_time)
        return MoodMeasurement.from_data(data, mood_time)

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    def to_measurement(self, measurement_data: Dict[str, int]) -> 'MoodMeasurement':
        return MoodMeasurement(self.mood_time, measurement_data, self.message_id)


class MoodRequest(MoodEntry):
    def __init__(self, mood_time: MoodTime, message_id: int):
        super().__init__(mood_time, message_id=message_id)

    @classmethod
    def from_data(cls, data: Dict, mood_time: MoodTime) -> 'MoodRequest':
        return MoodRequest(
            mood_time,
            data["message_id"]
        )

    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id
        }


class MoodMeasurement(MoodEntry):
    def __init__(self, mood_time: MoodTime, mood_dict: Dict[str, int], message_id: Optional[int] = None):
        super().__init__(mood_time, message_id=message_id)
        self.mood_dict = mood_dict

    @classmethod
    def from_data(cls, data: Dict, mood_time: MoodTime) -> 'MoodEntry':
        mood_data = data.copy()
        message_id = None
        if "message_id" in mood_data:
            message_id = mood_data["message_id"]
            del mood_data["message_id"]
        return MoodMeasurement(mood_time, mood_data, message_id=message_id)

    def to_dict(self) -> Dict:
        result = self.mood_dict.copy()
        if self.message_id:
            result["message_id"] = self.message_id
        return result


class MoodTriggeredCache:
    def __init__(self):
        self.cache = (
            dict()
        )  # Cache of time values which have triggered already on set days.
        """ :type : dict[date, list[time|str]"""

    def has_triggered(self, mood_date: date, time_val: MoodTime):
        return mood_date in self.cache and time_val.mood_time in self.cache[mood_date]

    def save_triggered(self, mood_date, time_val):
        self.clean_old_cache(mood_date)
        if mood_date not in self.cache:
            self.cache[mood_date] = []
        self.cache[mood_date].append(time_val)

    def clean_old_cache(self, current_date):
        expired_dates = []
        for mood_date in self.cache:
            if mood_date <= current_date - timedelta(days=4):
                expired_dates.append(mood_date)
        for del_date in expired_dates:
            del self.cache[del_date]


class MoodTimeList:
    def __init__(self, mood_times: List[MoodTime]):
        self.times = mood_times

    def has_wake(self):
        return MoodTime(MoodTime.WAKE) in self.times

    def has_sleep(self):
        return MoodTime(MoodTime.SLEEP) in self.times

    def has_non_sleep(self):
        return self.times != [MoodTime(MoodTime.SLEEP)]

    def most_recent_time(self, current_time: time) -> Optional[MoodTime]:
        times = [t for t in self.times if t.is_time]
        past_times = [t for t in times if t.mood_time < current_time]
        if len(past_times) == 0:
            return None
        return max(past_times, key=lambda t: t.mood_time)

    def contains_time(self, mood_time: Union[MoodTime, str, time]) -> bool:
        if probably_instance(mood_time, MoodTime):
            return mood_time in self.times
        return MoodTime(mood_time) in self.times


class DailysMoodField(hallo.modules.dailys.dailys_field.DailysField):
    type_name = "mood"
    # Does mood measurements

    def __init__(
            self,
            spreadsheet: 'hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet',
            times: List[MoodTime],
            moods: List[str]
    ):
        super().__init__(spreadsheet)
        self.times = times
        self.time_list = MoodTimeList(times)
        self.moods = moods
        self.lock = RLock()
        self.triggered_cache = MoodTriggeredCache()

    @staticmethod
    def create_from_input(
            event: EventMessage,
            spreadsheet: 'hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet'
    ) -> 'DailysMoodField':
        return DailysMoodField.create_from_spreadsheet(spreadsheet)

    @staticmethod
    def create_from_spreadsheet(
            spreadsheet: 'hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet'
    ) -> 'DailysMoodField':
        static_data = spreadsheet.read_path("stats/mood/static/")
        if len(static_data) == 0:
            raise hallo.modules.dailys.dailys_field.DailysException(
                "Mood field static data has not been set up on dailys system."
            )
        moods = static_data[0]["data"]["moods"]
        times = []
        for time_str in static_data[0]["data"]["times"]:
            times.append(MoodTime.from_str(time_str))
        # Return new field
        return DailysMoodField(spreadsheet, times, moods)

    @staticmethod
    def passive_events():
        return [EventMessage, EventMinute]

    def get_current_mood_data(self, mood_date: date) -> MoodDay:
        """
        Returns the current mood data, and the day offset. Which might be today's or it could be yesterday's,
        if that is not done yet.
        """
        with self.lock:
            # Get today's data, unless it's empty, then get yesterday's, unless it's full, then use today's.
            yesterday_date = mood_date - timedelta(1)
            today_raw = self.load_data(mood_date)
            today_data = MoodDay.from_dict(today_raw, mood_date)
            if today_data.is_empty():
                yesterday_raw = self.load_data(yesterday_date)
                yesterday_data = MoodDay.from_dict(yesterday_raw, yesterday_date)
                if yesterday_data.is_empty() or yesterday_data.is_full(self.times):
                    return today_data
                return yesterday_data
            return today_data

    def has_triggered_for_time(self, mood_date: date, time_val: MoodTime):
        # Check cache for true values
        if self.triggered_cache.has_triggered(mood_date, time_val):
            return True
        # Get the current data
        mood_day = self.get_current_mood_data(mood_date)
        # If sleep message, and today hasn't got previous mood measurements, return true (don't cache)
        if time_val.is_sleep() and len(self.times) > 1 and mood_day.is_empty():
            return True
        # See if time has been queried or measured
        triggered = mood_day.has_time(time_val)
        # Update cache
        if triggered:
            self.triggered_cache.save_triggered(mood_day.mood_date, time_val)
        return triggered

    def passive_trigger(self, evt: Event) -> None:
        msg_date = evt.get_send_time().date()
        mood_day = self.get_current_mood_data(msg_date)
        if isinstance(evt, EventMinute):
            latest_time = self.time_list.most_recent_time(evt.get_send_time().time())
            if latest_time is None:
                return None
            if not mood_day.has_time(latest_time):
                return self.send_mood_query(mood_day, latest_time)
            return None
        if isinstance(evt, EventMessage):
            # Check if it's a morning/night message
            input_clean = evt.text.strip().lower()
            if (
                input_clean in hallo.modules.dailys.field_sleep.DailysSleepField.WAKE_WORDS
            ):
                if self.time_list.has_wake() and not mood_day.has_wake_time():
                    return self.send_mood_query(mood_day, MoodTime(MoodTime.WAKE))
                return None
            if (
                input_clean in hallo.modules.dailys.field_sleep.DailysSleepField.SLEEP_WORDS
            ):
                if self.time_list.has_sleep() and mood_day.awaiting_sleep(self.time_list):
                    return self.send_mood_query(mood_day, MoodTime(MoodTime.SLEEP))
                return None
            # Check if it's a reply to a mood message, or if there's an unanswered mood message
            input_split = input_clean.split()
            if (
                len(input_split) == 2 and input_split[0].upper() == self.mood_acronym()
            ) or input_clean.isdigit():
                unanswered_requests = mood_day.list_unanswered_requests()
                # Check if telegram message, and reply to a message
                if (
                    isinstance(evt.raw_data, RawDataTelegram)
                    and evt.raw_data.update_obj.message.reply_to_message is not None
                ):
                    reply_id = (
                        evt.raw_data.update_obj.message.reply_to_message.message_id
                    )  # TODO: This should just be a method in event.
                    unanswered_ids = {
                        request.message_id: request for request in unanswered_requests
                    }
                    if reply_id in unanswered_ids:
                        return self.process_mood_response(
                            evt, input_split[-1], unanswered_ids[reply_id].mood_time, mood_day
                        )
                # Otherwise, use the most recent mood query
                if len(unanswered_requests) > 0:
                    return self.process_mood_response(
                        evt, input_split[-1], unanswered_requests[-1].mood_time, mood_day
                    )
                return evt.reply(evt.create_response(
                    "Is this a mood measurement, because I can't find a mood query."
                ))
            # Check if it's a more complicated message
            if len(input_split) == 3 and input_split[0].upper() == self.mood_acronym():
                input_time = input_split[1]
                time_val = None
                if input_time.lower() in hallo.modules.dailys.field_sleep.DailysSleepField.WAKE_WORDS:
                    time_val = MoodTime(MoodTime.WAKE)
                elif input_time.lower() in hallo.modules.dailys.field_sleep.DailysSleepField.SLEEP_WORDS:
                    time_val = MoodTime(MoodTime.SLEEP)
                else:
                    try:
                        time_val = MoodTime(time(int(input_time[:2]), int(input_time[-2:])))
                    except ValueError:
                        return evt.reply(evt.create_response(
                            "Could not parse the time in that mood measurement."
                        ))
                if not self.time_list.contains_time(time_val):
                    return evt.reply(evt.create_response(
                        "That time value is not being tracked for mood measurements."
                    ))
                return self.process_mood_response(evt, input_split[-1], time_val, mood_day)
        return None

    def mood_acronym(self) -> str:
        return "".join([m[0] for m in self.moods]).upper()

    def send_mood_query(self, mood_day: MoodDay, time_val: MoodTime) -> None:
        # Construct message
        msg = (
            "Hello, this is your {} mood check. How are you feeling (scale from 1-5) "
            "in these categories: {}".format(time_val, ", ".join(self.moods))
        )
        # Send message
        evt = self.message_channel(msg)
        # Get message_id, if telegram outbound message
        sent_msg_id = -1
        if isinstance(evt.raw_data, RawDataTelegramOutbound):
            sent_msg_id = evt.raw_data.sent_msg_object.message_id
        # Update data
        with self.lock:
            mood_day.add_request(time_val, sent_msg_id)
            self.save_day(mood_day)
        return None

    def process_mood_response(self, evt: EventMessage, mood_str: str, time_val: MoodTime, mood_day: MoodDay) -> None:
        if len(mood_str) != len(self.moods):
            return evt.reply(evt.create_response(
                "This mood measurement doesn't seem to have the right number of datapoints"
            ))
        with self.lock:
            measurement_data = {
                mood_key: mood_val for mood_key, mood_val in zip(self.moods, [int(x) for x in mood_str])
            }
            mood_day.set_measurement(time_val, measurement_data)
            self.save_day(mood_day)
        return evt.reply(evt.create_response(
            f"Added mood stat {mood_str} for time: {time_val} and date: {mood_day.mood_date.isoformat()}"
        ))

    def save_day(self, mood_day: MoodDay) -> None:
        data = mood_day.to_dict()
        self.save_data(data, mood_day.mood_date)

    def to_json(self):
        return {
            "type_name": self.type_name
        }

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysMoodField.create_from_spreadsheet(spreadsheet)
