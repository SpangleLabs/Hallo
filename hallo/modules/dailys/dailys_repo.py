import json
from typing import List

import hallo.modules.dailys.dailys_spreadsheet


class DailysRepo:
    def __init__(self):
        self.spreadsheets: List[hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet] = []

    def add_spreadsheet(self, spreadsheet: hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet):
        self.spreadsheets.append(spreadsheet)

    def get_by_location(self, event):
        for ds in self.spreadsheets:
            if ds.user == event.user and ds.destination == event.channel:
                return ds
        return None

    def save_json(self):
        json_obj = dict()
        json_obj["spreadsheets"] = []
        for spreadsheet in self.spreadsheets:
            json_obj["spreadsheets"].append(spreadsheet.to_json())
        # Write json to file
        with open("store/dailys.json", "w+") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json(hallo_obj):
        new_dailys_repo = DailysRepo()
        # Try loading json file, otherwise return blank list
        try:
            with open("store/dailys.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            return new_dailys_repo
        for spreadsheet_json in json_obj["spreadsheets"]:
            spreadsheet = hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet.from_json(
                spreadsheet_json, hallo_obj
            )
            new_dailys_repo.add_spreadsheet(spreadsheet)
        return new_dailys_repo
