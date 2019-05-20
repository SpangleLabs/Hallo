import json
import unittest
from datetime import datetime, timedelta, date

import dateutil

from Events import EventMessage, RawDataTelegram
from modules.Dailys import DailysSleepField, DailysException
from test.TestBase import TestBase
from test.modules.Dailys.DailysSpreadsheetMock import DailysSpreadsheetMock


class Obj:
    pass


class DailysSleepFieldTest(TestBase, unittest.TestCase):

    def get_telegram_time(self, date_time_val):
        fake_telegram_obj = Obj()
        fake_telegram_obj.message = Obj()
        fake_telegram_obj.message.date = date_time_val
        return fake_telegram_obj

    def test_create_from_input_col_specified(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "sleep"
        evt = EventMessage(self.server, self.test_chan, self.test_user, "{} {}".format(cmd_name, cmd_args))
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysSleepField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet

    def test_telegram_time(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        date = datetime(2018, 12, 23, 23, 44, 13)
        today = date.date()
        yesterday = today - timedelta(1)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date)))
        field.passive_trigger(evt)
        # Check data is saved
        notif_str = spreadsheet.saved_data[yesterday if date.hour <= 16 else today]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date.isoformat()

    def test_now_time(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        evt = EventMessage(self.server, self.test_chan, self.test_user, "sleep")
        now = datetime.now()
        today_date = now.date()
        yesterday_date = today_date - timedelta(1)
        field.passive_trigger(evt)
        # Check data is saved
        notif_str = spreadsheet.saved_data[yesterday_date if now.hour <= 16 else today_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        logged_time = dateutil.parser.parse(notif_dict["sleep_time"])
        assert logged_time-now < timedelta(0, 10)

    def test_sleep_before_5(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        sleep_time = datetime(2018, 12, 23, 12, 44, 13)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(sleep_time)))
        field.passive_trigger(evt)
        # Check data is saved to yesterday
        notif_str = spreadsheet.saved_data[sleep_time.date()-timedelta(1)]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == sleep_time.isoformat()

    def test_sleep_after_5(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
        # Send sleep message with telegram time
        sleep_time = datetime(2018, 12, 23, 23, 44, 13)
        evt = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(sleep_time)))
        field.passive_trigger(evt)
        # Check data is saved to today
        notif_str = spreadsheet.saved_data[sleep_time.date()]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == sleep_time.isoformat()

    def test_sleep_wake(self):
        sleep_date = date(2018, 12, 23)
        sleeps = list()
        # before midnight
        sleeps.append({"title": "before midnight",
                       "sleep": datetime(2018, 12, 23, 22, 44, 13),
                       "wake": datetime(2018, 12, 23, 23, 47, 34)})
        # over midnight
        sleeps.append({"title": "over midnight",
                       "sleep": datetime(2018, 12, 23, 22, 44, 13),
                       "wake": datetime(2018, 12, 24, 11, 47, 34)})
        # after midnight
        sleeps.append({"title": "after midnight",
                       "sleep": datetime(2018, 12, 24, 1, 44, 13),
                       "wake": datetime(2018, 12, 24, 11, 47, 34)})
        for sleep in sleeps:
            with self.subTest(sleep["title"]):
                spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
                # Setup field
                field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)
                # Send sleep message with telegram time
                date_sleep = sleep["sleep"]
                evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
                    .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep)))
                field.passive_trigger(evt_sleep)
                # Check sleep time is logged
                notif_str = spreadsheet.saved_data[sleep_date]
                notif_dict = json.loads(notif_str)
                assert "sleep_time" in notif_dict
                assert notif_dict["sleep_time"] == date_sleep.isoformat()
                # Check response is given
                data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
                assert "goodnight" in data_sleep[0].text.lower()
                # Send wake message with telegram time
                date_wake = sleep["wake"]
                evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
                    .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake)))
                field.passive_trigger(evt_wake)
                # Check wake time is logged
                notif_str = spreadsheet.saved_data[sleep_date]
                notif_dict = json.loads(notif_str)
                assert "sleep_time" in notif_dict
                assert "wake_time" in notif_dict
                assert notif_dict["sleep_time"] == date_sleep.isoformat()
                assert notif_dict["wake_time"] == date_wake.isoformat()
                # Check response is given
                data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
                assert "good morning" in data_wake[0].text.lower()

    def test_sleep_wake_sleep_wake(self):
        sleep_date = date(2018, 12, 23)
        sleeps = list()
        sleeps.append({"title": "all before midnight",
                       "sleep": datetime(2018, 12, 23, 22, 44, 13),
                       "interrupt_start": datetime(2018, 12, 23, 23, 15, 14),
                       "interrupt_end": datetime(2018, 12, 23, 23, 16, 17),
                       "wake": datetime(2018, 12, 23, 23, 47, 34)})
        sleeps.append({"title": "interrupt before midnight",
                       "sleep": datetime(2018, 12, 23, 22, 44, 13),
                       "interrupt_start": datetime(2018, 12, 23, 23, 15, 14),
                       "interrupt_end": datetime(2018, 12, 23, 23, 16, 17),
                       "wake": datetime(2018, 12, 24, 11, 47, 34)})
        sleeps.append({"title": "interrupt over midnight",
                       "sleep": datetime(2018, 12, 23, 22, 44, 13),
                       "interrupt_start": datetime(2018, 12, 23, 23, 55, 14),
                       "interrupt_end": datetime(2018, 12, 24, 0, 4, 17),
                       "wake": datetime(2018, 12, 24, 11, 47, 34)})
        sleeps.append({"title": "interrupt after midnight",
                       "sleep": datetime(2018, 12, 23, 22, 44, 13),
                       "interrupt_start": datetime(2018, 12, 24, 2, 15, 14),
                       "interrupt_end": datetime(2018, 12, 24, 2, 17, 17),
                       "wake": datetime(2018, 12, 24, 11, 47, 34)})
        sleeps.append({"title": "all after midnight",
                       "sleep": datetime(2018, 12, 24, 0, 44, 13),
                       "interrupt_start": datetime(2018, 12, 24, 2, 15, 14),
                       "interrupt_end": datetime(2018, 12, 24, 2, 16, 17),
                       "wake": datetime(2018, 12, 24, 11, 47, 34)})
        for sleep in sleeps:
            with self.subTest(sleep["title"]):
                spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
                # Setup field
                field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)

                # Send sleep message with telegram time
                date_sleep = sleep["sleep"]
                evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
                    .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep)))
                field.passive_trigger(evt_sleep)
                # Check sleep time is logged
                notif_str = spreadsheet.saved_data[sleep_date]
                notif_dict = json.loads(notif_str)
                assert "sleep_time" in notif_dict
                assert notif_dict["sleep_time"] == date_sleep.isoformat()
                # Check response is given
                data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
                assert "goodnight" in data_sleep[0].text.lower()

                # Send interrupt start message with telegram time
                date_interrupt_start = sleep["interrupt_start"]
                evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
                    .with_raw_data(RawDataTelegram(self.get_telegram_time(date_interrupt_start)))
                field.passive_trigger(evt_wake)
                # Check wake time is logged
                notif_str = spreadsheet.saved_data[sleep_date]
                notif_dict = json.loads(notif_str)
                assert "sleep_time" in notif_dict
                assert "wake_time" in notif_dict
                assert notif_dict["sleep_time"] == date_sleep.isoformat()
                assert notif_dict["wake_time"] == date_interrupt_start.isoformat()
                # Check response is given
                data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
                assert "good morning" in data_wake[0].text.lower()

                # Send interrupt end message with telegram time
                date_interrupt_end = sleep["interrupt_end"]
                evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
                    .with_raw_data(RawDataTelegram(self.get_telegram_time(date_interrupt_end)))
                field.passive_trigger(evt_wake)
                # Check wake time is logged
                notif_str = spreadsheet.saved_data[sleep_date]
                notif_dict = json.loads(notif_str)
                assert "sleep_time" in notif_dict
                assert "interruptions" in notif_dict
                assert "wake_time" not in notif_dict
                assert notif_dict["sleep_time"] == date_sleep.isoformat()
                assert isinstance(notif_dict["interruptions"], list)
                assert len(notif_dict["interruptions"]) == 1
                assert notif_dict["interruptions"][0]["wake_time"] == date_interrupt_start.isoformat()
                assert notif_dict["interruptions"][0]["sleep_time"] == date_interrupt_end.isoformat()
                # Check response is given
                data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
                assert "back to sleep" in data_wake[0].text.lower()

                # Send wake with telegram time
                date_wake = sleep["wake"]
                evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
                    .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake)))
                field.passive_trigger(evt_wake)
                # Check wake time is logged
                notif_str = spreadsheet.saved_data[sleep_date]
                notif_dict = json.loads(notif_str)
                assert "sleep_time" in notif_dict
                assert "interruptions" in notif_dict
                assert "wake_time" in notif_dict
                assert notif_dict["sleep_time"] == date_sleep.isoformat()
                assert isinstance(notif_dict["interruptions"], list)
                assert len(notif_dict["interruptions"]) == 1
                assert notif_dict["interruptions"][0]["wake_time"] == date_interrupt_start.isoformat()
                assert notif_dict["interruptions"][0]["sleep_time"] == date_interrupt_end.isoformat()
                assert notif_dict["wake_time"] == date_wake.isoformat()
                # Check response is given
                data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
                assert "good morning" in data_wake[0].text.lower()

    def test_two_interruptions(self):
        sleep_date = date(2018, 12, 23)
        sleep = {"sleep": datetime(2018, 12, 24, 0, 44, 13),
                 "interrupt1_start": datetime(2018, 12, 24, 2, 15, 14),
                 "interrupt1_end": datetime(2018, 12, 24, 2, 16, 17),
                 "interrupt2_start": datetime(2018, 12, 24, 4, 15, 14),
                 "interrupt2_end": datetime(2018, 12, 24, 4, 16, 17),
                 "wake": datetime(2018, 12, 24, 11, 47, 34)}

        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)

        # Send sleep message with telegram time
        date_sleep = sleep["sleep"]
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep)))
        field.passive_trigger(evt_sleep)
        # Check sleep time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "goodnight" in data_sleep[0].text.lower()

        # Send first interrupt start message with telegram time
        date_interrupt1_start = sleep["interrupt1_start"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_interrupt1_start)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert notif_dict["wake_time"] == date_interrupt1_start.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good morning" in data_wake[0].text.lower()

        # Send first interrupt end message with telegram time
        date_interrupt1_end = sleep["interrupt1_end"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_interrupt1_end)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "interruptions" in notif_dict
        assert "wake_time" not in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert isinstance(notif_dict["interruptions"], list)
        assert len(notif_dict["interruptions"]) == 1
        assert notif_dict["interruptions"][0]["wake_time"] == date_interrupt1_start.isoformat()
        assert notif_dict["interruptions"][0]["sleep_time"] == date_interrupt1_end.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "back to sleep" in data_wake[0].text.lower()

        # Send second interrupt start message with telegram time
        date_interrupt2_start = sleep["interrupt2_start"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_interrupt2_start)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "interruptions" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert len(notif_dict["interruptions"]) == 1
        assert notif_dict["interruptions"][0]["wake_time"] == date_interrupt1_start.isoformat()
        assert notif_dict["interruptions"][0]["sleep_time"] == date_interrupt1_end.isoformat()
        assert notif_dict["wake_time"] == date_interrupt2_start.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good morning" in data_wake[0].text.lower()

        # Send second interrupt end message with telegram time
        date_interrupt2_end = sleep["interrupt2_end"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_interrupt2_end)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "interruptions" in notif_dict
        assert "wake_time" not in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert isinstance(notif_dict["interruptions"], list)
        assert len(notif_dict["interruptions"]) == 2
        assert notif_dict["interruptions"][0]["wake_time"] == date_interrupt1_start.isoformat()
        assert notif_dict["interruptions"][0]["sleep_time"] == date_interrupt1_end.isoformat()
        assert notif_dict["interruptions"][1]["wake_time"] == date_interrupt2_start.isoformat()
        assert notif_dict["interruptions"][1]["sleep_time"] == date_interrupt2_end.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "back to sleep" in data_wake[0].text.lower()

        # Send wake with telegram time
        date_wake = sleep["wake"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "interruptions" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert isinstance(notif_dict["interruptions"], list)
        assert len(notif_dict["interruptions"]) == 2
        assert notif_dict["interruptions"][0]["wake_time"] == date_interrupt1_start.isoformat()
        assert notif_dict["interruptions"][0]["sleep_time"] == date_interrupt1_end.isoformat()
        assert notif_dict["interruptions"][1]["wake_time"] == date_interrupt2_start.isoformat()
        assert notif_dict["interruptions"][1]["sleep_time"] == date_interrupt2_end.isoformat()
        assert notif_dict["wake_time"] == date_wake.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good morning" in data_wake[0].text.lower()

    def test_sleep_sleep_wake(self):
        sleep_date = date(2018, 12, 23)
        # before midnight
        sleep = {"title": "before midnight",
                 "sleep1": datetime(2018, 12, 23, 22, 44, 13),
                 "sleep2": datetime(2018, 12, 23, 22, 56, 26),
                 "wake": datetime(2018, 12, 23, 23, 47, 34)}

        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)

        # Send sleep message with telegram time
        date_sleep1 = sleep["sleep1"]
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep1)))
        field.passive_trigger(evt_sleep)
        # Check sleep time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep1.isoformat()
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "goodnight" in data_sleep[0].text.lower()

        # Send second sleep message with telegram time
        date_sleep2 = sleep["sleep2"]
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep2)))
        field.passive_trigger(evt_sleep)
        # Check sleep time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep2.isoformat()
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good night again" in data_sleep[0].text.lower()

        # Send wake message with telegram time
        date_wake = sleep["wake"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep2.isoformat()
        assert notif_dict["wake_time"] == date_wake.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good morning" in data_wake[0].text.lower()

    def test_sleep_wake_wake(self):
        sleep_date = date(2018, 12, 23)
        # before midnight
        sleep = {"title": "before midnight",
                 "sleep": datetime(2018, 12, 23, 22, 44, 13),
                 "wake1": datetime(2018, 12, 23, 23, 35, 26),
                 "wake2": datetime(2018, 12, 23, 23, 47, 34)}

        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysSleepField(spreadsheet, spreadsheet.test_column_key)

        # Send sleep message with telegram time
        date_sleep = sleep["sleep"]
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "sleep")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_sleep)))
        field.passive_trigger(evt_sleep)
        # Check sleep time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "goodnight" in data_sleep[0].text.lower()

        # Send first wake message with telegram time
        date_wake1 = sleep["wake1"]
        evt_sleep = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake1)))
        field.passive_trigger(evt_sleep)
        # Check sleep time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert notif_dict["wake_time"] == date_wake1.isoformat()
        # Check response is given
        data_sleep = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "good morning" in data_sleep[0].text.lower()

        # Send wake message with telegram time
        date_wake2 = sleep["wake2"]
        evt_wake = EventMessage(self.server, self.test_chan, self.test_user, "morning")\
            .with_raw_data(RawDataTelegram(self.get_telegram_time(date_wake2)))
        field.passive_trigger(evt_wake)
        # Check wake time is logged
        notif_str = spreadsheet.saved_data[sleep_date]
        notif_dict = json.loads(notif_str)
        assert "sleep_time" in notif_dict
        assert "wake_time" in notif_dict
        assert notif_dict["sleep_time"] == date_sleep.isoformat()
        assert notif_dict["wake_time"] == date_wake1.isoformat()
        # Check response is given
        data_wake = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "didn't you already wake up?" in data_wake[0].text.lower()
