import json
import unittest
from datetime import time, date, datetime, timedelta

from Events import EventMessage, RawDataTelegram, EventMinute
from modules.Dailys import DailysMoodField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class Obj:
    pass


class DailysMoodFieldTest(TestBase, unittest.TestCase):

    def get_telegram_time(self, date_time_val):
        fake_telegram_obj = Obj()
        fake_telegram_obj.message = Obj()
        fake_telegram_obj.message.date = date_time_val
        fake_telegram_obj.message.reply_to_message = None
        return fake_telegram_obj

    def get_telegram_time_reply(self, date_time_val, message_id):
        fake_telegram_obj = Obj()
        fake_telegram_obj.message = Obj()
        fake_telegram_obj.message.date = date_time_val
        fake_telegram_obj.message.reply_to_message = Obj()
        fake_telegram_obj.message.reply_to_message.message_id = message_id
        return fake_telegram_obj

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
        moods = ["Happiness", "Anger", "Tiredness"]
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "night")
        saved_data = dict()
        saved_data[DailysMoodField.TIME_WAKE] = dict()
        saved_data[DailysMoodField.TIME_WAKE]["message_id"] = 1232
        saved_data[str(time(14, 0, 0))] = dict()
        saved_data[str(time(14, 0, 0))]["message_id"] = 1234
        for mood in moods:
            saved_data[DailysMoodField.TIME_WAKE][mood] = 3
            saved_data[str(time(14, 0, 0))][mood] = 2
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={evt_sleep.get_send_time().date(): json.dumps(saved_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
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
        # Setup
        moods = ["Happiness", "Anger", "Tiredness"]
        evt_sleep1 = EventMessage(self.server, self.test_chan, self.test_user, "night")
        saved_data = dict()
        saved_data[DailysMoodField.TIME_WAKE] = dict()
        saved_data[DailysMoodField.TIME_WAKE]["message_id"] = 1232
        saved_data[str(time(14, 0, 0))] = dict()
        saved_data[str(time(14, 0, 0))]["message_id"] = 1234
        for mood in moods:
            saved_data[DailysMoodField.TIME_WAKE][mood] = 3
            saved_data[str(time(14, 0, 0))][mood] = 2
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={evt_sleep1.get_send_time().date(): json.dumps(saved_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_sleep1 = EventMessage(self.server, self.test_chan, self.test_user, "night")
        field.passive_trigger(evt_sleep1)
        # Check mood query is sent
        notif_str = spreadsheet.saved_data[evt_sleep1.get_send_time().date()]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        # Check query is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "how are you feeling" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_wake[0].text
        assert all([mood in data_wake[0].text for mood in moods])
        # Set message ID to something
        msg_id = "test_message_id"
        notif_dict[DailysMoodField.TIME_SLEEP]["message_id"] = msg_id
        spreadsheet.saved_data[evt_sleep1.get_send_time().date()] = json.dumps(notif_dict)
        # Send second sleep query
        evt_sleep2 = EventMessage(self.server, self.test_chan, self.test_user, "night")
        field.passive_trigger(evt_sleep2)
        # Check no mood query is sent
        notif_str = spreadsheet.saved_data[evt_sleep1.get_send_time().date()]
        notif_dict = json.loads(notif_str)
        assert notif_dict[DailysMoodField.TIME_SLEEP]["message_id"] == msg_id
        self.server.get_send_data(0)

    def test_trigger_sleep_after_midnight(self):
        mood_date = date(2019, 1, 15)
        sleep_time = datetime(2019, 1, 16, 0, 34, 15)
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        moods = ["Happiness", "Anger", "Tiredness"]
        # Setup
        saved_data = dict()
        saved_data[DailysMoodField.TIME_WAKE] = dict()
        saved_data[DailysMoodField.TIME_WAKE]["message_id"] = 1232
        saved_data[str(time(14, 0, 0))] = dict()
        saved_data[str(time(14, 0, 0))]["message_id"] = 1234
        for mood in moods:
            saved_data[DailysMoodField.TIME_WAKE][mood] = 3
            saved_data[str(time(14, 0, 0))][mood] = 2
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(saved_data)})
        # Setup field
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "night")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(sleep_time)))
        field.passive_trigger(evt_sleep)
        # Check mood query is sent for previous day
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        # Check query is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "how are you feeling" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_wake[0].text
        assert all([mood in data_wake[0].text for mood in moods])

    def test_trigger_time_exactly_once(self):
        mood_date = date(2019, 1, 18)
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Prepare events
        evt1 = EventMinute()
        evt1.send_time = datetime(2019, 1, 18, 13, 59, 11)
        evt2 = EventMinute()
        evt2.send_time = datetime(2019, 1, 18, 14, 0, 11)
        evt3 = EventMinute()
        evt3.send_time = datetime(2019, 1, 18, 14, 1, 11)
        # Send time before trigger time
        field.passive_trigger(evt1)
        # Check mood data not updated and query not sent
        assert mood_date not in spreadsheet.saved_data
        self.server.get_send_data(0)
        # Send time after trigger time
        field.passive_trigger(evt2)
        # Check mood query is sent
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert str(time(14, 0, 0)) in notif_dict
        assert "message_id" in notif_dict[str(time(14, 0, 0))]
        # Check query is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "how are you feeling" in data_wake[0].text.lower()
        assert str(time(14, 0, 0)) in data_wake[0].text
        assert all([mood in data_wake[0].text for mood in moods])
        # Set message ID to something
        msg_id = "test_message_id"
        notif_dict[str(time(14, 0, 0))]["message_id"] = msg_id
        spreadsheet.saved_data[mood_date] = json.dumps(notif_dict)
        # Send another time after trigger time
        field.passive_trigger(evt3)
        # Check mood data not updated and query not sent
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert notif_dict[str(time(14, 0, 0))]["message_id"] == msg_id
        self.server.get_send_data(0)

    def test_process_reply_to_query(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(8, 13, 6))
        msg_id = 41212
        mood_data = dict()
        mood_data[DailysMoodField.TIME_WAKE] = dict()
        mood_data[DailysMoodField.TIME_WAKE]["message_id"] = msg_id
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(mood_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time_reply(mood_datetime, msg_id)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_WAKE]
        assert notif_dict[DailysMoodField.TIME_WAKE]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_WAKE in data_wake[0].text
        assert "413" in data_wake[0].text

    def test_process_most_recent_query(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(8, 13, 6))
        msg_id = 41212
        mood_data = dict()
        mood_data[DailysMoodField.TIME_WAKE] = dict()
        mood_data[DailysMoodField.TIME_WAKE]["message_id"] = msg_id
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(mood_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_WAKE]
        assert notif_dict[DailysMoodField.TIME_WAKE]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_WAKE in data_wake[0].text
        assert "413" in data_wake[0].text

    def test_process_most_recent_sleep_query_after_midnight(self):
        # Setup
        mood_date = date(2019, 1, 18)
        sleep_datetime = datetime.combine(mood_date, time(23, 55, 56))
        mood_datetime = datetime.combine(mood_date + timedelta(days=1), time(0, 3, 2))
        msg_id = 41212
        mood_data = dict()
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(mood_data)})
        # Setup field
        times = [DailysMoodField.TIME_SLEEP]
        moods = ["Happiness", "Anger", "Tiredness"]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send sleep message, check response
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(sleep_datetime)))
        field.passive_trigger(evt_sleep)
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        notif_dict[DailysMoodField.TIME_SLEEP]["message_id"] = msg_id
        spreadsheet.saved_data[mood_date] = json.dumps(notif_dict)
        self.server.get_send_data()
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        assert notif_dict[DailysMoodField.TIME_SLEEP]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Tiredness"] == 3
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_wake[0].text
        assert "413" in data_wake[0].text

    def test_process_no_mood_query(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
        moods = ["Happiness", "Anger", "Tiredness"]
        msg_id = 41212
        mood_data = dict()
        mood_data[DailysMoodField.TIME_WAKE] = dict()
        mood_data[DailysMoodField.TIME_WAKE]["message_id"] = msg_id
        for mood in moods:
            mood_data[DailysMoodField.TIME_WAKE][mood] = 3
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(mood_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is not logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert notif_dict[DailysMoodField.TIME_WAKE]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 3
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 3
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        assert str(time(14, 0, 0)) not in notif_dict
        # Check no response is given
        self.server.get_send_data(0)

    def test_process_time_specified(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
        moods = ["Happiness", "Anger", "Tiredness"]
        msg_id = 41212
        mood_data = dict()
        mood_data[DailysMoodField.TIME_WAKE] = dict()
        mood_data[DailysMoodField.TIME_WAKE]["message_id"] = msg_id
        for mood in moods:
            mood_data[DailysMoodField.TIME_WAKE][mood] = 3
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(mood_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "HAT 1400 413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert notif_dict[DailysMoodField.TIME_WAKE]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 3
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 3
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        assert str(time(14, 0, 0)) in notif_dict
        assert "message_id" not in notif_dict[str(time(14, 0, 0))]
        assert notif_dict[str(time(14, 0, 0))]["Happiness"] == 4
        assert notif_dict[str(time(14, 0, 0))]["Anger"] == 1
        assert notif_dict[str(time(14, 0, 0))]["Tiredness"] == 3
        # Check response is given
        data_1400 = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_1400[0].text.lower()
        assert str(time(14, 0, 0)) in data_1400[0].text
        assert "413" in data_1400[0].text

    def test_process_wake_specified(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
        moods = ["Happiness", "Anger", "Tiredness"]
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "HAT wake 413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert "message_id" not in notif_dict[DailysMoodField.TIME_WAKE]
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_WAKE in data_wake[0].text
        assert "413" in data_wake[0].text

    def test_process_sleep_specified(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
        moods = ["Happiness", "Anger", "Tiredness"]
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "HAT sleep 413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" not in notif_dict[DailysMoodField.TIME_SLEEP]
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Tiredness"] == 3
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_sleep[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_sleep[0].text
        assert "413" in data_sleep[0].text

    def test_no_trigger_after_processed(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
        moods = ["Happiness", "Anger", "Tiredness"]
        msg_id = 41212
        mood_data = dict()
        mood_data[DailysMoodField.TIME_WAKE] = dict()
        mood_data[DailysMoodField.TIME_WAKE]["message_id"] = msg_id
        for mood in moods:
            mood_data[DailysMoodField.TIME_WAKE][mood] = 3
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(mood_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "HAT 1400 413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert notif_dict[DailysMoodField.TIME_WAKE]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 3
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 3
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        assert str(time(14, 0, 0)) in notif_dict
        assert "message_id" not in notif_dict[str(time(14, 0, 0))]
        assert notif_dict[str(time(14, 0, 0))]["Happiness"] == 4
        assert notif_dict[str(time(14, 0, 0))]["Anger"] == 1
        assert notif_dict[str(time(14, 0, 0))]["Tiredness"] == 3
        # Check response is given
        data_1400 = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_1400[0].text.lower()
        assert str(time(14, 0, 0)) in data_1400[0].text
        assert "413" in data_1400[0].text
        # Check that when the time happens, a query isn't sent
        evt_time = EventMinute()
        evt_time.send_time = datetime.combine(mood_date, time(14, 3, 10))
        field.passive_trigger(evt_time)
        # Check data isn't added
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert str(time(14, 0, 0)) in notif_dict
        assert "message_id" not in notif_dict[str(time(14, 0, 0))]
        assert notif_dict[str(time(14, 0, 0))]["Happiness"] == 4
        assert notif_dict[str(time(14, 0, 0))]["Anger"] == 1
        assert notif_dict[str(time(14, 0, 0))]["Tiredness"] == 3
        # Check query isn't sent
        self.server.get_send_data(0)

    def test_no_trigger_wake_after_processed(self):
        # Setup
        mood_date = date(2019, 1, 18)
        mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
        wake_datetime = datetime.combine(mood_date, time(13, 15, 7))
        moods = ["Happiness", "Anger", "Tiredness"]
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0)]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send message
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "HAT wake 413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(mood_datetime)))
        field.passive_trigger(evt_mood)
        # Check mood response is logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert "message_id" not in notif_dict[DailysMoodField.TIME_WAKE]
        assert notif_dict[DailysMoodField.TIME_WAKE]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_WAKE]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_WAKE]["Tiredness"] == 3
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_WAKE in data_wake[0].text
        assert "413" in data_wake[0].text
        # Send wake message, ensure no response
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(wake_datetime)))
        field.passive_trigger(evt_wake)
        # Check query isn't logged
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_WAKE in notif_dict
        assert "message_id" not in notif_dict[DailysMoodField.TIME_WAKE]
        # Check response wasn't given
        self.server.get_send_data(0)

    def test_no_trigger_sleep_after_processed_sleep_and_midnight(self):
        # Setup
        mood_date = date(2019, 1, 18)
        sleep_datetime = datetime.combine(mood_date, time(23, 13, 6))
        mood_datetime = datetime.combine(mood_date, time(23, 15, 7))
        sleep2_datetime = datetime.combine(mood_date + timedelta(days=1), time(0, 3, 15))
        msg_id = 123123
        moods = ["Happiness", "Anger", "Tiredness"]
        saved_data = dict()
        saved_data[DailysMoodField.TIME_WAKE] = dict()
        saved_data[DailysMoodField.TIME_WAKE]["message_id"] = 1232
        saved_data[str(time(14, 0, 0))] = dict()
        saved_data[str(time(14, 0, 0))]["message_id"] = 1234
        for mood in moods:
            saved_data[DailysMoodField.TIME_WAKE][mood] = 3
            saved_data[str(time(14, 0, 0))][mood] = 2
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan,
                                            saved_data={mood_date: json.dumps(saved_data)})
        # Setup field
        times = [DailysMoodField.TIME_WAKE, time(14, 0, 0), DailysMoodField.TIME_SLEEP]
        field = DailysMoodField(spreadsheet, spreadsheet.test_column_key, times, moods)
        # Send sleep query
        evt_sleep1 = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(sleep_datetime)))
        field.passive_trigger(evt_sleep1)
        # Check mood query is given and stuff
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        notif_dict[DailysMoodField.TIME_SLEEP]["message_id"] = msg_id
        spreadsheet.saved_data[mood_date] = json.dumps(notif_dict)
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "how are you feeling" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_wake[0].text
        assert all([mood in data_wake[0].text for mood in moods])
        # Then mood response
        evt_mood = EventMessage(self.server, self.test_chan, self.test_user, "413")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time_reply(mood_datetime, msg_id)))
        field.passive_trigger(evt_mood)
        # Check mood is recorded and response given
        notif_str = spreadsheet.saved_data[mood_date]
        notif_dict = json.loads(notif_str)
        assert DailysMoodField.TIME_SLEEP in notif_dict
        assert "message_id" in notif_dict[DailysMoodField.TIME_SLEEP]
        assert notif_dict[DailysMoodField.TIME_SLEEP]["message_id"] == msg_id
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Happiness"] == 4
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Anger"] == 1
        assert notif_dict[DailysMoodField.TIME_SLEEP]["Tiredness"] == 3
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added" in data_wake[0].text.lower()
        assert DailysMoodField.TIME_SLEEP in data_wake[0].text
        assert "413" in data_wake[0].text
        # Then midnight
        # Another sleep query
        evt_sleep1 = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(sleep2_datetime)))
        field.passive_trigger(evt_sleep1)
        # Check there's no response
        self.server.get_send_data(0)
