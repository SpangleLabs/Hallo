import json
import os
import unittest
from datetime import timedelta

import pytest

from hallo.events import EventMessage, EventDay
from hallo.modules.dailys.dailys_field import DailysException
from hallo.modules.dailys.field_duolingo import DailysDuolingoField
from hallo.test.test_base import TestBase
from hallo.test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock


@pytest.mark.external_integration
class DailysDuolingoFieldTest(TestBase, unittest.TestCase):
    TEST_USERNAME = "Deer-Spangle"
    TEST_PASSWORD = os.getenv("test_duo_password")

    def test_day_rollover(self):
        # Setup
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Setup field
        field = DailysDuolingoField(spreadsheet, self.TEST_USERNAME, self.TEST_PASSWORD)
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
        assert len(self.server.send_data) == 1
        assert isinstance(self.server.send_data[0], EventMessage)
        assert self.server.send_data[0].text == json.dumps(notif_dict)
        assert self.server.send_data[0].channel == self.test_chan
        assert self.server.send_data[0].user == self.test_user

    def test_create_from_input_no_username(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo"
        evt = EventMessage(
            self.server,
            self.test_chan,
            self.test_user,
            "{} {}".format(cmd_name, cmd_args),
        )
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
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

    def test_create_from_input_no_password(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {}".format(self.TEST_USERNAME)
        evt = EventMessage(
            self.server,
            self.test_chan,
            self.test_user,
            "{} {}".format(cmd_name, cmd_args),
        )
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
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

    def test_create_from_input_invalid_password(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {} {}".format(self.TEST_USERNAME, "NoTAreaLPasSWorD")
        evt = EventMessage(
            self.server,
            self.test_chan,
            self.test_user,
            "{} {}".format(cmd_name, cmd_args),
        )
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
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

    def test_create_from_input_username_first(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {} {}".format(self.TEST_USERNAME, self.TEST_PASSWORD)
        evt = EventMessage(
            self.server,
            self.test_chan,
            self.test_user,
            "{} {}".format(cmd_name, cmd_args),
        )
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.username == self.TEST_USERNAME
        assert field.password == self.TEST_PASSWORD

    def test_create_from_input_password_first(self):
        # Setup
        cmd_name = "setup dailys field"
        cmd_args = "duolingo {} {}".format(self.TEST_PASSWORD, self.TEST_USERNAME)
        evt = EventMessage(
            self.server,
            self.test_chan,
            self.test_user,
            "{} {}".format(cmd_name, cmd_args),
        )
        evt.split_command_text(cmd_name, cmd_args)
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        # Create from input
        field = DailysDuolingoField.create_from_input(evt, spreadsheet)
        assert field.spreadsheet == spreadsheet
        assert field.username == self.TEST_USERNAME
        assert field.password == self.TEST_PASSWORD
