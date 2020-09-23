from datetime import timedelta

from hallo.events import EventMessage
from hallo.modules.dailys.dailys_field import DailysField


class DailysSleepField(DailysField):
    # Does sleep and wake times, sleep notes, dream logs, shower?
    type_name = "sleep"
    WAKE_WORDS = ["morning", "wake", "woke"]
    SLEEP_WORDS = ["goodnight", "sleep", "nini", "night"]
    json_key_wake_time = "wake_time"
    json_key_sleep_time = "sleep_time"
    json_key_interruptions = "interruptions"

    @staticmethod
    def create_from_input(event, spreadsheet):
        return DailysSleepField(spreadsheet)

    @staticmethod
    def passive_events():
        return [EventMessage]

    def passive_trigger(self, evt):
        """
        :type evt: EventMessage
        :rtype: None
        """
        input_clean = evt.text.strip().lower()
        now = evt.get_send_time()
        time_str = now.isoformat()
        sleep_date = evt.get_send_time().date()
        current_data = self.load_data(sleep_date)
        if current_data is None:
            current_data = dict()
        yesterday_date = sleep_date - timedelta(1)
        yesterday_data = self.load_data(yesterday_date)
        if yesterday_data is None:
            yesterday_data = dict()
        # If user is waking up
        if input_clean in DailysSleepField.WAKE_WORDS:
            # If today's data is blank, write in yesterday's sleep data
            if len(current_data) == 0:
                current_data = yesterday_data
                sleep_date = yesterday_date
            # If you already woke in this data, why are you waking again?
            if self.json_key_wake_time in current_data:
                self.message_channel("Didn't you already wake up?")
                return
            # If not, add a wake time to sleep data
            else:
                current_data[self.json_key_wake_time] = time_str
                self.save_data(current_data, sleep_date)
                self.message_channel("Good morning!")
                return
        # If user is going to sleep
        if input_clean in DailysSleepField.SLEEP_WORDS:
            # If it's before 4pm, it's probably yesterday's sleep.
            if now.hour <= 16:
                current_data = yesterday_data
                sleep_date = yesterday_date
            # Did they already go to sleep?
            if self.json_key_sleep_time in current_data:
                # Did they already wake? If not, they're updating their sleep time.
                if self.json_key_wake_time not in current_data:
                    current_data[self.json_key_sleep_time] = time_str
                    self.save_data(current_data, sleep_date)
                    self.message_channel("Good night again!")
                    return
                # Move the last wake time to interruptions
                interruption = dict()
                interruption[self.json_key_wake_time] = current_data.pop(
                    self.json_key_wake_time
                )
                interruption[self.json_key_sleep_time] = time_str
                if self.json_key_interruptions not in current_data:
                    current_data[self.json_key_interruptions] = []
                current_data[self.json_key_interruptions].append(interruption)
                self.save_data(current_data, sleep_date)
                self.message_channel("Oh, going back to sleep? Sleep well!")
                return
            # Otherwise they're headed to sleep
            else:
                current_data[self.json_key_sleep_time] = time_str
                self.save_data(current_data, sleep_date)
                self.message_channel("Goodnight!")
                return

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysSleepField(spreadsheet)