import functools
from abc import ABC, abstractmethod
from datetime import time, datetime, date, timedelta
from typing import Union, Optional


@functools.total_ordering
class MoodTime:
    """
    MoodTime represents the time of a specific mood measurement. This will be wakeup, sleep, or a specified time
    """
    WAKE = "WakeUpTime"
    SLEEP = "SleepTime"

    def __init__(self, mood_time: Union[str, time]):
        self.mood_time = mood_time
        if mood_time not in [self.WAKE, self.SLEEP] and not isinstance(mood_time, time):
            raise TypeError("Invalid type for MoodTime")

    @classmethod
    def from_str(cls, time_str: str) -> 'MoodTime':
        if time_str in [cls.WAKE, cls.SLEEP]:
            return MoodTime(time_str)
        else:
            return MoodTime(datetime.strptime(time_str, "%H:%M:%S").time())

    def __eq__(self, other):
        return isinstance(other, MoodTime) and self.mood_time == other.mood_time

    def __hash__(self):
        return hash(self.mood_time)

    def __str__(self):
        return str(self.mood_time)

    def __lt__(self, other) -> bool:
        if not isinstance(other, MoodTime):
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
    """
    MoodDay represents a day of mood measurements, this converts into a full Dailys data entry dict
    """
    def __init__(self, mood_date: date, mood_entries: dict[MoodTime, 'MoodEntry']):
        self.mood_date = mood_date
        self.mood_entries = mood_entries or {}

    def to_dict(self) -> dict:
        result = {}
        for time_val, entry in self.mood_entries.items():
            result[str(time_val)] = entry.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Optional[dict], mood_date: date) -> 'MoodDay':
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

    def is_full(self, mood_times: list[MoodTime]) -> bool:
        return all(
            mood_time in self.mood_entries and isinstance(self.mood_entries[mood_time], MoodMeasurement)
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

    def list_unanswered_requests(self) -> list['MoodRequest']:
        return sorted(
            [m for m in self.mood_entries.values() if isinstance(m, MoodRequest)],
            key=lambda x: x.mood_time
        )

    def add_request(self, mood_time: MoodTime, message_id: Optional[int]) -> None:
        if message_id is None:
            return None
        request = MoodRequest(mood_time, message_id)
        self.mood_entries[mood_time] = request

    def set_measurement(self, time_val: MoodTime, measurement_data: dict[str, int]) -> None:
        if self.has_time(time_val):
            current = self.mood_entries[time_val]
            self.mood_entries[time_val] = current.to_measurement(measurement_data)
            return
        self.mood_entries[time_val] = MoodMeasurement(time_val, measurement_data)


class MoodEntry(ABC):
    """
    MoodEntry is an entry in the MoodDay data dictionary. It's aligned to a time, but it's possible it may be an entry
    without mood data yet (as it could be a confirmation that a mood request was sent).
    This is the raw data parsed from Dailys data, basically.
    """
    def __init__(self, mood_time: MoodTime, *, message_id: Optional[int] = None):
        self.mood_time = mood_time
        self.message_id = message_id

    @classmethod
    def from_data(cls, data: dict, mood_time: MoodTime) -> 'MoodEntry':
        if {"message_id"} == set(data.keys()):
            return MoodRequest.from_data(data, mood_time)
        return MoodMeasurement.from_data(data, mood_time)

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def to_measurement(self, measurement_data: dict[str, int]) -> 'MoodMeasurement':
        return MoodMeasurement(self.mood_time, measurement_data, self.message_id)


class MoodRequest(MoodEntry):
    """
    MoodRequest is a MoodEntry where Hallo has sent out a request for a mood measurement, but hasn't yet received the
    response
    """
    def __init__(self, mood_time: MoodTime, message_id: int):
        super().__init__(mood_time, message_id=message_id)

    @classmethod
    def from_data(cls, data: dict, mood_time: MoodTime) -> 'MoodRequest':
        return MoodRequest(
            mood_time,
            data["message_id"]
        )

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id
        }


class MoodMeasurement(MoodEntry):
    """
    MoodMeasurement is a MoodEntry where the mood measurement data has been supplied by the user
    """
    def __init__(self, mood_time: MoodTime, mood_dict: dict[str, int], message_id: Optional[int] = None):
        super().__init__(mood_time, message_id=message_id)
        self.mood_dict = mood_dict

    @classmethod
    def from_data(cls, data: dict, mood_time: MoodTime) -> 'MoodEntry':
        mood_data = data.copy()
        message_id = None
        if "message_id" in mood_data:
            message_id = mood_data["message_id"]
            del mood_data["message_id"]
        return MoodMeasurement(mood_time, mood_data, message_id=message_id)

    def to_dict(self) -> dict:
        result = self.mood_dict.copy()
        if self.message_id:
            result["message_id"] = self.message_id
        return result


class MoodTriggeredCache:
    """
    MoodTriggeredCache is a cache of dates to which mood measurements have triggered for that day
    """
    def __init__(self):
        self.cache: dict[date, list[Union[time, str]]] = {}
        # Cache of time values which have triggered already on set days.

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
    """
    MoodTimeList stores the list of times which mood measurements should be taken at each day
    """
    def __init__(self, mood_times: list[MoodTime]):
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
        if isinstance(mood_time, MoodTime):
            return mood_time in self.times
        return MoodTime(mood_time) in self.times
