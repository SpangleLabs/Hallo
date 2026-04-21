import json

from hallo.events import EventMessage
from hallo.hallo import Hallo
from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


class DailysRepo:
    def __init__(self) -> None:
        self.spreadsheets: list[DailysSpreadsheet] = []

    def add_spreadsheet(self, spreadsheet: DailysSpreadsheet) -> None:
        self.spreadsheets.append(spreadsheet)

    def get_by_location(self, event: EventMessage) -> DailysSpreadsheet | None:
        for ds in self.spreadsheets:
            if ds.user == event.user and ds.destination == event.channel:
                return ds
        return None

    def save_json(self) -> dict:
        json_obj = {
            "spreadsheets": [spreadsheet.to_json() for spreadsheet in self.spreadsheets],
        }
        # Write json to file
        with open("store/dailys.json", "w+") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json(hallo_obj: 'Hallo') -> 'DailysRepo':
        new_dailys_repo = DailysRepo()
        # Try loading json file, otherwise return blank list
        try:
            with open("store/dailys.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            return new_dailys_repo
        for spreadsheet_json in json_obj["spreadsheets"]:
            spreadsheet = DailysSpreadsheet.from_json(spreadsheet_json, hallo_obj)
            new_dailys_repo.add_spreadsheet(spreadsheet)
        return new_dailys_repo
