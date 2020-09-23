from hallo.inc.commons import Commons
from hallo.modules.dailys.dailys_field import DailysException, DailysFieldFactory


class DailysSpreadsheet:
    def __init__(self, user, destination, dailys_url, dailys_key):
        """
        :type user: destination.User
        :type destination: destination.Destination
        :type dailys_url: str
        :type dailys_key: str | None
        """
        self.user = user
        """ :type : Destination.User"""
        self.destination = destination
        """ :type : Destination.Destination | None"""
        self.dailys_url = dailys_url
        if self.dailys_url is not None and self.dailys_url[-1] == "/":
            self.dailys_url = self.dailys_url[:-1]
        """ :type : str"""
        self.dailys_key = dailys_key
        """ :type : str"""
        self.fields_list = []
        """ :type : list[DailysField]"""

    def add_field(self, field):
        """
        :type field: DailysField
        """
        self.fields_list.append(field)

    def save_field(self, dailys_field, data, data_date):
        """
        Save given data in a specified column for the current date row.
        :type dailys_field: DailysField
        :type data: dict
        :type data_date: date
        """
        if dailys_field.type_name is None:
            raise DailysException("Cannot write to unassigned dailys field")
        headers = None
        if self.dailys_key is not None:
            headers = [["Authorization", self.dailys_key]]
        Commons.put_json_to_url(
            "{}/stats/{}/{}/?source=Hallo".format(
                self.dailys_url, dailys_field.type_name, data_date.isoformat()
            ),
            data,
            headers,
        )

    def read_path(self, path):
        """
        Save given data in a specified column for the current date row.
        :type path: str
        :rtype: list | dict
        """
        headers = None
        if self.dailys_key is not None:
            headers = [["Authorization", self.dailys_key]]
        return Commons.load_url_json(
            "{}/{}".format(
                self.dailys_url, path
            ),
            headers
        )

    def read_field(self, dailys_field, data_date):
        """
        Save given data in a specified column for the current date row.
        :type dailys_field: DailysField
        :type data_date: date
        :rtype: dict | None
        """
        if dailys_field.type_name is None:
            raise DailysException("Cannot read from unassigned dailys field")
        data = self.read_path("stats/{}/{}/".format(dailys_field.type_name, data_date.isoformat()))
        if len(data) == 0:
            return None
        return data[0]["data"]

    def to_json(self):
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
    def from_json(json_obj, hallo):
        server = hallo.get_server_by_name(json_obj["server_name"])
        if server is None:
            raise DailysException(
                'Could not find server with name "{}"'.format(json_obj["server"])
            )
        user = server.get_user_by_address(json_obj["user_address"])
        if user is None:
            raise DailysException(
                'Could not find user with address "{}" on server "{}"'.format(
                    json_obj["user_address"], json_obj["server"]
                )
            )
        dest_chan = None
        if "dest_address" in json_obj:
            dest_chan = server.get_channel_by_address(json_obj["dest_address"])
            if dest_chan is None:
                raise DailysException(
                    'Could not find channel with address "{}" on server "{}"'.format(
                        json_obj["dest_address"], json_obj["server"]
                    )
                )
        dailys_url = json_obj["dailys_url"]
        dailys_key = json_obj.get("dailys_key")
        new_spreadsheet = DailysSpreadsheet(user, dest_chan, dailys_url, dailys_key)
        for field_json in json_obj["fields"]:
            new_spreadsheet.add_field(
                DailysFieldFactory.from_json(field_json, new_spreadsheet)
            )
        return new_spreadsheet