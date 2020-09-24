import importlib
import inspect
import os
from datetime import time

import pytest

from hallo.events import EventMessage
from hallo.inc.commons import inherits_from
from hallo.modules.dailys.dailys_field_factory import DailysFieldFactory
from hallo.modules.dailys.field_dream import DailysDreamField
from hallo.modules.dailys.field_duolingo import DailysDuolingoField
from hallo.modules.dailys.field_fa import DailysFAField
from hallo.modules.dailys.field_mood import DailysMoodField
from hallo.modules.dailys.field_sleep import DailysSleepField
from hallo.test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock


def get_field_objects(test_user, test_chan):
    spreadsheet = DailysSpreadsheetMock(test_user, test_chan)
    field_obs = list()
    field_obs.append(
        DailysDuolingoField(spreadsheet, "cabinet", os.getenv("test_duo_password"))
    )
    field_obs.append(
        DailysMoodField(
            spreadsheet,
            [DailysMoodField.TIME_SLEEP, time(14, 00), time(22, 00)],
            ["Happiness", "Anger", "Sleepiness"],
        )
    )
    field_obs.append(DailysFAField(spreadsheet))
    field_obs.append(DailysSleepField(spreadsheet))
    field_obs.append(DailysDreamField(spreadsheet))
    return field_obs


def test_field_type_name_doesnt_overlap():
    """
    Test that field classes don't have type_name values which overlap each other
    """
    all_type_names = []
    for field_class in DailysFieldFactory.fields:
        assert field_class.type_name not in all_type_names
        all_type_names.append(field_class.type_name)


def test_field_classes_added_to_factory(hallo_getter):
    """
    Test tht all field classes which are implemented are added to DailysFieldFactory
    """
    hallo_obj, test_server, test_chan, test_user = hallo_getter({"dailys"})
    module_obj = importlib.import_module("hallo.modules.dailys")
    # Loop through module, searching for DailysField subclasses.
    for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
        function_class = function_tuple[1]
        # Only look at subclasses of DailysField
        if not inherits_from(function_class, "DailysField"):
            continue
        # Only look at implemented classes.
        spreadsheet = DailysSpreadsheetMock(test_user, test_chan)
        # noinspection PyBroadException
        try:
            function_class.create_from_input(
                EventMessage(test_server, test_chan, test_user, "hello"),
                spreadsheet,
            )
        except NotImplementedError:
            continue
        except Exception:
            pass
        # Check it's in DailysFieldFactory
        assert function_class.__name__ in [
            sub_class.__name__ for sub_class in DailysFieldFactory.fields
        ]


@pytest.mark.parametrize(
    "field_class", DailysFieldFactory.fields
)
def test_all_field_classes_in_field_objs(field_class, hallo_getter):
    """
    Tests that all field classes have an object in the get_field_objects method here.
    """
    hallo_obj, test_server, test_chan, test_user = hallo_getter({"dailys"})
    assert field_class in [
        field_obj.__class__ for field_obj in get_field_objects(test_user, test_chan)
    ]


@pytest.mark.parametrize(
    "field_class", DailysFieldFactory.fields
)
def test_sub_class_has_type_name(field_class):
    """
    Test that the type_name value has been set for each field class, and that it is lower case
    """
    assert len(field_class.type_name) != 0
    assert field_class.type_name == field_class.type_name.lower()


@pytest.mark.parametrize("field_object", get_field_objects(None, None))
def test_to_json_contains_field_type(field_object):
    """
    Test that to_json() for each field type remembers to set field_type in the json dict
    """
    json_obj = field_object.to_json()
    assert "type_name" in json_obj
