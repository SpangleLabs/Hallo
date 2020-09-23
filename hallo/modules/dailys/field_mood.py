from datetime import timedelta, datetime, time
from threading import RLock

from hallo.events import EventMessage, EventMinute, RawDataTelegram, RawDataTelegramOutbound
from hallo.modules.dailys.dailys_field import DailysField, DailysException
from hallo.modules.dailys.field_sleep import DailysSleepField


class DailysMoodField(DailysField):
    type_name = "mood"
    # Does mood measurements
    TIME_WAKE = "WakeUpTime"  # Used as a time entry, to signify that it should take a mood measurement in the morning,
    # after wakeup has been logged.
    TIME_SLEEP = "SleepTime"  # Used as a time entry to signify that a mood measurement should be taken before sleep.

    class MoodTriggeredCache:
        def __init__(self):
            self.cache = (
                dict()
            )  # Cache of time values which have triggered already on set days.
            """ :type : dict[date, list[time|str]"""

        def has_triggered(self, mood_date, time_val):
            return mood_date in self.cache and time_val in self.cache[mood_date]

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

    def __init__(self, spreadsheet, times, moods):
        super().__init__(spreadsheet)
        self.times = times
        """ :type : list[time|str]"""
        self.moods = moods
        """ :type : list[str]"""
        self.lock = RLock()
        self.triggered_cache = DailysMoodField.MoodTriggeredCache()

    @staticmethod
    def create_from_input(event, spreadsheet):
        static_data = spreadsheet.read_path("stats/mood/static/")
        if len(static_data) == 0:
            raise DailysException("Mood field static data has not been set up on dailys system.")
        moods = static_data[0]["data"]["moods"]
        times = []
        for time_str in static_data[0]["data"]["times"]:
            if time_str in [DailysMoodField.TIME_WAKE, DailysMoodField.TIME_SLEEP]:
                times.append(time_str)
            else:
                times.append(datetime.strptime(time_str, "%H:%M:%S").time())
        # Return new field
        return DailysMoodField(spreadsheet, times, moods)

    @staticmethod
    def passive_events():
        return [EventMessage, EventMinute]

    def get_current_data(self, mood_date):
        """
        Returns the current mood data, and the day offset. Which might be today's or it could be yesterday's,
        if that is not done yet.
        :type mood_date: date
        :return: (dict, date)
        """
        with self.lock:
            # Get today's data, unless it's empty, then get yesterday's, unless it's full, then use today's.
            yesterday_date = mood_date - timedelta(1)
            today_data = self.load_data(mood_date)
            if today_data is None:
                yesterday_data = self.load_data(yesterday_date)
                if yesterday_data is None:
                    return dict(), mood_date
                if self.mood_data_is_full(yesterday_data):
                    return dict(), mood_date
                return yesterday_data, yesterday_date
            return today_data, mood_date

    def mood_data_is_full(self, date_data):
        return len(date_data) == len(self.times) and all(
            [m in date_data[str(t)] for t in self.times for m in self.moods]
        )

    def has_triggered_for_time(self, mood_date, time_val):
        """
        :type mood_date: date
        :type time_val: str|time
        :return: bool
        """
        # Check cache for true values
        if self.triggered_cache.has_triggered(mood_date, time_val):
            return True
        # Get the current data
        data, adjusted_date = self.get_current_data(mood_date)
        # If sleep message, and today hasn't got previous mood measurements, return true (don't cache)
        if time_val is self.TIME_SLEEP and len(self.times) > 1 and len(data) == 0:
            return True
        # See if time has been queried or measured
        triggered = self.time_triggered(data, time_val)
        # Update cache
        if triggered:
            self.triggered_cache.save_triggered(adjusted_date, time_val)
        return triggered

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: None
        """
        mood_date = evt.get_send_time().date()
        if isinstance(evt, EventMinute):
            # Get the largest time which is less than the current time. If none, do nothing.
            times = [t for t in self.times if isinstance(t, time)]
            past_times = [t for t in times if t < evt.get_send_time().time()]
            if len(past_times) == 0:
                return
            latest_time = max(past_times)
            if not self.has_triggered_for_time(mood_date, latest_time):
                return self.send_mood_query(mood_date, latest_time)
            return
        if isinstance(evt, EventMessage):
            # Check if it's a morning/night message
            input_clean = evt.text.strip().lower()
            if (
                input_clean in DailysSleepField.WAKE_WORDS
                and self.TIME_WAKE in self.times
                and not self.has_triggered_for_time(mood_date, self.TIME_WAKE)
            ):
                return self.send_mood_query(mood_date, self.TIME_WAKE)
            if (
                input_clean in DailysSleepField.SLEEP_WORDS
                and self.TIME_SLEEP in self.times
                and not self.has_triggered_for_time(mood_date, self.TIME_SLEEP)
            ):
                return self.send_mood_query(mood_date, self.TIME_SLEEP)
            # Check if it's a reply to a mood message, or if there's an unanswered mood message
            input_split = input_clean.split()
            if (
                len(input_split) == 2 and input_split[0].upper() == self.mood_acronym()
            ) or input_clean.isdigit():
                data = self.get_current_data(mood_date)
                unreplied = self.get_unreplied_moods(mood_date)
                # Check if telegram message, and reply to a message
                if (
                    isinstance(evt.raw_data, RawDataTelegram)
                    and evt.raw_data.update_obj.message.reply_to_message is not None
                ):
                    reply_id = (
                        evt.raw_data.update_obj.message.reply_to_message.message_id
                    )
                    unreplied_ids = {
                        data[0][str(f)]["message_id"]: f for f in unreplied
                    }
                    if reply_id in unreplied_ids:
                        return self.process_mood_response(
                            input_split[-1], unreplied_ids[reply_id], data[1]
                        )
                # Otherwise, use the most recent mood query
                if len(unreplied) > 0:
                    return self.process_mood_response(
                        input_split[-1], unreplied[-1], data[1]
                    )
                return evt.create_response(
                    "Is this a mood measurement, because I can't find a mood query."
                )
            # Check if it's a more complicated message
            if len(input_split) == 3 and input_split[0].upper() == self.mood_acronym():
                data = self.get_current_data(mood_date)
                input_time = input_split[1]
                time_val = None
                if input_time.lower() in DailysSleepField.WAKE_WORDS:
                    time_val = DailysMoodField.TIME_WAKE
                if input_time.lower() in DailysSleepField.SLEEP_WORDS:
                    time_val = DailysMoodField.TIME_SLEEP
                if time_val is None:
                    try:
                        time_val = time(int(input_time[:2]), int(input_time[-2:]))
                    except ValueError:
                        evt.create_response(
                            "Could not parse the time in that mood measurement."
                        )
                if time_val not in self.times:
                    evt.create_response(
                        "That time value is not being tracked for mood measurements."
                    )
                return self.process_mood_response(input_split[-1], time_val, data[1])
        return None

    def mood_acronym(self):
        return "".join([m[0] for m in self.moods]).upper()

    def time_triggered(self, data, time_val):
        return str(time_val) in data

    def time_query_unreplied(self, data, time_val):
        return str(time_val) in data and len(data[str(time_val)]) <= 1

    def get_unreplied_moods(self, mood_date):
        data = self.get_current_data(mood_date)[0]
        unreplied = []
        # Check for wake time
        if DailysMoodField.TIME_WAKE in self.times:
            # Check if time in data, message_id in time data, but mood values are not
            if self.time_triggered(
                data, DailysMoodField.TIME_WAKE
            ) and self.time_query_unreplied(data, DailysMoodField.TIME_WAKE):
                unreplied.append(DailysMoodField.TIME_WAKE)
        # Check for time values
        times = [t for t in self.times if isinstance(t, time)]
        for time_val in times:
            if self.time_triggered(data, time_val) and self.time_query_unreplied(
                data, time_val
            ):
                unreplied.append(time_val)
        # Check for sleep time
        if DailysMoodField.TIME_SLEEP in self.times:
            if self.time_triggered(
                data, DailysMoodField.TIME_SLEEP
            ) and self.time_query_unreplied(data, DailysMoodField.TIME_SLEEP):
                unreplied.append(DailysMoodField.TIME_SLEEP)
        return unreplied

    def send_mood_query(self, mood_date, time_val):
        """
        :type mood_date: date
        :type time_val: str | datetime.time
        :rtype: None
        """
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
            data = self.get_current_data(mood_date)
            data[0][str(time_val)] = dict()
            data[0][str(time_val)]["message_id"] = sent_msg_id
            self.save_data(data[0], data[1])
        return None

    def process_mood_response(self, mood_str, time_val, mood_date):
        """
        :type mood_str: str
        :type time_val: str | datetime.time
        :type mood_date: date
        :rtype: None
        """
        with self.lock:
            data = self.get_current_data(mood_date)
            if str(time_val) not in data[0]:
                data[0][str(time_val)] = dict()
            for mood_key, mood_val in zip(self.moods, [int(x) for x in mood_str]):
                data[0][str(time_val)][mood_key] = mood_val
            self.save_data(data[0], mood_date)
        self.message_channel(
            "Added mood stat {} for time: {} and date: {}".format(
                mood_str, time_val, mood_date.isoformat()
            )
        )

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["times"] = [str(t) for t in self.times]
        json_obj["moods"] = self.moods
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        static_data = spreadsheet.read_path("stats/mood/static/")
        if len(static_data) == 0:
            raise DailysException("Mood field static data has not been set up.")
        moods = static_data[0]["data"]["moods"]
        times = []
        for time_str in static_data[0]["data"]["times"]:
            if time_str in [DailysMoodField.TIME_WAKE, DailysMoodField.TIME_SLEEP]:
                times.append(time_str)
            else:
                times.append(datetime.strptime(time_str, "%H:%M:%S").time())
        return DailysMoodField(spreadsheet, times, moods)