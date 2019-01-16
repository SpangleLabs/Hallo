from modules.Dailys import DailysSpreadsheet


class DailysSpreadsheetMock(DailysSpreadsheet):

    test_column_key = "abcdefg"

    def __init__(self, user, destination, col_titles=None, saved_data=None):
        """
        :type user: User
        :type destination: Channel | None
        :type col_titles: dict[str, str]
        :type saved_data: dict[date, str]
        """
        super().__init__(user, destination, None)
        self.tagged_columns = []
        self.col_titles = dict() if col_titles is None else col_titles
        self.saved_data = dict() if saved_data is None else saved_data
        """ :type : dict[date, str]"""
        self.channel_messages = []

    def tag_column(self, col_title):
        self.tagged_columns.append(col_title)
        return self.test_column_key

    def find_column_by_names(self, names):
        matches = [col for col in self.col_titles if any([n in self.col_titles[col] for n in names])]
        if len(matches) != 1:
            return None
        return self.col_string_to_num(matches[0])

    def save_field(self, field, data_str, data_date):
        """
        :type field: DailysField
        :type data_str: str
        :type data_date: date
        """
        self.saved_data[data_date] = data_str

    def read_field(self, field, data_date):
        """
        :type field: DailysField
        :type data_date: date
        :rtype: str | None
        """
        if data_date in self.saved_data:
            return self.saved_data[data_date]
        return None
