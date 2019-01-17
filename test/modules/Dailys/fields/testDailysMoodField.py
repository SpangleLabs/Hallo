import json
import unittest
from datetime import time

from Events import EventMessage
from modules.Dailys import DailysMoodField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class DailysMoodFieldTest(TestBase, unittest.TestCase):

    def test_create_from_input_no_args(self):
        # Setup stuff
        command_name = "setup dailys field"
        command_args = "mood"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_chan, self.test_user)
        # Try and create dailys field
        try:
            DailysMoodField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysMoodField"
        except DailysException as e:
            assert "must contain" in str(e).lower()
            assert "times" in str(e).lower()
            assert "mood measurements" in str(e).lower()

    def test_create_from_input_no_semicolon(self):
        # Setup stuff
        command_name = "setup dailys field"
        command_times = "wake 12:00 sleep"
        command_moods = "happiness anger tiredness"
        command_args = "mood {} {}".format(command_times, command_moods)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_chan, self.test_user)
        # Try and create dailys field
        try:
            DailysMoodField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysMoodField"
        except DailysException as e:
            assert "must contain" in str(e).lower()
            assert "times" in str(e).lower()
            assert "semicolon" in str(e).lower()
            assert "mood measurements" in str(e).lower()

    def test_create_from_input_with_column_title(self):
        # Setup stuff
        command_name = "setup dailys field"
        command_times = "wake 12:00 sleep"
        command_moods = "happiness anger tiredness boisterousness"
        command_column = "AJ"
        command_args = "mood {};{};{}".format(command_times, command_moods, command_column)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Try and create dailys field
        field = DailysMoodField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert command_column in spreadsheet.tagged_columns
        assert isinstance(field.times, list)
        assert len(field.times) == 3
        assert DailysMoodField.TIME_WAKE in field.times
        assert DailysMoodField.TIME_SLEEP in field.times
        assert time(12, 0, 0) in field.times
        assert isinstance(field.moods, list)
        assert len(field.moods) == 4
        assert field.moods == command_moods.split()

    def test_create_from_input_column_not_found(self):
        col = "AJ"
        # Setup stuff
        command_name = "setup dailys field"
        command_times = "wake 12:00 sleep"
        command_moods = "happiness anger tiredness boisterousness"
        command_args = "mood {};{}".format(command_times, command_moods)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col: "nothing useful", "AG": "world"})
        # Try and create dailys field
        try:
            DailysMoodField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysMoodField"
        except DailysException as e:
            assert "could not find" in str(e).lower()

    def test_create_from_input_column_found(self):
        col = "AJ"
        # Setup stuff
        command_name = "setup dailys field"
        command_times = "wake 12:00 sleep"
        command_moods = "happiness anger tiredness boisterousness"
        command_args = "mood {};{}".format(command_times, command_moods)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            col_titles={"AE": "hello", col: "mood summary", "AG": "world"})
        # Try and create dailys field
        field = DailysMoodField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.hallo_key_field_id == spreadsheet.test_column_key
        assert col in spreadsheet.tagged_columns
        assert isinstance(field.times, list)
        assert len(field.times) == 3
        assert DailysMoodField.TIME_WAKE in field.times
        assert DailysMoodField.TIME_SLEEP in field.times
        assert time(12, 0, 0) in field.times
        assert isinstance(field.moods, list)
        assert len(field.moods) == 4
        assert field.moods == command_moods.split()

    def test_create_from_input_invalid_time(self):
        # Setup stuff
        command_name = "setup dailys field"
        command_times = "wake 12:99 sleep"
        command_moods = "happiness anger tiredness boisterousness"
        command_column = "AJ"
        command_args = "mood {};{};{}".format(command_times, command_moods, command_column)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Try and create dailys field
        try:
            DailysMoodField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysMoodField"
        except DailysException as e:
            assert "provide times as 24 hour" in str(e).lower()
            assert "hh:mm" in str(e).lower()

    def test_create_from_input_not_a_time(self):
        # Setup stuff
        command_name = "setup dailys field"
        command_times = "wake noon sleep"
        command_moods = "happiness anger tiredness boisterousness"
        command_column = "AJ"
        command_args = "mood {};{};{}".format(command_times, command_moods, command_column)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(command_name, command_args))
        evt.split_command_text(command_name, command_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Try and create dailys field
        try:
            DailysMoodField.create_from_input(evt, spreadsheet)
            assert False, "Should have failed to create DailysMoodField"
        except DailysException as e:
            assert "provide times as 24 hour" in str(e).lower()
            assert "hh:mm" in str(e).lower()
            assert "i don't recognise that time" in str(e).lower()

    def test_trigger_morning_query(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")
        field.passive_trigger(evt_wake)
        # Check mood query is sent
        notif_str = spreadsheet.saved_data[evt_wake.get_send_time().date()]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_WAKE]
        # Check query is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "how are you feeling" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_WAKE in data_wake[0].text
        assert all([mood in data_wake[0].text for mood in moods])

    def test_trigger_sleep_query(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "night")
        field.passive_trigger(evt_sleep)
        # Check mood query is sent
        notif_str = spreadsheet.saved_data[evt_sleep.get_send_time().date()]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        # Check query is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "how are you feeling" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_wake[0].text
        assert all([mood in data_wake[0].text for mood in moods])

    def test_trigger_morning_no_query_if_not_in_times(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")
        field.passive_trigger(evt_wake)
        # Check mood query is not sent or added to saved data
        assert evt_wake.get_send_time().date() not in spreadsheet.saved_data
        self.server.get_send_data(0)

    def test_trigger_sleep_no_query_if_not_in_times(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "night")
        field.passive_trigger(evt_sleep)
        # Check mood query is not sent or added to saved data
        assert evt_sleep.get_send_time().date() not in spreadsheet.saved_data
        self.server.get_send_data(0)

    def test_trigger_sleep_no_query_if_already_given(self):
        pass

    def test_trigger_sleep_after_midnight(self):
        pass

    def test_trigger_time_exactly_once(self):
        pass

    def test_process_reply_to_query(self):
        pass

    def test_process_most_recent_query(self):
        pass

    def test_process_most_recent_sleep_query_after_midnight(self):
        pass

    def test_process_no_mood_query(self):
        pass

    def test_process_time_specified(self):
        pass

    def test_process_wake_specified(self):
        pass
