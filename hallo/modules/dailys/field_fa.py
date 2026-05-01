import json
import os
from datetime import timedelta
from typing import TYPE_CHECKING, Type

import hallo.modules.user_data
import hallo.modules.dailys.dailys_field
from hallo.events import EventDay, EventMessage, Event
from hallo.inc.commons import Commons

if TYPE_CHECKING:
    from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet

class DailysFAField(hallo.modules.dailys.dailys_field.DailysField):
    type_name = "furaffinity"

    @staticmethod
    def passive_events() -> list[Type[Event]]:
        """
        :rtype: list[type]
        """
        return [EventDay]

    async def passive_trigger(self, evt: Event) -> None:
        user_parser = hallo.modules.user_data.UserDataParser()
        fa_data: hallo.modules.user_data.FAKeyData = user_parser.get_data_by_user_and_type(
            self.spreadsheet.user, hallo.modules.user_data.FAKeyData
        )
        if fa_data is None:
            raise hallo.modules.dailys.dailys_field.DailysException(
                "No FA data has been set up for the FA field module to use."
            )
        cookie = "b=" + fa_data.cookie_b + "; a=" + fa_data.cookie_a
        fa_api_url = os.getenv("FA_API_URL", "https://faexport.spangle.org.uk")
        try:
            notifications_data = await Commons.load_url_json(
                "{}/notifications/others.json".format(fa_api_url),
                [["FA_COOKIE", cookie]],
            )
        except Exception:
            raise hallo.modules.dailys.dailys_field.DailysException(
                "FA key in storage is not currently logged in to FA."
            )
        profile_name = notifications_data["current_user"]["profile_name"]
        profile_data = await Commons.load_url_json("{}/user/{}.json".format(fa_api_url, profile_name))
        notifications = {
            "submissions": notifications_data["notification_counts"]["submissions"],
            "comments": notifications_data["notification_counts"]["comments"],
            "journals": notifications_data["notification_counts"]["journals"],
            "favourites": notifications_data["notification_counts"]["favorites"],
            "watches": notifications_data["notification_counts"]["watchers"],
            "notes": notifications_data["notification_counts"]["notes"],
            "watchers_count": profile_data["watchers"]["count"],
            "watching_count": profile_data["watching"]["count"]
        }
        d = (evt.get_send_time() - timedelta(1)).date()
        await self.save_data(notifications, d)
        # Send date to destination
        notif_str = json.dumps(notifications)
        await self.message_channel(notif_str)

    @staticmethod
    def create_from_input(event: EventMessage, spreadsheet: 'DailysSpreadsheet') -> 'DailysFAField':
        # Check user has an FA login
        user_parser = hallo.modules.user_data.UserDataParser()
        fa_data = user_parser.get_data_by_user_and_type(spreadsheet.user, hallo.modules.user_data.FAKeyData)
        if not isinstance(fa_data, hallo.modules.user_data.FAKeyData):
            raise hallo.modules.dailys.dailys_field.DailysException(
                "No FA data has been set up for the FA dailys field to use."
            )
        return DailysFAField(spreadsheet)

    def to_json(self) -> dict:
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        return json_obj

    @staticmethod
    def from_json(json_obj: dict, spreadsheet: 'DailysSpreadsheet') -> 'DailysFAField':
        return DailysFAField(spreadsheet)
