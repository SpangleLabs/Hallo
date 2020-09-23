from hallo.events import EventMessage
from hallo.inc.commons import Commons
from hallo.modules.dailys.dailys_field import DailysField


class DailysDreamField(DailysField):
    type_name = "dreams"

    @staticmethod
    def create_from_input(event, spreadsheet):
        return DailysDreamField(spreadsheet)

    @staticmethod
    def passive_events():
        return [EventMessage]

    def passive_trigger(self, evt):
        if not isinstance(evt, EventMessage):
            return
        if not evt.text.lower().startswith("dream"):
            return
        data_date = evt.get_send_time().date()
        dream_text = evt.text
        new_dream = {"text": dream_text}
        dream_data = self.load_data(data_date)
        if dream_data is None:
            dream_data = {"dreams": []}
        dream_data["dreams"].append(new_dream)
        dream_count = len(dream_data["dreams"])
        self.save_data(dream_data, data_date)
        # Send date to destination
        dream_ordinal = Commons.ordinal(dream_count)
        self.message_channel("Logged dream. {} of the day.".format(dream_ordinal))

    def to_json(self):
        json_obj = dict()
        json_obj["type_name"] = self.type_name
        return json_obj

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return DailysDreamField(spreadsheet)