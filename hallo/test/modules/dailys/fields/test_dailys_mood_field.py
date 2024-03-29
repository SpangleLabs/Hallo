from datetime import time, date, datetime, timedelta

import pytest

import hallo.modules.dailys.dailys_field
from hallo.events import EventMessage, RawDataTelegram, EventMinute
from hallo.modules.dailys.field_mood import DailysMoodField, MoodTime
from hallo.test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock


class Obj:
    pass


def get_telegram_time(date_time_val):
    fake_telegram_obj = Obj()
    fake_telegram_obj.message = Obj()
    fake_telegram_obj.message.date = date_time_val
    fake_telegram_obj.message.reply_to_message = None
    return fake_telegram_obj


def get_telegram_time_reply(date_time_val, message_id):
    fake_telegram_obj = Obj()
    fake_telegram_obj.message = Obj()
    fake_telegram_obj.message.date = date_time_val
    fake_telegram_obj.message.reply_to_message = Obj()
    fake_telegram_obj.message.reply_to_message.message_id = message_id
    return fake_telegram_obj


def test_create_from_input(hallo_getter, requests_mock):
    dailys_times = ["WakeUpTime", "12:00:00", "SleepTime"]
    dailys_moods = ["happiness", "anger", "tiredness", "boisterousness"]
    # Setup stuff
    command_name = "setup dailys field"
    command_args = "mood"
    test_hallo = hallo_getter({"dailys"})
    evt = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "{} {}".format(command_name, command_args),
    )
    evt.split_command_text(command_name, command_args)
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    requests_mock.get(
        "{}/stats/mood/static/".format(spreadsheet.dailys_url),
        json=[
            {
                "date": "static",
                "source": "Mock test data",
                "stat_name": "mood",
                "data": {
                    "moods": dailys_moods,
                    "times": dailys_times
                }
            }
        ]
    )

    # Try and create dailys field
    field = DailysMoodField.create_from_input(evt, spreadsheet)

    assert field.spreadsheet == spreadsheet
    assert isinstance(field.times, list)
    assert len(field.times) == 3
    assert MoodTime(MoodTime.WAKE) in field.times
    assert MoodTime(MoodTime.SLEEP) in field.times
    assert MoodTime(time(12, 0, 0)) in field.times
    assert isinstance(field.moods, list)
    assert len(field.moods) == 4
    assert field.moods == dailys_moods


def test_create_from_input__no_static_data(hallo_getter, requests_mock):
    # Setup stuff
    command_name = "setup dailys field"
    command_args = "mood"
    test_hallo = hallo_getter({"dailys"})
    evt = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "{} {}".format(command_name, command_args),
    )
    evt.split_command_text(command_name, command_args)
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    requests_mock.get(
        "{}/stats/mood/static/".format(spreadsheet.dailys_url),
        json=[]
    )

    # Try and create dailys field
    with pytest.raises(hallo.modules.dailys.dailys_field.DailysException) as e:
        DailysMoodField.create_from_input(evt, spreadsheet)
    assert "mood field static data has not been set up on dailys system" in str(e.value).lower()


def test_trigger_morning_query(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_wake = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "morning")
    field.passive_trigger(evt_wake)
    # Check mood query is sent
    notif_dict = spreadsheet.saved_data["mood"][evt_wake.get_send_time().date()]
    assert MoodTime.WAKE in notif_dict
    assert "message_id" in notif_dict[MoodTime.WAKE]
    # Check query is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "how are you feeling" in data_wake[0].text.lower()
    assert MoodTime.WAKE in data_wake[0].text
    assert all([mood in data_wake[0].text for mood in moods])


def test_trigger_sleep_query(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    moods = ["Happiness", "Anger", "Tiredness"]
    evt_sleep = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "night")
    saved_data = dict()
    saved_data[MoodTime.WAKE] = dict()
    saved_data[MoodTime.WAKE]["message_id"] = 1232
    saved_data[str(time(14, 0, 0))] = dict()
    saved_data[str(time(14, 0, 0))]["message_id"] = 1234
    for mood in moods:
        saved_data[MoodTime.WAKE][mood] = 3
        saved_data[str(time(14, 0, 0))][mood] = 2
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user,
        test_hallo.test_chan,
        saved_data={"mood": {evt_sleep.get_send_time().date(): saved_data}},
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0)), MoodTime(MoodTime.SLEEP)]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    field.passive_trigger(evt_sleep)
    # Check mood query is sent
    notif_dict = spreadsheet.saved_data["mood"][evt_sleep.get_send_time().date()]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    # Check query is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "how are you feeling" in data_wake[0].text.lower()
    assert MoodTime.SLEEP in data_wake[0].text
    assert all([mood in data_wake[0].text for mood in moods])


def test_trigger_morning_no_query_if_not_in_times(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {}}
    )
    # Setup field
    times = [MoodTime(time(14, 0)), MoodTime(MoodTime.SLEEP)]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_wake = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "morning")
    field.passive_trigger(evt_wake)
    # Check mood query is not sent or added to saved data
    assert evt_wake.get_send_time().date() not in spreadsheet.saved_data["mood"]
    test_hallo.test_server.get_send_data(0)


def test_trigger_sleep_no_query_if_not_in_times(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0))]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_sleep = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "night")
    field.passive_trigger(evt_sleep)
    # Check mood query is not sent or added to saved data
    assert evt_sleep.get_send_time().date() not in spreadsheet.saved_data["mood"]
    test_hallo.test_server.get_send_data(0)


def test_trigger_sleep_no_query_if_already_given(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    moods = ["Happiness", "Anger", "Tiredness"]
    evt_sleep1 = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "night")
    saved_data = dict()
    saved_data[MoodTime.WAKE] = dict()
    saved_data[MoodTime.WAKE]["message_id"] = 1232
    saved_data[str(time(14, 0, 0))] = dict()
    saved_data[str(time(14, 0, 0))]["message_id"] = 1234
    for mood in moods:
        saved_data[MoodTime.WAKE][mood] = 3
        saved_data[str(time(14, 0, 0))][mood] = 2
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user,
        test_hallo.test_chan,
        saved_data={"mood": {evt_sleep1.get_send_time().date(): saved_data}},
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0)), MoodTime(MoodTime.SLEEP)]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_sleep1 = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "night")
    field.passive_trigger(evt_sleep1)
    # Check mood query is sent
    notif_dict = spreadsheet.saved_data["mood"][evt_sleep1.get_send_time().date()]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    # Check query is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "how are you feeling" in data_wake[0].text.lower()
    assert MoodTime.SLEEP in data_wake[0].text
    assert all([mood in data_wake[0].text for mood in moods])
    # Set message ID to something
    msg_id = "test_message_id"
    notif_dict[MoodTime.SLEEP]["message_id"] = msg_id
    spreadsheet.saved_data["mood"][evt_sleep1.get_send_time().date()] = notif_dict
    # Send second sleep query
    evt_sleep2 = EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "night")
    field.passive_trigger(evt_sleep2)
    # Check no mood query is sent
    notif_dict = spreadsheet.saved_data["mood"][evt_sleep1.get_send_time().date()]
    assert notif_dict[MoodTime.SLEEP]["message_id"] == msg_id
    test_hallo.test_server.get_send_data(0)


def test_trigger_sleep_after_midnight(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    mood_date = date(2019, 1, 15)
    sleep_time = datetime(2019, 1, 16, 0, 34, 15)
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0)), MoodTime(MoodTime.SLEEP)]
    moods = ["Happiness", "Anger", "Tiredness"]
    # Setup
    saved_data = dict()
    saved_data[MoodTime.WAKE] = dict()
    saved_data[MoodTime.WAKE]["message_id"] = 1232
    saved_data[str(time(14, 0, 0))] = dict()
    saved_data[str(time(14, 0, 0))]["message_id"] = 1234
    for mood in moods:
        saved_data[MoodTime.WAKE][mood] = 3
        saved_data[str(time(14, 0, 0))][mood] = 2
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: saved_data}}
    )
    # Setup field
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_sleep = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "night"
    ).with_raw_data(RawDataTelegram(get_telegram_time(sleep_time)))
    field.passive_trigger(evt_sleep)
    # Check mood query is sent for previous day
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    # Check query is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "how are you feeling" in data_wake[0].text.lower()
    assert MoodTime.SLEEP in data_wake[0].text
    assert all([mood in data_wake[0].text for mood in moods])


def test_trigger_time_exactly_once(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    mood_date = date(2019, 1, 18)
    # Setup
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0)), MoodTime(MoodTime.SLEEP)]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
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
    assert mood_date not in spreadsheet.saved_data["mood"]
    test_hallo.test_server.get_send_data(0)
    # Send time after trigger time
    field.passive_trigger(evt2)
    # Check mood query is sent
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert str(time(14, 0, 0)) in notif_dict
    assert "message_id" in notif_dict[str(time(14, 0, 0))]
    # Check query is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "how are you feeling" in data_wake[0].text.lower()
    assert str(time(14, 0, 0)) in data_wake[0].text
    assert all([mood in data_wake[0].text for mood in moods])
    # Set message ID to something
    msg_id = "test_message_id"
    notif_dict[str(time(14, 0, 0))]["message_id"] = msg_id
    spreadsheet.saved_data["mood"][mood_date] = notif_dict
    # Send another time after trigger time
    field.passive_trigger(evt3)
    # Check mood data not updated and query not sent
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert notif_dict[str(time(14, 0, 0))]["message_id"] == msg_id
    test_hallo.test_server.get_send_data(0)


def test_process_reply_to_query(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(8, 13, 6))
    msg_id = 41212
    mood_data = dict()
    mood_data[MoodTime.WAKE] = dict()
    mood_data[MoodTime.WAKE]["message_id"] = msg_id
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: mood_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "413"
    ).with_raw_data(
        RawDataTelegram(get_telegram_time_reply(mood_datetime, msg_id))
    )
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert "message_id" in notif_dict[MoodTime.WAKE]
    assert notif_dict[MoodTime.WAKE]["message_id"] == msg_id
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 4
    assert notif_dict[MoodTime.WAKE]["Anger"] == 1
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    # Check response is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_wake[0].text.lower()
    assert MoodTime.WAKE in data_wake[0].text
    assert mood_date.isoformat() in data_wake[0].text
    assert "413" in data_wake[0].text


def test_process_most_recent_query(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(8, 13, 6))
    msg_id = 41212
    mood_data = dict()
    mood_data[MoodTime.WAKE] = dict()
    mood_data[MoodTime.WAKE]["message_id"] = msg_id
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: mood_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert "message_id" in notif_dict[MoodTime.WAKE]
    assert notif_dict[MoodTime.WAKE]["message_id"] == msg_id
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 4
    assert notif_dict[MoodTime.WAKE]["Anger"] == 1
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    # Check response is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_wake[0].text.lower()
    assert MoodTime.WAKE in data_wake[0].text
    assert mood_date.isoformat() in data_wake[0].text
    assert "413" in data_wake[0].text


def test_process_most_recent_sleep_query_after_midnight(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    sleep_datetime = datetime.combine(mood_date, time(23, 55, 56))
    mood_datetime = datetime.combine(mood_date + timedelta(days=1), time(0, 3, 2))
    msg_id = 41212
    mood_data = dict()
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: mood_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.SLEEP)]
    moods = ["Happiness", "Anger", "Tiredness"]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send sleep message, check response
    evt_sleep = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "sleep"
    ).with_raw_data(RawDataTelegram(get_telegram_time(sleep_datetime)))
    field.passive_trigger(evt_sleep)
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    notif_dict[MoodTime.SLEEP]["message_id"] = msg_id
    spreadsheet.saved_data["mood"][mood_date] = notif_dict
    test_hallo.test_server.get_send_data()
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    assert notif_dict[MoodTime.SLEEP]["message_id"] == msg_id
    assert notif_dict[MoodTime.SLEEP]["Happiness"] == 4
    assert notif_dict[MoodTime.SLEEP]["Anger"] == 1
    assert notif_dict[MoodTime.SLEEP]["Tiredness"] == 3
    # Check response is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_wake[0].text.lower()
    assert MoodTime.SLEEP in data_wake[0].text
    assert mood_date.isoformat() in data_wake[0].text
    assert "413" in data_wake[0].text


def test_process_no_mood_query(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
    moods = ["Happiness", "Anger", "Tiredness"]
    msg_id = 41212
    mood_data = dict()
    mood_data[MoodTime.WAKE] = dict()
    mood_data[MoodTime.WAKE]["message_id"] = msg_id
    for mood in moods:
        mood_data[MoodTime.WAKE][mood] = 3
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: mood_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is not logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert notif_dict[MoodTime.WAKE]["message_id"] == msg_id
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 3
    assert notif_dict[MoodTime.WAKE]["Anger"] == 3
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    assert str(time(14, 0, 0)) not in notif_dict
    # Check error response is given
    data_err = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "is this a mood measurement, because i can't find a mood query" in data_err[0].text.lower()


def test_process_time_specified(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
    moods = ["Happiness", "Anger", "Tiredness"]
    msg_id = 41212
    mood_data = dict()
    mood_data[MoodTime.WAKE] = dict()
    mood_data[MoodTime.WAKE]["message_id"] = msg_id
    for mood in moods:
        mood_data[MoodTime.WAKE][mood] = 3
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: mood_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "HAT 1400 413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert notif_dict[MoodTime.WAKE]["message_id"] == msg_id
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 3
    assert notif_dict[MoodTime.WAKE]["Anger"] == 3
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    assert str(time(14, 0, 0)) in notif_dict
    assert "message_id" not in notif_dict[str(time(14, 0, 0))]
    assert notif_dict[str(time(14, 0, 0))]["Happiness"] == 4
    assert notif_dict[str(time(14, 0, 0))]["Anger"] == 1
    assert notif_dict[str(time(14, 0, 0))]["Tiredness"] == 3
    # Check response is given
    data_1400 = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_1400[0].text.lower()
    assert str(time(14, 0, 0)) in data_1400[0].text
    assert mood_date.isoformat() in data_1400[0].text
    assert "413" in data_1400[0].text


def test_process_wake_specified(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
    moods = ["Happiness", "Anger", "Tiredness"]
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "HAT wake 413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert "message_id" not in notif_dict[MoodTime.WAKE]
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 4
    assert notif_dict[MoodTime.WAKE]["Anger"] == 1
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    # Check response is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_wake[0].text.lower()
    assert MoodTime.WAKE in data_wake[0].text
    assert mood_date.isoformat() in data_wake[0].text
    assert "413" in data_wake[0].text


def test_process_sleep_specified(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
    moods = ["Happiness", "Anger", "Tiredness"]
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0)), MoodTime(MoodTime.SLEEP)]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "HAT sleep 413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" not in notif_dict[MoodTime.SLEEP]
    assert notif_dict[MoodTime.SLEEP]["Happiness"] == 4
    assert notif_dict[MoodTime.SLEEP]["Anger"] == 1
    assert notif_dict[MoodTime.SLEEP]["Tiredness"] == 3
    # Check response is given
    data_sleep = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_sleep[0].text.lower()
    assert MoodTime.SLEEP in data_sleep[0].text
    assert mood_date.isoformat() in data_sleep[0].text
    assert "413" in data_sleep[0].text


def test_no_trigger_after_processed(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
    moods = ["Happiness", "Anger", "Tiredness"]
    msg_id = 41212
    mood_data = dict()
    mood_data[MoodTime.WAKE] = dict()
    mood_data[MoodTime.WAKE]["message_id"] = msg_id
    for mood in moods:
        mood_data[MoodTime.WAKE][mood] = 3
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: mood_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "HAT 1400 413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert notif_dict[MoodTime.WAKE]["message_id"] == msg_id
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 3
    assert notif_dict[MoodTime.WAKE]["Anger"] == 3
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    assert str(time(14, 0, 0)) in notif_dict
    assert "message_id" not in notif_dict[str(time(14, 0, 0))]
    assert notif_dict[str(time(14, 0, 0))]["Happiness"] == 4
    assert notif_dict[str(time(14, 0, 0))]["Anger"] == 1
    assert notif_dict[str(time(14, 0, 0))]["Tiredness"] == 3
    # Check response is given
    data_1400 = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_1400[0].text.lower()
    assert str(time(14, 0, 0)) in data_1400[0].text
    assert mood_date.isoformat() in data_1400[0].text
    assert "413" in data_1400[0].text
    # Check that when the time happens, a query isn't sent
    evt_time = EventMinute()
    evt_time.send_time = datetime.combine(mood_date, time(14, 3, 10))
    field.passive_trigger(evt_time)
    # Check data isn't added
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert str(time(14, 0, 0)) in notif_dict
    assert "message_id" not in notif_dict[str(time(14, 0, 0))]
    assert notif_dict[str(time(14, 0, 0))]["Happiness"] == 4
    assert notif_dict[str(time(14, 0, 0))]["Anger"] == 1
    assert notif_dict[str(time(14, 0, 0))]["Tiredness"] == 3
    # Check query isn't sent
    test_hallo.test_server.get_send_data(0)


def test_no_trigger_wake_after_processed(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    mood_datetime = datetime.combine(mood_date, time(13, 13, 6))
    wake_datetime = datetime.combine(mood_date, time(13, 15, 7))
    moods = ["Happiness", "Anger", "Tiredness"]
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0))]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send message
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "HAT wake 413"
    ).with_raw_data(RawDataTelegram(get_telegram_time(mood_datetime)))
    field.passive_trigger(evt_mood)
    # Check mood response is logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert "message_id" not in notif_dict[MoodTime.WAKE]
    assert notif_dict[MoodTime.WAKE]["Happiness"] == 4
    assert notif_dict[MoodTime.WAKE]["Anger"] == 1
    assert notif_dict[MoodTime.WAKE]["Tiredness"] == 3
    # Check response is given
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_wake[0].text.lower()
    assert MoodTime.WAKE in data_wake[0].text
    assert mood_date.isoformat() in data_wake[0].text
    assert "413" in data_wake[0].text
    # Send wake message, ensure no response
    evt_wake = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "morning"
    ).with_raw_data(RawDataTelegram(get_telegram_time(wake_datetime)))
    field.passive_trigger(evt_wake)
    # Check query isn't logged
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.WAKE in notif_dict
    assert "message_id" not in notif_dict[MoodTime.WAKE]
    # Check response wasn't given
    test_hallo.test_server.get_send_data(0)


def test_no_trigger_sleep_after_processed_sleep_and_midnight(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    mood_date = date(2019, 1, 18)
    sleep_datetime = datetime.combine(mood_date, time(23, 13, 6))
    mood_datetime = datetime.combine(mood_date, time(23, 15, 7))
    sleep2_datetime = datetime.combine(
        mood_date + timedelta(days=1), time(0, 3, 15)
    )
    msg_id = 123123
    moods = ["Happiness", "Anger", "Tiredness"]
    saved_data = dict()
    saved_data[MoodTime.WAKE] = dict()
    saved_data[MoodTime.WAKE]["message_id"] = 1232
    saved_data[str(time(14, 0, 0))] = dict()
    saved_data[str(time(14, 0, 0))]["message_id"] = 1234
    for mood in moods:
        saved_data[MoodTime.WAKE][mood] = 3
        saved_data[str(time(14, 0, 0))][mood] = 2
    spreadsheet = DailysSpreadsheetMock(
        test_hallo.test_user, test_hallo.test_chan, saved_data={"mood": {mood_date: saved_data}}
    )
    # Setup field
    times = [MoodTime(MoodTime.WAKE), MoodTime(time(14, 0, 0)), MoodTime(MoodTime.SLEEP)]
    field = DailysMoodField(spreadsheet, times, moods)
    # Send sleep query
    evt_sleep1 = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "sleep"
    ).with_raw_data(RawDataTelegram(get_telegram_time(sleep_datetime)))
    field.passive_trigger(evt_sleep1)
    # Check mood query is given and stuff
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    notif_dict[MoodTime.SLEEP]["message_id"] = msg_id
    spreadsheet.saved_data["mood"][mood_date] = notif_dict
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "how are you feeling" in data_wake[0].text.lower()
    assert MoodTime.SLEEP in data_wake[0].text
    assert all([mood in data_wake[0].text for mood in moods])
    # Then mood response
    evt_mood = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "413"
    ).with_raw_data(
        RawDataTelegram(get_telegram_time_reply(mood_datetime, msg_id))
    )
    field.passive_trigger(evt_mood)
    # Check mood is recorded and response given
    notif_dict = spreadsheet.saved_data["mood"][mood_date]
    assert MoodTime.SLEEP in notif_dict
    assert "message_id" in notif_dict[MoodTime.SLEEP]
    assert notif_dict[MoodTime.SLEEP]["message_id"] == msg_id
    assert notif_dict[MoodTime.SLEEP]["Happiness"] == 4
    assert notif_dict[MoodTime.SLEEP]["Anger"] == 1
    assert notif_dict[MoodTime.SLEEP]["Tiredness"] == 3
    data_wake = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "added" in data_wake[0].text.lower()
    assert MoodTime.SLEEP in data_wake[0].text
    assert mood_date.isoformat() in data_wake[0].text
    assert "413" in data_wake[0].text
    # Then midnight
    # Another sleep query
    evt_sleep1 = EventMessage(
        test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "sleep"
    ).with_raw_data(RawDataTelegram(get_telegram_time(sleep2_datetime)))
    field.passive_trigger(evt_sleep1)
    # Check there's no response
    test_hallo.test_server.get_send_data(0)
