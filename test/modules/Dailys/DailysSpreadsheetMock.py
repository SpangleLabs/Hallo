from Events import EventMessage
from modules.Dailys import DailysSpreadsheet


class DailysSpreadsheetMock(DailysSpreadsheet):

    test_column_key = "abcdefg"

    def __init__(self, user, destination, col_titles=None, saved_data=None):
        super().__init__(user, destination, None)
        self.tagged_columns = []
        self.col_titles = dict() if col_titles is None else col_titles
        self.saved_data = dict() if saved_data is None else saved_data
        self.channel_messages = []

    def tag_column(self, col_title):
        self.tagged_columns.append(col_title)
        return self.test_column_key

    def find_column_by_names(self, names):
        matches = [col for col in self.col_titles if any([n in self.col_titles[col] for n in names])]
        if len(matches) != 1:
            return None
        return self.col_string_to_num(matches[0])

    def save_field(self, field, data_str, date_modifier=0):
        self.saved_data[date_modifier] = data_str
