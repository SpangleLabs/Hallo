import json
import os
from datetime import timedelta

import pytest

import hallo.modules.dailys.dailys_field
from hallo.events import EventDay, EventMessage
from hallo.modules.dailys.field_fa import DailysFAField
from hallo.modules.user_data import UserDataParser, FAKeyData
from hallo.test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock


def test_day_rollover_no_data(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup field
    field = DailysFAField(spreadsheet)
    # Send a new day event
    try:
        field.passive_trigger(EventDay())
        assert False, "Should have failed to check FA data."
    except hallo.modules.dailys.dailys_field.DailysException as e:
        assert (
                "no fa data" in str(e).lower()
        ), "Exception should say there's no FA data."


@pytest.mark.external_integration
def test_day_rollover(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup FA key
    udp = UserDataParser()
    key = FAKeyData(os.getenv("test_cookie_a"), os.getenv("test_cookie_b"))
    udp.set_user_data(test_hallo.test_user, key)
    # Setup field
    field = DailysFAField(spreadsheet)
    # Send a new day event
    evt = EventDay()
    field.passive_trigger(evt)
    assert evt.get_send_time().date() not in spreadsheet.saved_data
    notif_dict = spreadsheet.saved_data["furaffinity"][
        evt.get_send_time().date() - timedelta(1)
    ]
    assert "submissions" in notif_dict
    assert "comments" in notif_dict
    assert "journals" in notif_dict
    assert "favourites" in notif_dict
    assert "watches" in notif_dict
    assert "notes" in notif_dict
    assert "watchers_count" in notif_dict
    assert "watching_count" in notif_dict
    assert len(test_hallo.test_server.send_data) == 1
    assert isinstance(test_hallo.test_server.send_data[0], EventMessage)
    assert test_hallo.test_server.send_data[0].text == json.dumps(notif_dict)
    assert test_hallo.test_server.send_data[0].channel == test_hallo.test_chan
    assert test_hallo.test_server.send_data[0].user == test_hallo.test_user


def test_create_from_input_no_fa_data(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "furaffinity"
    evt = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "{} {}".format(cmd_name, cmd_args),
    )
    evt.split_command_text(cmd_name, cmd_args)
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Create from input
    try:
        DailysFAField.create_from_input(evt, spreadsheet)
        assert (
            False
        ), "Should have failed to create DailysFAField due to missing FA login info."
    except hallo.modules.dailys.dailys_field.DailysException as e:
        assert (
            "no fa data" in str(e).lower()
        ), "Exception did not mention that there was no FA data set up."


def test_create_from_input(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "furaffinity"
    evt = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "{} {}".format(cmd_name, cmd_args),
    )
    evt.split_command_text(cmd_name, cmd_args)
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup an FA key, doesn't matter if it works
    udp = UserDataParser()
    key = FAKeyData("cookie_a", "cookie_b")
    udp.set_user_data(test_hallo.test_user, key)
    # Create from input
    field = DailysFAField.create_from_input(evt, spreadsheet)
    assert field.spreadsheet == spreadsheet
