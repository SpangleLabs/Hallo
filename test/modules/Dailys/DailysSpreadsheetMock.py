from modules.Dailys import DailysSpreadsheet


class DailysSpreadsheetMock(DailysSpreadsheet):

    test_column_key = "abcdefg"

    def __init__(self, user, destination):
        super().__init__(user, destination, None)
        self.tagged_columns = []

    def tag_column(self, col_title):
        self.tagged_columns.append(col_title)
        return self.test_column_key
