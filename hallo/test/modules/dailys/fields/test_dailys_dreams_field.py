from hallo.events import EventMessage
from hallo.modules.dailys import DailysDreamField
from hallo.test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock


def test_ignore_other(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(test_user, test_chan)
    # Setup field
    field = DailysDreamField(spreadsheet)
    evt = EventMessage(
        test_server,
        test_chan,
        test_user,
        "some other message",
    )

    # Send a message event
    field.passive_trigger(evt)

    assert field.type_name not in spreadsheet.saved_data

    # Check sent data
    assert len(test_server.send_data) == 0


def test_record_dream(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(test_user, test_chan)
    # Setup field
    field = DailysDreamField(spreadsheet)
    evt = EventMessage(
        test_server,
        test_chan,
        test_user,
        "dream about some thing",
    )

    # Send a message event
    field.passive_trigger(evt)

    dream_dict = spreadsheet.saved_data[field.type_name][
        evt.get_send_time().date()
    ]
    assert "dreams" in dream_dict
    assert len(dream_dict["dreams"]) == 1
    dream = dream_dict["dreams"][0]
    assert "text" in dream
    assert dream["text"] == "dream about some thing"

    # Check sent data
    assert len(test_server.send_data) == 1
    assert isinstance(test_server.send_data[0], EventMessage)
    assert "Logged dream." in test_server.send_data[0].text
    assert "1st of the day" in test_server.send_data[0].text
    assert test_server.send_data[0].channel == test_chan
    assert test_server.send_data[0].user == test_user


def test_record_second_dream(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"dailys"})
    evt = EventMessage(
        test_server,
        test_chan,
        test_user,
        "Dream about some second thing",
    )
    previous_dream = {
        "text": "Dreamt the first time"
    }
    saved_data = {
        "dreams": {
            evt.get_send_time().date(): {"dreams": [previous_dream]}
        }
    }
    spreadsheet = DailysSpreadsheetMock(test_user, test_chan, saved_data=saved_data)
    # Setup field
    field = DailysDreamField(spreadsheet)

    # Send a message event
    field.passive_trigger(evt)

    # Check data is added
    dream_dict = spreadsheet.saved_data[field.type_name][
        evt.get_send_time().date()
    ]
    assert "dreams" in dream_dict
    assert len(dream_dict["dreams"]) == 2
    dream1 = dream_dict["dreams"][0]
    assert "text" in dream1
    assert dream1["text"] == "Dreamt the first time"
    dream2 = dream_dict["dreams"][1]
    assert "text" in dream2
    assert dream2["text"] == "Dream about some second thing"

    # Check sent data
    assert len(test_server.send_data) == 1
    assert isinstance(test_server.send_data[0], EventMessage)
    assert "Logged dream." in test_server.send_data[0].text
    assert "2nd of the day" in test_server.send_data[0].text
    assert test_server.send_data[0].channel == test_chan
    assert test_server.send_data[0].user == test_user


def test_create_from_input(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "dream"
    evt = EventMessage(
        test_server,
        test_chan,
        test_user,
        "{} {}".format(cmd_name, cmd_args),
    )
    evt.split_command_text(cmd_name, cmd_args)
    spreadsheet = DailysSpreadsheetMock(test_user, test_chan)

    # Create from input
    field = DailysDreamField.create_from_input(evt, spreadsheet)

    assert field.spreadsheet == spreadsheet
    assert field.type_name == "dreams"
