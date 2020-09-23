import json
from datetime import timedelta

import duolingo

from hallo.events import EventDay
import hallo.modules.dailys.dailys_field


class DailysDuolingoField(hallo.modules.dailys.dailys_field.DailysField):
    type_name = "duolingo"

    def __init__(self, spreadsheet, username, password):
        super().__init__(spreadsheet)
        self.username = username
        self.password = password

    @staticmethod
    def passive_events():
        """
        :rtype: list[type]
        """
        return [EventDay]

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: None
        """
        try:
            lingo = duolingo.Duolingo(self.username, password=self.password)
            friends = lingo.get_friends()
        except Exception:
            self.message_channel(
                "It seems the password no longer works for Duolingo account {}. "
                "Please reset it.".format(self.username)
            )
            return
        result = dict()
        for friend in friends:
            result[friend["username"]] = friend["points"]
        result_str = json.dumps(result)
        d = (evt.get_send_time() - timedelta(1)).date()
        self.save_data(result, d)
        # Send date to destination
        self.message_channel(result_str)

    @staticmethod
    def _check_duo_username(username, password):
        try:
            lingo = duolingo.Duolingo(username, password=password)
            lingo.get_friends()
            return True
        except Exception:
            return False

    @staticmethod
    def create_from_input(event, spreadsheet):
        clean_input = (
            event.command_args[len(DailysDuolingoField.type_name):].strip().split()
        )
        if len(clean_input) != 2:
            raise hallo.modules.dailys.dailys_field.DailysException(
                "You must specify both a duolingo username, and password."
            )
        username = clean_input[0]
        password = clean_input[1]
        if DailysDuolingoField._check_duo_username(username, password):
            return DailysDuolingoField(spreadsheet, username, password)
        elif DailysDuolingoField._check_duo_username(password, username):
            return DailysDuolingoField(spreadsheet, password, username)
        else:
            raise hallo.modules.dailys.dailys_field.DailysException(
                "Could not access a duolingo account with that username and password."
            )

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        json_obj["username"] = self.username
        json_obj["password"] = self.password
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        password = None
        if "password" in json_obj:
            password = json_obj["password"]
        return DailysDuolingoField(spreadsheet, json_obj["username"], password)
