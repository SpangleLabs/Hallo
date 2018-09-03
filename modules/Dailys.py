

class DailysRegister(Function):
    # Register spreadsheet ID, sheet name
    # Might be able to automatically gather sheet name? (just get first)
    # Might be able to automatically gather initial data row and date (check top 10:10 for a date? or use frozen)
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#gridproperties
    # Title key row would be nice?
    pass


class DailysRepo():
    # Store data on all users dailys spreadsheets
    pass


class DailysSpreadsheet():
    # Store the data on an individual user's spreadsheet, has a list of enabled fields/topics?
    def get_fields_list(self):
        # Return a list of fields this spreadsheet has
        pass

    def list_all_columns(self):
        # List all the columns of all the fields which hallo manages in this spreadsheet
        pass

    def get_current_date(self):
        # Return the current date. Not equal to calendar date, as user may be awake after midnight
        pass


class DailysField(metaclass=ABCMeta):
    # An abstract class representing an individual dailys field type.
    # A field can/will be multiple columns, maybe a varying quantity of them by configuration

    def list_columns(self):
        # Return a full list of the columns this field occupies
        raise NotImplementedError()

    def new_day(self):
        # Called on all fields when DailysSpreadsheet confirms a new day, animals can save at that point, some might not react


class DailysSleepField(DailysField):
    # Does sleep and wake times, sleep notes, dream logs, shower?
    WAKE_WORDS = ["morning", "wake", "woke"]
    SLEEP_WORDS = ["goodnight", "sleep", "nini"]
    pass


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
    # Measures duolingo progress of user and specified friends.
    # Checks at midnight

    def get_friends(self):
        # Return a list of friends which should be tracked?
        pass


class DailysFAField(DailysField):
    # Go reference FA sub perhaps? Needs those cookies at least
    # Check at midnight
    pass


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
