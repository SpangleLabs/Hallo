import importlib
import inspect
import os
import unittest
from datetime import time

from events import EventMessage
from modules.dailys import DailysDuolingoField, DailysFAField, DailysMoodField, DailysSleepField, DailysFieldFactory, \
    DailysField
from test.test_base import TestBase
from test.modules.dailys.dailys_spreadsheet_mock import DailysSpreadsheetMock


class TestAllFieldTypes(TestBase, unittest.TestCase):

    def get_field_objects(self):
        spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
        field_obs = list()
        field_obs.append(DailysDuolingoField(spreadsheet, "cabinet", os.getenv("test_duo_jwt_token")))
        field_obs.append(DailysFAField(spreadsheet))
        field_obs.append(DailysMoodField(
            spreadsheet,
            [DailysMoodField.TIME_SLEEP, time(14, 00), time(22, 00)],
            ["Happiness", "Anger", "Sleepiness"])
        )
        field_obs.append(DailysSleepField(spreadsheet))
        return field_obs

    def test_all_field_classes_in_field_objs(self):
        """
        Tests that all field classes have an object in the get_field_objects method here.
        """
        for field_class in DailysFieldFactory.fields:
            with self.subTest(field_class.__name__):
                assert field_class in [field_obj.__class__ for field_obj in self.get_field_objects()]

    def test_to_json_contains_field_type(self):
        """
        Test that to_json() for each field type remembers to set field_type in the json dict
        """
        for field_obj in self.get_field_objects():
            with self.subTest(field_obj.__class__.__name__):
                json_obj = field_obj.to_json()
                assert "type_name" in json_obj

    def test_field_col_names_dont_overlap(self):
        """
        Test that field classes don't have names values which overlap each other
        """
        all_names = []
        for field_class in DailysFieldFactory.fields:
            for name in field_class.col_names:
                assert name not in all_names
                all_names.append(name)

    def test_field_type_name_doesnt_overlap(self):
        """
        Test that field classes don't have type_name values which overlap each other
        """
        all_type_names = []
        for field_class in DailysFieldFactory.fields:
            assert field_class.type_name not in all_type_names
            all_type_names.append(field_class.type_name)

    def test_sub_class_has_names(self):
        """
        Test that each field class has a non-empty list of column names
        """
        for field_class in DailysFieldFactory.fields:
            with self.subTest(field_class.__name__):
                assert len(field_class.col_names) != 0

    def test_sub_class_names_lower_case(self):
        """
        Test that field class names are all lower case
        """
        for field_class in DailysFieldFactory.fields:
            with self.subTest(field_class.__name__):
                for name in field_class.col_names:
                    assert name == name.lower()

    def test_sub_class_has_type_name(self):
        """
        Test that the type_name value has been set for each field class, and that it is lower case
        """
        for field_class in DailysFieldFactory.fields:
            with self.subTest(field_class.__name__):
                assert len(field_class.type_name) != 0
                assert field_class.type_name == field_class.type_name.lower()

    def test_field_classes_added_to_factory(self):
        """
        Test tht all field classes which are implemented are added to DailysFieldFactory
        """
        module_obj = importlib.import_module("modules.dailys")
        # Loop through module, searching for DailysField subclasses.
        for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
            function_class = function_tuple[1]
            # Only look at subclasses of DailysField
            if not issubclass(function_class, DailysField):
                continue
            # Only look at implemented classes.
            spreadsheet = DailysSpreadsheetMock(self.test_user, self.test_chan)
            # noinspection PyBroadException
            try:
                function_class.create_from_input(
                    EventMessage(self.server, self.test_chan, self.test_user, "hello"),
                    spreadsheet
                )
            except NotImplementedError:
                continue
            except Exception:
                pass
            # Check it's in DailysFieldFactory
            assert function_class.__name__ in [sub_class.__name__ for sub_class in DailysFieldFactory.fields]
