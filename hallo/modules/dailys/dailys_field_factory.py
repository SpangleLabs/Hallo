import hallo.modules
import hallo.modules.dailys.dailys_field
import hallo.modules.dailys.field_dream
import hallo.modules.dailys.field_duolingo
import hallo.modules.dailys.field_fa
import hallo.modules.dailys.field_mood
import hallo.modules.dailys.field_sleep


class DailysFieldFactory:
    fields = [
        hallo.modules.dailys.field_fa.DailysFAField,
        hallo.modules.dailys.field_duolingo.DailysDuolingoField,
        hallo.modules.dailys.field_sleep.DailysSleepField,
        hallo.modules.dailys.field_mood.DailysMoodField,
        hallo.modules.dailys.field_dream.DailysDreamField
    ]

    @staticmethod
    def from_json(json_obj, spreadsheet):
        type_name = json_obj["type_name"]
        for field in DailysFieldFactory.fields:
            if field.type_name == type_name:
                return field.from_json(json_obj, spreadsheet)
        raise hallo.modules.dailys.dailys_field.DailysException(
            "Could not load dailys field of type {}".format(type_name)
        )