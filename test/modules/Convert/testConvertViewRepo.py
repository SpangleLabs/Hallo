import unittest

import modules.Convert
from Events import EventMessage
from test.modules.Convert.ConvertFunctionTestBase import ConvertFunctionTestBase


class MockMethod:

    def __init__(self, response):
        self.response = response
        self.arg = None
        self.args = []

    def method(self, arg):
        self.arg = arg
        self.args.append(arg)
        return self.response


class ConvertViewRepoTest(ConvertFunctionTestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Mock out methods
        self.output_repo = "{repo output}"
        self.output_type = "{type output}"
        self.output_unit = "{unit output}"
        self.output_group = "{group output}"
        self.output_prefix = "{prefix output}"
        self.mock_view_repo = MockMethod(self.output_repo)
        self.mock_view_type = MockMethod(self.output_type)
        self.mock_view_unit = MockMethod(self.output_unit)
        self.mock_view_group = MockMethod(self.output_group)
        self.mock_view_prefix = MockMethod(self.output_prefix)
        self.view_repo = modules.Convert.ConvertViewRepo.output_repo_as_string
        self.view_type = modules.Convert.ConvertViewRepo.output_type_as_string
        self.view_unit = modules.Convert.ConvertViewRepo.output_unit_as_string
        self.view_group = modules.Convert.ConvertViewRepo.output_prefix_group_as_string
        self.view_prefix = modules.Convert.ConvertViewRepo.output_prefix_as_string
        modules.Convert.ConvertViewRepo.output_repo_as_string = self.mock_view_repo.method
        modules.Convert.ConvertViewRepo.output_type_as_string = self.mock_view_type.method
        modules.Convert.ConvertViewRepo.output_unit_as_string = self.mock_view_unit.method
        modules.Convert.ConvertViewRepo.output_prefix_group_as_string = self.mock_view_group.method
        modules.Convert.ConvertViewRepo.output_prefix_as_string = self.mock_view_prefix.method

    def tearDown(self):
        super().tearDown()
        modules.Convert.ConvertViewRepo.output_repo_as_string = self.view_repo
        modules.Convert.ConvertViewRepo.output_type_as_string = self.view_type
        modules.Convert.ConvertViewRepo.output_unit_as_string = self.view_unit
        modules.Convert.ConvertViewRepo.output_prefix_group_as_string = self.view_group
        modules.Convert.ConvertViewRepo.output_prefix_as_string = self.view_prefix

    def test_specified_type_invalid(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo type=no_type"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised type specified" in data[0].text.lower()
        assert self.mock_view_type.arg is None

    def test_type_specified_unit_incorrect(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo type=test_type1 unit=no_unit"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised unit specified" in data[0].text.lower()
        assert self.mock_view_type.arg is None
        assert self.mock_view_unit.arg is None

    def test_type_specified_unit_different_type(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo type=test_type1 unit=unit2a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised unit specified" in data[0].text.lower()
        assert self.mock_view_type.arg is None
        assert self.mock_view_unit.arg is None

    def test_type_and_unit_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo type=test_type1 unit=unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_unit in data[0].text.lower()
        assert self.mock_view_unit.arg == self.test_unit1b
        assert self.mock_view_type.arg is None

    def test_type_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo type=test_type1"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_type in data[0].text.lower()
        assert self.mock_view_type.arg == self.test_type1

    def test_specified_group_invalid(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo group=no_group"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix group specified" in data[0].text.lower()
        assert self.mock_view_group.arg is None

    def test_group_specified_prefix_incorrect(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo group=test_group1 prefix=no_prefix"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix specified" in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg is None

    def test_group_specified_prefix_different_group(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo group=test_group1 prefix=prefix2a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix specified" in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg is None

    def test_group_and_prefix_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo group=test_group1 prefix=prefix1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg == self.test_prefix1a

    def test_group_and_prefix_abbr_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo group=test_group1 prefix=pref1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.mock_view_group.arg is None
        assert self.mock_view_prefix.arg == self.test_prefix1a

    def test_group_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo group=test_group1"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_group in data[0].text.lower()
        assert self.mock_view_group.arg == self.test_group1

    def test_specified_unit_incorrect(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo unit=no_unit"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised unit specified" in data[0].text.lower()
        assert self.mock_view_unit.arg is None

    def test_specified_unit_multiple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo unit=same_name"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_unit in data[0].text.lower()
        assert self.test_unit1b in self.mock_view_unit.args
        assert self.test_unit2b in self.mock_view_unit.args

    def test_unit_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo unit=unit1b"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_unit in data[0].text.lower()
        assert self.mock_view_unit.arg == self.test_unit1b

    def test_specified_prefix_incorrect(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo prefix=no_prefix"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "unrecognised prefix specified" in data[0].text.lower()
        assert self.mock_view_prefix.arg is None

    def test_specified_prefix_multiple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo prefix=prefixb"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.test_prefix1b in self.mock_view_prefix.args
        assert self.test_prefix2b in self.mock_view_prefix.args

    def test_prefix_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo prefix=prefix1a"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_prefix in data[0].text.lower()
        assert self.mock_view_prefix.arg == self.test_prefix1a

    def test_nothing_specified(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "convert view repo"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert self.output_repo in data[0].text.lower()
        assert self.mock_view_repo.arg == self.test_repo
