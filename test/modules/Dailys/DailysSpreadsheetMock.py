from modules.Dailys import DailysSpreadsheet


class DailysSpreadsheetMock(DailysSpreadsheet):

    def __init__(self, user, destination):
        super().__init__(user, destination, None)

