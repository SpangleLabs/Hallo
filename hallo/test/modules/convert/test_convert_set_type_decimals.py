import unittest

from hallo.events import EventMessage
from hallo.test.modules.convert.convert_function_test_base import ConvertFunctionTestBase


class ConvertSetTypeDecimalsTest(ConvertFunctionTestBase, unittest.TestCase):
    def test_no_number_given(self):
        decimals = self.test_repo.get_type_by_name("test_type1").decimals
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert set type decimals test_type1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "please specify" in data[0].text.lower()
        assert "a number of decimal places" in data[0].text.lower()
        assert (
            self.test_repo.get_type_by_name("test_type1").decimals == decimals
        ), "Decimals shouldn't have changed."

    def test_decimals_at_start(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert set type decimals 5 test_type1",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "set the number of decimal places" in data[0].text.lower()
        assert '"test_type1" type units' in data[0].text
        assert "at 5 places" in data[0].text
        assert (
            self.test_repo.get_type_by_name("test_type1").decimals == 5
        ), "Decimals wasn't set."

    def test_decimals_at_end(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "convert set type decimals test_type1 5",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "set the number of decimal places" in data[0].text.lower()
        assert '"test_type1" type units' in data[0].text
        assert "at 5 places" in data[0].text
        assert (
            self.test_repo.get_type_by_name("test_type1").decimals == 5
        ), "Decimals wasn't set."

    def test_no_type(self):
        decimals1 = self.test_repo.get_type_by_name("test_type1").decimals
        decimals2 = self.test_repo.get_type_by_name("test_type2").decimals
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, None, self.test_user, "convert set type decimals 5"
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "this is not a recognised conversion type" in data[0].text.lower()
        assert (
            self.test_repo.get_type_by_name("test_type1").decimals == decimals1
        ), "Decimals shouldn't have changed."
        assert (
            self.test_repo.get_type_by_name("test_type2").decimals == decimals2
        ), "Decimals shouldn't have changed."
