from typing import TYPE_CHECKING
import datetime

from hallo.inc.commons import Commons
from hallo.modules.dailys.dailys_field import DailysException, DailysField
from hallo.modules.dailys.dailys_field_factory import DailysFieldFactory

if TYPE_CHECKING:
    from hallo.destination import Destination, User
    from hallo.hallo import Hallo


class DailysSpreadsheet:
    def __init__(self, user: User, destination: Destination, dailys_url: str, dailys_key: str | None) -> None:
        self.user: User = user
        self.destination: Destination = destination
        self.dailys_url: str = dailys_url
        if self.dailys_url is not None and self.dailys_url[-1] == "/":
            self.dailys_url = self.dailys_url[:-1]
        self.dailys_key: str | None = dailys_key
        self.fields_list: list['DailysField'] = []

    def add_field(self, field: 'DailysField') -> None:
        self.fields_list.append(field)

    async def save_field(self, dailys_field: 'DailysField', data: dict, data_date: datetime.date) -> None:
        """
        Save given data in a specified column for the current date row.
        """
        if dailys_field.type_name is None:
            raise DailysException("Cannot write to unassigned dailys field")
        headers = None
        if self.dailys_key is not None:
            headers = [["Authorization", self.dailys_key]]
        await Commons.put_json_to_url(
            f"{self.dailys_url}/stats/{dailys_field.type_name}/{data_date.isoformat()}/?source=Hallo",
            data,
            headers,
        )

    async def read_path(self, path: str) -> list | dict:
        """
        Save given data in a specified column for the current date row.
        """
        headers = None
        if self.dailys_key is not None:
            headers = [["Authorization", self.dailys_key]]
        return await Commons.load_url_json(f"{self.dailys_url}/{path}", headers)

    async def read_field(self, dailys_field: 'DailysField', data_date: datetime.date) -> dict | None:
        """
        Save given data in a specified column for the current date row.
        """
        if dailys_field.type_name is None:
            raise DailysException("Cannot read from unassigned dailys field")
        data = await self.read_path(f"stats/{dailys_field.type_name}/{data_date.isoformat()}/")
        if len(data) == 0:
            return None
        return data[0]["data"]

    def to_json(self) -> dict:
        json_obj = dict()
        json_obj["server_name"] = self.user.server.name
        json_obj["user_address"] = self.user.address
        if self.destination is not None:
            json_obj["dest_address"] = self.destination.address
        json_obj["dailys_url"] = self.dailys_url
        if self.dailys_key is not None:
            json_obj["dailys_key"] = self.dailys_key
        json_obj["fields"] = []
        for field in self.fields_list:
            json_obj["fields"].append(field.to_json())
        return json_obj

    @staticmethod
    async def from_json(json_obj: dict, hallo_obj: Hallo) -> 'DailysSpreadsheet':
        server = hallo_obj.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise DailysException(f'Could not find server with name "{json_obj["server"]}"')
        user = server.get_user_by_address(json_obj["user_address"])
        if user is None:
            raise DailysException(
                f'Could not find user with address "{json_obj["user_address"]}" on server "{json_obj["server"]}"'
            )
        dest_chan = None
        if "dest_address" in json_obj:
            dest_chan = server.get_channel_by_address(json_obj["dest_address"])
            if dest_chan is None:
                raise DailysException(
                    f'Could not find channel with address "{json_obj["dest_address"]}" on server "{json_obj["server"]}"'
                )
        dailys_url = json_obj["dailys_url"]
        dailys_key = json_obj.get("dailys_key")
        new_spreadsheet = DailysSpreadsheet(user, dest_chan, dailys_url, dailys_key)
        for field_json in json_obj["fields"]:
            new_spreadsheet.add_field(await DailysFieldFactory.from_json(field_json, new_spreadsheet))
        return new_spreadsheet
