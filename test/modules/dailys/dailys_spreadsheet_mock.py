from modules.dailys import DailysSpreadsheet


class DailysSpreadsheetMock(DailysSpreadsheet):
    def __init__(self, user, destination, saved_data=None):
        """
        :type user: User
        :type destination: Channel | None
        :type saved_data: dict[str, dict[date, dict]]
        """
        super().__init__(user, destination, None, None)
        self.saved_data = dict() if saved_data is None else saved_data
        """ :type : dict[str, dict[date, str]]"""

    def save_field(self, field, data, data_date):
        """
        :type field: DailysField
        :type data: dict
        :type data_date: date
        """
        if field.type_name not in self.saved_data:
            self.saved_data[field.type_name] = {}
        self.saved_data[field.type_name][data_date] = data

    def read_field(self, field, data_date):
        """
        :type field: DailysField
        :type data_date: date
        :rtype: str | None
        """
        if field.type_name in self.saved_data:
            if data_date in self.saved_data[field.type_name]:
                return self.saved_data[field.type_name][data_date]
        return None
