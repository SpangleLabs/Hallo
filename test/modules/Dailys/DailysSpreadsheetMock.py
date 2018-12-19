from modules.Dailys import DailysSpreadsheet


class DailysSpreadsheetMock(DailysSpreadsheet):

    test_column_key = "abcdefg"

    def __init__(self, user, destination, col_titles=None):
        super().__init__(user, destination, None)
        self.tagged_columns = []
        self.col_titles = dict() if col_titles is None else col_titles  # {"AE": "hello", "AF": "furaffinity", "AG": "world"}

    def tag_column(self, col_title):
        self.tagged_columns.append(col_title)
        return self.test_column_key

    def find_column_by_names(self, names):
        matches = [n in self.col_titles for n in names]
        if matches.count(True) != 1:
            return None
        return self.col_string_to_num(self.col_titles[matches.index(True)])
