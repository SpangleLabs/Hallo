import json
import os
from datetime import timedelta

import pytest

from hallo.events import EventMessage, EventDay
from hallo.modules.dailys.dailys_field import DailysException
from hallo.modules.dailys.field_duolingo import DailysDuolingoField
from hallo.test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock

TEST_USERNAME = "Deer-Spangle"
TEST_PASSWORD = os.getenv("test_duo_password")


@pytest.mark.external_integration
def test_day_rollover(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Setup field
    field = DailysDuolingoField(spreadsheet, TEST_USERNAME, TEST_PASSWORD)
    # Send a new day event
    evt = EventDay()
    field.passive_trigger(evt)
    assert (
            field.type_name not in spreadsheet.saved_data
            or evt.get_send_time().date() not in spreadsheet.saved_data[field.type_name]
    )
    notif_dict = spreadsheet.saved_data[field.type_name][
        evt.get_send_time().date() - timedelta(1)
        ]
    assert len(notif_dict) > 0, "No results appeared in dict."
    for key in notif_dict:
        assert isinstance(
            notif_dict[key], int
        ), "Value for {} is not an int.".format(key)
    # Check sent data
    assert len(test_hallo.test_server.send_data) == 1
    assert isinstance(test_hallo.test_server.send_data[0], EventMessage)
    assert test_hallo.test_server.send_data[0].text == json.dumps(notif_dict)
    assert test_hallo.test_server.send_data[0].channel == test_hallo.test_chan
    assert test_hallo.test_server.send_data[0].user == test_hallo.test_user


@pytest.mark.external_integration
def test_create_from_input_no_username(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "duolingo"
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
        DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert (
            False
        ), "Should have failed to create DailysDuolingoField due to missing username."
    except DailysException as e:
        assert (
                "you must specify both a duolingo username, and password"
                in str(e).lower()
        ), "Exception did not prompt to specify a username and password."


@pytest.mark.external_integration
def test_create_from_input_no_password(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "duolingo {}".format(TEST_USERNAME)
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
        DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert (
            False
        ), "Should have failed to create DailysDuolingoField due to missing password."
    except DailysException as e:
        assert (
                "you must specify both a duolingo username, and password"
                in str(e).lower()
        ), "Exception did not prompt to specify a username and password."


@pytest.mark.external_integration
def test_create_from_input_invalid_password(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "duolingo {} {}".format(TEST_USERNAME, "NoTAreaLPasSWorD")
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
        DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert (
            False
        ), "Should have failed to create DailysDuolingoField due to incorrect password."
    except DailysException as e:
        assert (
                "could not access a duolingo account with that username and password"
                in str(e).lower()
        ), "Exception didn't clarify that password and username do not work."


@pytest.mark.external_integration
def test_create_from_input_username_first(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "duolingo {} {}".format(TEST_USERNAME, TEST_PASSWORD)
    evt = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "{} {}".format(cmd_name, cmd_args),
    )
    evt.split_command_text(cmd_name, cmd_args)
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Create from input
    field = DailysDuolingoField.create_from_input(evt, spreadsheet)
    assert field.spreadsheet == spreadsheet
    assert field.username == TEST_USERNAME
    assert field.password == TEST_PASSWORD


@pytest.mark.external_integration
def test_create_from_input_password_first(hallo_getter):
    test_hallo = hallo_getter({"dailys"})
    # Setup
    cmd_name = "setup dailys field"
    cmd_args = "duolingo {} {}".format(TEST_PASSWORD, TEST_USERNAME)
    evt = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "{} {}".format(cmd_name, cmd_args),
    )
    evt.split_command_text(cmd_name, cmd_args)
    spreadsheet = DailysSpreadsheetMock(test_hallo.test_user, test_hallo.test_chan)
    # Create from input
    field = DailysDuolingoField.create_from_input(evt, spreadsheet)
    assert field.spreadsheet == spreadsheet
    assert field.username == TEST_USERNAME
    assert field.password == TEST_PASSWORD
