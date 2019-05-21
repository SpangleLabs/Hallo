import json
import traceback
from abc import ABCMeta
from datetime import datetime, time, date, timedelta
from threading import RLock
from urllib.error import HTTPError

from Events import EventDay, EventMessage, EventMinute, RawDataTelegram, RawDataTelegramOutbound
from Function import Function
from inc.Commons import Commons
from modules.Subscriptions import FAKey
from modules.UserData import UserDataParser, FAKeyData


class DailysException(Exception):
    pass


class DailysRegister(Function):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "dailys register"
        # Names which can be used to address the function
        self.names = set([template.format(setup, dailys)
                          for template in ["{0} {1}", "{1} {0}"]
                          for setup in ["setup", "register"]
                          for dailys in ["dailys", "dailys api"]])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Registers a new dailys API to be fed from the current location." \
                         " Format: dailys register <dailys API URL>"

    def run(self, event):
        # Get dailys repo
        hallo = event.server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("dailys")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: Dailys
        dailys_repo = sub_check_obj.get_dailys_repo(hallo)
        # Check if there's already a spreadsheet here
        if dailys_repo.get_by_location(event) is not None:
            return event.create_response("There is already a dailys API configured in this location.")
        # Create new spreadsheet object
        clean_input = event.command_args.strip()
        spreadsheet = DailysSpreadsheet(event.user, event.channel, clean_input)
        # Check the stats/ endpoint returns a list.
        resp = Commons.load_url_json(clean_input)
        if not isinstance(resp, list):
            return event.create_response("Could not locate Dailys API at this URL.")
        # Save the spreadsheet
        dailys_repo.add_spreadsheet(spreadsheet)
        dailys_repo.save_json()
        # Send response
        return event.create_response("Dailys API found, currently with data for {}.".format(resp))


class DailysAddField(Function):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "add dailys field"
        # Names which can be used to address the function
        self.names = set([template.format(setup, dailys)
                          for template in ["{0} {1}", "{1} {0}"]
                          for setup in ["setup", "register", "add"]
                          for dailys in ["dailys field", "field to dailys"]])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Registers a new dailys field to the spreadsheet in the current chat location." \
                         " Format: add dailys field <field name>"

    def run(self, event):
        # Get spreadsheet repo
        hallo = event.server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("dailys")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: Dailys
        dailys_repo = sub_check_obj.get_dailys_repo(hallo)
        # Get the active spreadsheet for this person and destination
        spreadsheet = dailys_repo.get_by_location(event)
        if spreadsheet is None:
            return event.create_response("There is no dailys API configured in this channel. "
                                         "Please register a dailys API first with `dailys register`")
        # Get args
        clean_input = event.command_args.strip().lower()
        # If args are empty, list available fields
        if clean_input == "":
            return event.create_response("Please specify a field, available fields are: {}"
                                         .format(", ".join(field.type_name for field in DailysFieldFactory.fields)))
        # Check that there's exactly one field matching that name
        matching_fields = [field for field in DailysFieldFactory.fields if clean_input.startswith(field.type_name)]
        if len(matching_fields) != 1:
            return event.create_response("I don't understand what field you would like to add. "
                                         "Please specify a field less ambiguously.")
        # Try and create the field
        matching_field = matching_fields[0]
        new_field = matching_field.create_from_input(event, spreadsheet)
        # TODO: check if field already assigned, or if we already have a field of that type?
        spreadsheet.add_field(new_field)
        return event.create_response("Added a new field to your dailys API data.")


class Dailys(Function):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        # Name for use in help listing
        self.help_name = "dailys"
        # Names which can be used to address the function
        self.names = {"dailys"}
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Core dailys method, does all the dailys processing passively." \
                         " Doesn't do anything (currently) when called actively."
        self.dailys_repo = None
        """ :type : DailysRepo | None"""

    def get_dailys_repo(self, hallo):
        if self.dailys_repo is None:
            self.dailys_repo = DailysRepo.load_json(hallo)
        return self.dailys_repo

    @staticmethod
    def is_persistent():
        return True

    @staticmethod
    def load_function():
        """Loads the function, persistent functions only."""
        return Dailys()

    def save_function(self):
        """Saves the function, persistent functions only."""
        if self.dailys_repo is not None:
            self.dailys_repo.save_json()

    def get_passive_events(self):
        """Returns a list of events which this function may want to respond to in a passive way"""
        return set([event for field in DailysFieldFactory.fields for event in field.passive_events()])

    def run(self, event):
        pass  # TODO

    def passive_run(self, event, hallo_obj):
        repo = self.get_dailys_repo(hallo_obj)
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
                        field.passive_trigger(event)
                    except Exception as e:
                        # TODO
                        print("Dailys failure: {}".format(e))
                        print(traceback.format_exc())


class DailysRepo:

    def __init__(self):
        self.spreadsheets = []
        """ :type : list[DailysSpreadsheet]"""

    def add_spreadsheet(self, spreadsheet):
        """
        :type spreadsheet: DailysSpreadsheet
        """
        self.spreadsheets.append(spreadsheet)

    def get_by_location(self, event):
        for ds in self.spreadsheets:
            if ds.user == event.user and ds.destination == event.channel:
                return ds
        return None

    def save_json(self):
        json_obj = dict()
        json_obj["spreadsheets"] = []
        for spreadsheet in self.spreadsheets:
            json_obj["spreadsheets"].append(spreadsheet.to_json())
        # Write json to file
        with open("store/dailys.json", "w+") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json(hallo):
        new_dailys_repo = DailysRepo()
        # Try loading json file, otherwise return blank list
        try:
            with open("store/dailys.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            return new_dailys_repo
        for spreadsheet_json in json_obj["spreadsheets"]:
            spreadsheet = DailysSpreadsheet.from_json(spreadsheet_json, hallo)
            new_dailys_repo.add_spreadsheet(spreadsheet)
        return new_dailys_repo


class DailysSpreadsheet:

    def __init__(self, user, destination, dailys_url):
        """
        :type user: Destination.User
        :type destination: Destination.Destination
        """
        self.user = user
        """ :type : Destination.User"""
        self.destination = destination
        """ :type : Destination.Destination | None"""
        self.dailys_url = dailys_url
        if self.dailys_url[-1] == "/":
            self.dailys_url = self.dailys_url[:-1]
        """ :type : str"""
        self.fields_list = []
        """ :type : list[DailysField]"""

    def add_field(self, field):
        """
        :type field: DailysField
        """
        self.fields_list.append(field)

    def save_field(self, dailys_field, data, data_date):
        """
        Save given data in a specified column for the current date row.
        # TODO: change data for dict
        :type dailys_field: DailysField
        :type data: str
        :type data_date: date
        """
        if dailys_field.type_name is None:
            raise DailysException("Cannot write to unassigned dailys field")
        Commons.put_json_to_url(
            "{}/stats/{}/{}/?source=Hallo".format(self.dailys_url, dailys_field.type_name, data_date.isoformat()),
            json.loads(data)
        )

    def read_field(self, dailys_field, data_date):
        """
        Save given data in a specified column for the current date row.
        :type dailys_field: DailysField
        :type data_date: date
        :rtype: str | None
        """
        if dailys_field.type_name is None:
            raise DailysException("Cannot read from unassigned dailys field")
        data = Commons.load_url_json(
            "{}/stats/{}/{}/".format(self.dailys_url, dailys_field.type_name, data_date.isoformat())
        )
        if len(data) == 0:
            return None
        return json.dumps(data[0]['data'])

    def to_json(self):
        json_obj = dict()
        json_obj["server_name"] = self.user.server.name
        json_obj["user_address"] = self.user.address
        if self.destination is not None:
            json_obj["dest_address"] = self.destination.address
        json_obj["dailys_url"] = self.dailys_url
        json_obj["fields"] = []
        for field in self.fields_list:
            json_obj["fields"].append(field.to_json())
        return json_obj

    @staticmethod
    def from_json(json_obj, hallo):
        server = hallo.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise DailysException("Could not find server with name \"{}\"".format(json_obj["server"]))
        user = server.get_user_by_address(json_obj["user_address"])
        if user is None:
            raise DailysException("Could not find user with address \"{}\" on server \"{}\""
                                  .format(json_obj["user_address"], json_obj["server"]))
        dest_chan = None
        if "dest_address" in json_obj:
            dest_chan = server.get_channel_by_address(json_obj["dest_address"])
            if dest_chan is None:
                raise DailysException("Could not find channel with address \"{}\" on server \"{}\""
                                      .format(json_obj["dest_address"], json_obj["server"]))
        dailys_url = json_obj["dailys_url"]
        new_spreadsheet = DailysSpreadsheet(user, dest_chan, dailys_url)
        for field_json in json_obj["fields"]:
            new_spreadsheet.add_field(DailysFieldFactory.from_json(field_json, new_spreadsheet))
        return new_spreadsheet


class DailysField(metaclass=ABCMeta):
    # An abstract class representing an individual dailys field type.
    # A field can/will be multiple columns, maybe a varying quantity of them by configuration
    type_name = None

    def __init__(self, spreadsheet):
        """
        :type spreadsheet: DailysSpreadsheet
        """
        self.spreadsheet = spreadsheet
        """ :type : DailysSpreadsheet"""

    @staticmethod
    def create_from_input(event, spreadsheet):
        """
        :type event: EventMessage
        :type spreadsheet: DailysSpreadsheet
        :rtype: DailysField
        """
        raise NotImplementedError()

    @staticmethod
    def passive_events():
        raise NotImplementedError()

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: None
        """
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj, spreadsheet):
        raise NotImplementedError()

    def save_data(self, data, data_date):
        """
        :type data: str | dict
        :type data_date: date
        """
        data_str = data
        if isinstance(data, dict):
            data_str = json.dumps(data)
        self.spreadsheet.save_field(self, data_str, data_date=data_date)

    def load_data(self, data_date):
        """
        :type data_date: date
        :rtype: str | None
        """
        return self.spreadsheet.read_field(self, data_date)

    def message_channel(self, text):
        """
        :type text: str
        :rtype : EventMessage
        """
        evt = EventMessage(self.spreadsheet.destination.server,
                           self.spreadsheet.destination,
                           self.spreadsheet.user,
                           text,
                           inbound=False)
        self.spreadsheet.user.server.send(evt)
        return evt


class DailysFAField(DailysField):
    type_name = "furaffinity"
    col_names = ["furaffinity", "fa notifications", "furaffinity notifications"]

    @staticmethod
    def passive_events():
        """
        :rtype: list[type]
        """
        return [EventDay]

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: None
        """
        user_parser = UserDataParser()
        fa_data = user_parser.get_data_by_user_and_type(self.spreadsheet.user, FAKeyData)  # type: FAKeyData
        if fa_data is None:
            raise DailysException("No FA data has been set up for the FA field module to use.")
        fa_key = FAKey(self.spreadsheet.user, fa_data.cookie_a, fa_data.cookie_b)
        notif_page = fa_key.get_fa_reader().get_notification_page()
        notifications = dict()
        notifications["submissions"] = notif_page.total_submissions
        notifications["comments"] = notif_page.total_comments
        notifications["journals"] = notif_page.total_journals
        notifications["favourites"] = notif_page.total_favs
        notifications["watches"] = notif_page.total_watches
        notifications["notes"] = notif_page.total_notes
        notif_str = json.dumps(notifications)
        d = (evt.get_send_time() - timedelta(1)).date()
        self.save_data(notif_str, d)
        # Send date to destination
        self.message_channel(notif_str)

    @staticmethod
    def create_from_input(event, spreadsheet):
        # Check user has an FA login
        user_parser = UserDataParser()
        fa_data = user_parser.get_data_by_user_and_type(spreadsheet.user, FAKeyData)  # type: FAKeyData
        if fa_data is None:
            raise DailysException("No FA data has been set up for the FA dailys field to use.")
        return DailysFAField(spreadsheet)

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysFAField(spreadsheet)


class DailysSleepField(DailysField):
    # Does sleep and wake times, sleep notes, dream logs, shower?
    type_name = "sleep"
    col_names = ["sleep", "sleep times"]
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
        current_str = self.load_data(sleep_date)
        if current_str is None or current_str == "":
            current_data = dict()
        else:
            current_data = json.loads(current_str)
        yesterday_date = sleep_date - timedelta(1)
        yesterday_str = self.load_data(yesterday_date)
        if yesterday_str is None or yesterday_str == "":
            yesterday_data = dict()
        else:
            yesterday_data = json.loads(yesterday_str)
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
                interruption[self.json_key_wake_time] = current_data.pop(self.json_key_wake_time)
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


class DailysMoodField(DailysField):
    col_names = ["mood", "hallo mood", "mood summary"]
    type_name = "mood"
    # Does mood measurements
    TIME_WAKE = "WakeUpTime"  # Used as a time entry, to signify that it should take a mood measurement in the morning,
    # after wakeup has been logged.
    TIME_SLEEP = "SleepTime"  # Used as a time entry to signify that a mood measurement should be taken before sleep.

    class MoodTriggeredCache:
        def __init__(self):
            self.cache = dict()  # Cache of time values which have triggered already on set days.
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
        clean_input = event.command_args[len(DailysMoodField.type_name):].strip()
        input_split = clean_input.split(";")
        if len(input_split) not in [2, 3]:
            raise DailysException("Mood setup must contain times, then a semicolon, then mood measurements.")
        input_times = input_split[0].lower()
        input_moods = input_split[1]
        # Parse times
        times = []
        for input_time in input_times.split():
            # Check if it's a 24hour time
            if len(input_time.replace(":", "")) == 4 and input_time.replace(":", "").isdigit():
                try:
                    times.append(time(int(input_time[:2]), int(input_time[-2:])))
                    continue
                except ValueError:
                    raise DailysException("Please provide times as 24 hour hh:mm formatted times.")
            # Check if it's wake or sleep
            if input_time in DailysSleepField.WAKE_WORDS:
                times.append(DailysMoodField.TIME_WAKE)
                continue
            if input_time in DailysSleepField.SLEEP_WORDS:
                times.append(DailysMoodField.TIME_SLEEP)
                continue
            raise DailysException("I don't recognise that time, \"{}\". Please provide times as 24 hour hh:mm "
                                  "formatted times, or 'wake' or 'sleep'.".format(input_time))
        # Parse mood measurements
        moods = input_moods.split()
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
            today_str = self.load_data(mood_date)
            if today_str is None or today_str == "":
                yesterday_str = self.load_data(yesterday_date)
                if yesterday_str is None or yesterday_str == "":
                    return dict(), mood_date
                yesterday_data = json.loads(yesterday_str)
                if self.mood_data_is_full(yesterday_data):
                    return dict(), mood_date
                return yesterday_data, yesterday_date
            today_data = json.loads(today_str)
            return today_data, mood_date

    def mood_data_is_full(self, date_data):
        return len(date_data) == len(self.times) and \
               all([m in date_data[str(t)] for t in self.times for m in self.moods])

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
            if input_clean in DailysSleepField.WAKE_WORDS and self.TIME_WAKE in self.times and \
                    not self.has_triggered_for_time(mood_date, self.TIME_WAKE):
                return self.send_mood_query(mood_date, self.TIME_WAKE)
            if input_clean in DailysSleepField.SLEEP_WORDS and self.TIME_SLEEP in self.times and \
                    not self.has_triggered_for_time(mood_date, self.TIME_SLEEP):
                return self.send_mood_query(mood_date, self.TIME_SLEEP)
            # Check if it's a reply to a mood message, or if there's an unanswered mood message
            input_split = input_clean.split()
            if (len(input_split) == 2 and input_split[0].upper() == self.mood_acronym()) or input_clean.isdigit():
                data = self.get_current_data(mood_date)
                unreplied = self.get_unreplied_moods(mood_date)
                # Check if telegram message, and reply to a message
                if isinstance(evt.raw_data, RawDataTelegram) and \
                        evt.raw_data.update_obj.message.reply_to_message is not None:
                    reply_id = evt.raw_data.update_obj.message.reply_to_message.message_id
                    unreplied_ids = {data[0][str(f)]["message_id"]: f for f in unreplied}
                    if reply_id in unreplied_ids:
                        return self.process_mood_response(input_split[-1], unreplied_ids[reply_id], data[1])
                # Otherwise, use the most recent mood query
                if len(unreplied) > 0:
                    return self.process_mood_response(input_split[-1], unreplied[-1], data[1])
                return evt.create_response("Is this a mood measurement, because I can't find a mood query.")
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
                        evt.create_response("Could not parse the time in that mood measurement.")
                if time_val not in self.times:
                    evt.create_response("That time value is not being tracked for mood measurements.")
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
            if self.time_triggered(data, DailysMoodField.TIME_WAKE) and \
                    self.time_query_unreplied(data, DailysMoodField.TIME_WAKE):
                unreplied.append(DailysMoodField.TIME_WAKE)
        # Check for time values
        times = [t for t in self.times if isinstance(t, time)]
        for time_val in times:
            if self.time_triggered(data, time_val) and self.time_query_unreplied(data, time_val):
                unreplied.append(time_val)
        # Check for sleep time
        if DailysMoodField.TIME_SLEEP in self.times:
            if self.time_triggered(data, DailysMoodField.TIME_SLEEP) and \
                    self.time_query_unreplied(data, DailysMoodField.TIME_SLEEP):
                unreplied.append(DailysMoodField.TIME_SLEEP)
        return unreplied

    def send_mood_query(self, mood_date, time_val):
        """
        :type mood_date: date
        :type time_val: str | datetime.time
        :rtype: None
        """
        # Construct message
        msg = "Hello, this is your {} mood check. How are you feeling (scale from 1-5) " \
              "in these categories: {}".format(time_val, ", ".join(self.moods))
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
            "Added mood stat {} for time: {} and date: {}".format(mood_str, time_val, mood_date.isoformat()))

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["times"] = [str(t) for t in self.times]
        json_obj["moods"] = self.moods
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        moods = json_obj["moods"]
        times = []
        for time_str in json_obj["times"]:
            if time_str in [DailysMoodField.TIME_WAKE, DailysMoodField.TIME_SLEEP]:
                times.append(time_str)
            else:
                times.append(datetime.strptime(time_str, "%H:%M:%S").time())
        return DailysMoodField(spreadsheet, times, moods)


class DailysAnimalsField(DailysField):
    # Does animal sightings measurements

    def get_animal_list(self):
        # Return a list of animals which are being logged
        pass


class DailysDuolingoField(DailysField):
    type_name = "duolingo"
    col_names = ["duolingo", "duolingo friends", "duolingo friends list"]

    def __init__(self, spreadsheet, username):
        super().__init__(spreadsheet)
        self.username = username

    @staticmethod
    def passive_events():
        """
        :rtype: list[type]
        """
        return [EventDay]

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: None
        """
        duo = Commons.load_url_json("https://www.duolingo.com/users/{}".format(self.username))
        result = dict()
        for lang in duo["language_data"]:
            for friend in duo["language_data"][lang]["points_ranking_data"]:
                result[friend["username"]] = friend["points_data"]["total"]
        result_str = json.dumps(result)
        d = (evt.get_send_time() - timedelta(1)).date()
        self.save_data(result_str, d)
        # Send date to destination
        self.message_channel(result_str)

    @staticmethod
    def _check_duo_username(username):
        try:
            Commons.load_url_json("https://www.duolingo.com/users/{}".format(username))
            return True
        except HTTPError:
            return False

    @staticmethod
    def _check_spreadsheet_col_name(col_name):
        return len(col_name) <= 3 and col_name.isalpha()

    @staticmethod
    def create_from_input(event, spreadsheet):
        clean_input = event.command_args[len(DailysDuolingoField.type_name):].strip()
        if DailysDuolingoField._check_duo_username(clean_input):
            return DailysDuolingoField(spreadsheet, clean_input)
        else:
            raise DailysException("Could not find a duolingo account with that username.")

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["username"] = self.username
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysDuolingoField(spreadsheet, json_obj["username"])


class DailysSplooField(DailysField):
    pass


class DailysShowerField(DailysField):
    # Temperature, song, whatever
    pass


class DailysCaffeineField(DailysField):
    # At new_day(), can input N, none if there's no entry today
    pass


class DailysShavingField(DailysField):
    # At new_day(), can input N, N, none, none if there's no entry today
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


class DailysFieldFactory:
    fields = [DailysFAField, DailysDuolingoField, DailysSleepField, DailysMoodField]

    @staticmethod
    def from_json(json_obj, spreadsheet):
        type_name = json_obj["type_name"]
        for field in DailysFieldFactory.fields:
            if field.type_name == type_name:
                return field.from_json(json_obj, spreadsheet)
        raise DailysException("Could not load dailys field of type {}".format(type_name))
