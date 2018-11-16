import json
import uuid
from abc import ABCMeta
from datetime import datetime

import dateutil.parser

from Events import EventDay, EventMessage
from Function import Function
from inc.Commons import CachedObject, Commons
from modules.Subscriptions import FAKey
from modules.UserData import UserDataParser, FAKeyData
from googleapiclient.discovery import build
from oauth2client import file
from httplib2 import Http


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
                          for dailys in ["dailys", "dailys spreadsheet"]])
        # Help documentation, if it's just a single line, can be set here
        self.help_docs = "Registers a new dailys spreadsheet to be fed from the current location." \
                         " Format: dailys register <google spreadsheet ID>"

    def run(self, event):
        # Get dailys repo
        hallo = event.server.hallo
        function_dispatcher = hallo.function_dispatcher
        sub_check_function = function_dispatcher.get_function_by_name("dailys")
        sub_check_obj = function_dispatcher.get_function_object(sub_check_function)  # type: Dailys
        dailys_repo = sub_check_obj.get_dailys_repo(hallo)
        # Check if there's already a spreadsheet here
        if dailys_repo.get_by_location(event) is not None:
            return event.create_response("There is already a spreadsheet configured in this location.")
        # Create new spreadsheet object
        clean_input = event.command_args.strip()
        spreadsheet = DailysSpreadsheet(event.user, event.channel, clean_input)
        # Check a bunch of things can be detected, which also set the cache for them.
        hallo_key_row = spreadsheet.hallo_key_row.get()
        if hallo_key_row is None:
            return event.create_response("Could not locate hallo key row in spreadsheet. "
                                         "Please add one (and only one) header row labelled \"hallo key\", "
                                         "for hallo to store column references in.")
        date_col = spreadsheet.date_column.get()
        if hallo_key_row is None:
            return event.create_response("Could not locate date column in spreadsheet. "
                                         "Please add one (and only one) label column titled \"date\".")
        date_start = spreadsheet.get_first_date()
        if date_start is None:
            return event.create_response("Could not find the first date in the date column of the spreadsheet. "
                                         "Please add an initial date to the spreadsheet")
        # Save the spreadsheet
        dailys_repo.add_spreadsheet(spreadsheet)
        dailys_repo.save_json()
        # Send response
        return event.create_response("Dailys spreadsheet found, with hallo keys in row {}, "
                                     "dates in column {}, "
                                     "and starting from {}".format(hallo_key_row+1,
                                                                   spreadsheet.col_num_to_string(date_col),
                                                                   date_start.date()))


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
        self.help_docs = "Registers a new dailys spreadsheet to be fed from the current location." \
                         " Format: dailys register <google spreadsheet ID>"

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
            return event.create_response("There is no spreadsheet configured in this channel. "
                                         "Please register a spreadsheet first with `dailys register`")
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
        return event.create_response("Added a new field to your dailys spreadsheet.")


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
        self.help_docs = "Core dailys method, does .. a bunch of stuff I guess?." \
                         " Format: dailys"  # TODO
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
            spreadsheets = [repo.get_by_location(event)]
        for spreadsheet in spreadsheets:
            for field in spreadsheet.fields_list:
                if event.__class__ in field.passive_events():
                    try:
                        field.passive_trigger(event)
                    except Exception as e:
                        print("Dailys failure: {}".format(e))


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

    def __init__(self, user, destination, spreadsheet_id):
        """
        :type user: Destination.User
        :type destination: Destination.Destination
        """
        self.user = user
        """ :type : Destination.User"""
        self.destination = destination
        """ :type : Destination.Channel | None"""
        self.spreadsheet_id = spreadsheet_id
        """ :type : str"""
        self.first_sheet_name = CachedObject(self.find_first_sheet_name)
        """ :type : CachedObject"""
        self.hallo_key_row = CachedObject(self.find_hallo_key_row)
        """ :type : CachedObject"""
        self.date_column = CachedObject(self.find_date_column)
        """ :type : CachedObject"""
        self.first_date_pair = CachedObject(self.find_first_date)
        """ :type : CachedObject"""
        self.fields_list = []
        """ :type : list[DailysField]"""

    def get_spreadsheet_service(self):
        store = file.Storage('store/google-oauth-token.json')
        creds = store.get()
        if not creds or creds.invalid:
            raise DailysException("Google oauth token is not valid. "
                                  "Please run store/google-oauth-import.py somewhere with a UI")
        return build('sheets', 'v4', http=creds.authorize(Http()))

    def get_spreadsheet_range(self, val_range):
        service = self.get_spreadsheet_service()
        result = service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                     range=val_range).execute()
        return result.get('values', [])

    def update_spreadsheet_cell(self, cell, data):
        service = self.get_spreadsheet_service()
        body = {"values": [[data]]}
        request = service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id,
                                                         range=cell,
                                                         valueInputOption="RAW",
                                                         body=body)
        return request.execute()

    def find_first_sheet_name(self):
        service = self.get_spreadsheet_service()
        sheet_metadata = service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        name = sheets[0].get("properties", {}).get("title", "Sheet1")
        return "'{}'".format(name)

    def find_hallo_key_row(self):
        test_range = '{}!A1:J10'.format(self.first_sheet_name.get())
        rows = self.get_spreadsheet_range(test_range)
        sub_str = "hallo key"
        match_count = 0
        match_row = None
        for row_num in range(len(rows)):
            if any([sub_str in elem.lower() for elem in rows[row_num]]):
                match_count += 1
                match_row = row_num
                if match_count > 1:
                    match_row = None
                    break
        return match_row

    def find_column_by_names(self, names):
        col_range = "{}!A1:10".format(self.first_sheet_name.get())
        header_rows = self.get_spreadsheet_range(col_range)
        max_cols = max([len(row) for row in header_rows])
        match_col = None
        match_count = 0
        for col_num in range(max_cols):
            for row in header_rows:
                if col_num < len(row) and any(name in row[col_num].lower() for name in names):
                    match_col = col_num
            if match_col == col_num:
                match_count += 1
            if match_count > 1:
                match_col = None
                break
        return match_col

    def tag_column(self, col_title):
        key = str(uuid.uuid4())
        cell = "{}!{}{}".format(self.first_sheet_name.get(), col_title, self.hallo_key_row.get()+1)
        self.update_spreadsheet_cell(cell, key)
        return key

    def find_and_tag_column_by_names(self, names):
        col = self.find_column_by_names(names)
        if col is None:
            return None
        return self.tag_column(self.col_num_to_string(col))

    def get_column_by_field_id(self, field_id):
        hallo_row = self.hallo_key_row.get()
        field_id_range = "{0}!A{1}:{1}".format(self.first_sheet_name.get(), hallo_row+1)
        row = self.get_spreadsheet_range(field_id_range)[0]
        return row.index(field_id)

    def find_date_column(self):
        return self.find_column_by_names(["date"])

    def col_num_to_string(self, num):
        string = ""
        num += 1
        while num > 0:
            num, remainder = divmod(num - 1, 26)
            string = chr(65 + remainder) + string
        return string

    def find_first_date(self):
        date_col = self.date_column.get()
        date_col_name = self.col_num_to_string(date_col)
        date_range = self.get_spreadsheet_range("{0}!{1}1:{1}".format(self.first_sheet_name.get(), date_col_name))
        first_date = None
        first_date_row = None
        for row_num in range(len(date_range)):
            try:
                first_date = dateutil.parser.parse(date_range[row_num][0], dayfirst=True)
                first_date_row = row_num
                break
            except ValueError:
                continue
            except IndexError:
                continue
        return first_date_row, first_date

    def get_first_date_row(self):
        return self.first_date_pair.get()[0]

    def get_first_date(self):
        return self.first_date_pair.get()[1]

    def get_current_date_row(self):
        first_date_row, first_date = self.first_date_pair.get()
        current_date = self.get_current_date()
        return (current_date-first_date).days + first_date_row

    def add_field(self, field):
        """
        :type field: DailysField
        """
        self.fields_list.append(field)

    def get_current_date(self):
        # Return the current date. Not equal to calendar date, as user may be awake after midnight
        # TODO: roman dates, need to track sleep for that?
        return datetime.now()

    def save_field(self, dailys_field, data):
        """
        Save given data in a specified column for the current date row.
        :type dailys_field: DailysField
        :type data: str
        """
        col_num = self.get_column_by_field_id(dailys_field.hallo_key_field_id)
        row_num = self.get_current_date_row()
        self.update_spreadsheet_cell("{}!{}{}".format(self.first_sheet_name.get(),
                                                      self.col_num_to_string(col_num),
                                                      row_num+1),
                                     data)

    def read_field(self, dailys_field):
        """
        Save given data in a specified column for the current date row.
        :type dailys_field: DailysField
        :rtype: str
        """
        col_num = self.get_column_by_field_id(dailys_field.hallo_key_field_id)
        row_num = self.get_current_date_row()
        self.get_spreadsheet_range("{}!{}{}".format(self.first_sheet_name.get(),
                                                      self.col_num_to_string(col_num),
                                                      row_num+1))

    def to_json(self):
        json_obj = dict()
        json_obj["server_name"] = self.user.server.name
        json_obj["user_address"] = self.user.address
        if self.destination is not None:
            json_obj["dest_address"] = self.destination.address
        json_obj["spreadsheet_id"] = self.spreadsheet_id
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
        spreadsheet_id = json_obj["spreadsheet_id"]
        new_spreadsheet = DailysSpreadsheet(user, dest_chan, spreadsheet_id)
        for field_json in json_obj["fields"]:
            new_spreadsheet.add_field(DailysFieldFactory.from_json(field_json, new_spreadsheet))
        return new_spreadsheet


class DailysField(metaclass=ABCMeta):
    # An abstract class representing an individual dailys field type.
    # A field can/will be multiple columns, maybe a varying quantity of them by configuration

    def __init__(self, spreadsheet, hallo_key_field_id):
        """
        :type spreadsheet: DailysSpreadsheet
        :type hallo_key_field_id: str
        """
        self.spreadsheet = spreadsheet
        """ :type : DailysSpreadsheet"""
        self.hallo_key_field_id = hallo_key_field_id
        """ :type : str"""

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
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj, spreadsheet):
        raise NotImplementedError()

    def save_data(self, data):
        """
        :type data: str | dict
        """
        data_str = data
        if isinstance(data, dict):
            data_str = json.dumps(data)
        self.spreadsheet.save_field(self, data_str)

    def load_data(self):
        """
        :rtype: str
        """
        self.spreadsheet.read_field(self)

    def message_channel(self, text):
        """
        :type text: str
        """
        self.spreadsheet.user.server.send(EventMessage(self.spreadsheet.destination.server,
                                                       self.spreadsheet.destination,
                                                       self.spreadsheet.user,
                                                       text,
                                                       inbound=False))



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
        :rtype: Event.EventMessage
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
        self.save_data(notif_str)
        # Send date to destination
        self.message_channel(notif_str)

    @staticmethod
    def create_from_input(event, spreadsheet):
        # Check user has an FA login
        user_parser = UserDataParser()
        fa_data = user_parser.get_data_by_user_and_type(spreadsheet.user, FAKeyData)  # type: FAKeyData
        if fa_data is None:
            raise DailysException("No FA data has been set up for the FA dailys field to use.")
        # Get column or find it.
        clean_input = event.command_args[len(DailysFAField.type_name):].strip()
        if len(clean_input) <= 3 and clean_input.isalpha():
            key = spreadsheet.tag_column(clean_input)
            return DailysFAField(spreadsheet, key)
        key = spreadsheet.find_and_tag_column_by_names(DailysFAField.col_names)
        if key is None:
            raise DailysException("Could not find a suitable column. "
                                  "Please ensure one and only one column is titled: {}."
                                  "Or specify a column reference."
                                  .format(", ".join(DailysFAField.col_names)))
        return DailysFAField(spreadsheet, key)

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["field_key"] = self.hallo_key_field_id
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysFAField(spreadsheet, json_obj["field_key"])


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
        # Get column or find it.
        clean_input = event.command_args[len(DailysSleepField.type_name):].strip()
        if len(clean_input) <= 3 and clean_input.isalpha():
            key = spreadsheet.tag_column(clean_input)
            return DailysSleepField(spreadsheet, key)
        key = spreadsheet.find_and_tag_column_by_names(DailysSleepField.col_names)
        if key is None:
            raise DailysException("Could not find a suitable column. "
                                  "Please ensure one and only one column is titled: {}."
                                  "Or specify a column reference."
                                  .format(", ".join(DailysSleepField.col_names)))
        return DailysSleepField(spreadsheet, key)

    @staticmethod
    def passive_events():
        return [EventMessage]

    def passive_trigger(self, evt):
        # TODO: check the day before, if need be
        input_clean = evt.text.strip().lower()
        time = datetime.now().isoformat()
        current_data = self.load_data()
        if current_data == "":
            current_data = {}
        else:
            current_data = json.loads(current_data)
        if input_clean in DailysSleepField.WAKE_WORDS:
            if self.json_key_wake_time in current_data:
                self.message_channel("Didn't you already wake up?")
                return
            else:
                current_data[self.json_key_wake_time] = time
                self.save_data(current_data)
                self.message_channel("Good morning!")
                return
        if input_clean in DailysSleepField.SLEEP_WORDS:
            if self.json_key_sleep_time in current_data:
                # Did they already wake? If not, they're updating their sleep time.
                if self.json_key_wake_time not in current_data:
                    current_data[self.json_key_sleep_time] = time
                    self.save_data(current_data)
                    self.message_channel("Good night again!")
                # Move the last wake time to interruptions
                interruption = dict()
                interruption[self.json_key_wake_time] = current_data[self.json_key_wake_time]
                interruption[self.json_key_sleep_time] = time
                if self.json_key_interruptions not in current_data:
                    current_data[self.json_key_interruptions] = []
                current_data[self.json_key_interruptions].append(interruption)
                self.save_data(current_data)
                self.message_channel("Oh, going back to sleep? Sleep well!")
                return
            else:
                current_data[self.json_key_sleep_time] = time
                self.save_data(current_data)
                self.message_channel("Goodnight!")
                return

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["field_key"] = self.hallo_key_field_id
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysFAField(spreadsheet, json_obj["field_key"])


class DailysMoodField(DailysField):
    # Does mood measurements
    TIME_WAKE = "WakeUpTime"  # Used as a time entry, to signify that it should take a mood measurement in the morning, after wakeup has been logged
    TIME_SLEEP = "SleepTime"  # Used as a time entry to signify that a mood measurement should be taken before sleep

    def get_times(self):
        # Return a list of times of day to take mood measurements
        pass

    def get_dimensions(self):
        # Return a list of mood dimensions? F, H, I, S, T, M
        pass


class DailysAnimalsField(DailysField):
    # Does animal sightings measurements

    def get_animal_list(self):
        # Return a list of animals which are being logged
        pass


class DailysDuolingoField(DailysField):
    type_name = "duolingo"
    col_names = ["duolingo", "duolingo friends", "duolingo friends list"]

    def __init__(self, spreadsheet, hallo_key_field_id, username):
        super().__init__(spreadsheet, hallo_key_field_id)
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
        :rtype: Event.EventMessage
        """
        duo = Commons.load_url_json("https://www.duolingo.com/users/{}".format(self.username))
        result = dict()
        for lang in duo["language_data"]:
            for friend in duo["language_data"][lang]["points_ranking_data"]:
                result[friend["username"]] = friend["points_data"]["total"]
        result_str = json.dumps(result)
        self.save_data(result_str)
        # Send date to destination
        self.message_channel(result_str)

    @staticmethod
    def _check_duo_username(username):
        try:
            Commons.load_url_json("https://www.duolingo.com/users/{}".format(username))
            return True
        except ValueError:
            return False

    @staticmethod
    def _check_spreadsheet_col_name(col_name):
        return len(col_name) <= 3 and col_name.isalpha()

    @staticmethod
    def create_from_input(event, spreadsheet):
        clean_input = event.command_args[len(DailysDuolingoField.type_name):].strip().split()
        if len(clean_input) > 2 or len(clean_input) == 0:
            raise DailysException("Cannot understand input. Please provide your Duolingo username, "
                                  "and optionally, a column reference for this data in the spreadsheet.")
        if len(clean_input) == 1:
            if DailysDuolingoField._check_duo_username(clean_input[0]):
                key = spreadsheet.find_and_tag_column_by_names(DailysDuolingoField.col_names)
                if key is None:
                    raise DailysException("Could not find a suitable column. "
                                          "Please ensure one and only one column is titled: {}."
                                          "Or specify a column reference."
                                          .format(", ".join(DailysDuolingoField.col_names)))
                return DailysDuolingoField(spreadsheet, key, clean_input[0])
            else:
                raise DailysException("Could not find a duolingo account with that username.")
        # length of input is 2.
        if DailysDuolingoField._check_spreadsheet_col_name(clean_input[0]):
            if DailysDuolingoField._check_duo_username(clean_input[1]):
                key = spreadsheet.tag_column(clean_input[0])
                return DailysDuolingoField(spreadsheet, key, clean_input[1])
        if DailysDuolingoField._check_duo_username(clean_input[0]):
            if DailysDuolingoField._check_spreadsheet_col_name(clean_input[1]):
                key = spreadsheet.tag_column(clean_input[1])
                return DailysDuolingoField(spreadsheet, key, clean_input[0])
        raise DailysException("Could not understand your input. Please provide a duolingo username, and optionally, "
                              "a column reference for this data in the spreadsheet.")

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["field_key"] = self.hallo_key_field_id
        json_obj["username"] = self.username
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysDuolingoField(spreadsheet, json_obj["field_key"], json_obj["username"])


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
    fields = [DailysFAField, DailysDuolingoField]

    @staticmethod
    def from_json(json_obj, spreadsheet):
        type_name = json_obj["type_name"]
        for field in DailysFieldFactory.fields:
            if field.type_name == type_name:
                return field.from_json(json_obj, spreadsheet)
        raise DailysException("Could not load dailys field of type {}".format(type_name))
