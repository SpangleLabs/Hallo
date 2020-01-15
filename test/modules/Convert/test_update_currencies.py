import unittest

import pytest

import modules.convert
from events import EventMessage, EventHour
from test.test_base import TestBase


class MockUpdate:

    def __init__(self, answer):
        self.answer = answer
        self.was_called = False

    def method(self, arg1=None, arg2=None):
        self.was_called = True
        return self.answer

    def method_throws(self, arg1=None, arg2=None):
        self.was_called = True
        raise Exception(self.answer)


class UpdateCurrenciesTest(TestBase, unittest.TestCase):

    def test_run(self):
        update_all = modules.convert.UpdateCurrencies.update_all
        mock_update_all = MockUpdate(["Check method called"])
        modules.convert.UpdateCurrencies.update_all = mock_update_all.method
        try:
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "update currencies"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert data[0].text == "Check method called"
            assert mock_update_all.was_called, "update_all() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_all = update_all

    def test_passive_run(self):
        update_all = modules.convert.UpdateCurrencies.update_all
        mock_update_all = MockUpdate(["Check method called"])
        modules.convert.UpdateCurrencies.update_all = mock_update_all.method
        try:
            self.function_dispatcher.dispatch_passive(EventHour())
            self.server.get_send_data(0)
            assert mock_update_all.was_called, "update_all() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_all = update_all

    def test_update_all(self):
        # Mock out methods
        mock_ecb = MockUpdate(None)
        mock_forex = MockUpdate(None)
        mock_cryptonator = MockUpdate(None)
        update_ecb = modules.convert.UpdateCurrencies.update_from_european_bank_data
        update_forex = modules.convert.UpdateCurrencies.update_from_forex_data
        update_cryptonator = modules.convert.UpdateCurrencies.update_from_cryptonator_data
        modules.convert.UpdateCurrencies.update_from_european_bank_data = mock_ecb.method
        modules.convert.UpdateCurrencies.update_from_forex_data = mock_forex.method
        modules.convert.UpdateCurrencies.update_from_cryptonator_data = mock_cryptonator.method
        try:
            # Test update_all calls all 3, and gives reply
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "update currencies"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "Updated currency data from the European Central Bank" in data[0].text
            assert "Updated currency data from Forex" in data[0].text
            assert "Updated currency data from Cryptonator" in data[0].text
            assert mock_ecb.was_called, "update_from_european_bank_data() wasn't called."
            assert mock_forex.was_called, "update_from_forex_data() wasn't called."
            assert mock_cryptonator.was_called, "update_from_cryptonator_data() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_from_european_bank_data = update_ecb
            modules.convert.UpdateCurrencies.update_from_forex_data = update_forex
            modules.convert.UpdateCurrencies.update_from_cryptonator_data = update_cryptonator

    def test_update_all_fail_ecb(self):
        # Mock out methods
        mock_ecb = MockUpdate("HTTPException: 403")
        mock_forex = MockUpdate(None)
        mock_cryptonator = MockUpdate(None)
        update_ecb = modules.convert.UpdateCurrencies.update_from_european_bank_data
        update_forex = modules.convert.UpdateCurrencies.update_from_forex_data
        update_cryptonator = modules.convert.UpdateCurrencies.update_from_cryptonator_data
        modules.convert.UpdateCurrencies.update_from_european_bank_data = mock_ecb.method_throws
        modules.convert.UpdateCurrencies.update_from_forex_data = mock_forex.method
        modules.convert.UpdateCurrencies.update_from_cryptonator_data = mock_cryptonator.method
        try:
            # Test update_all calls all 3, and gives reply
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "update currencies"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "Failed to update European Central Bank data" in data[0].text
            assert "HTTPException: 403" in data[0].text
            assert "Updated currency data from Forex" in data[0].text
            assert "Updated currency data from Cryptonator" in data[0].text
            assert mock_ecb.was_called, "update_from_european_bank_data() wasn't called."
            assert mock_forex.was_called, "update_from_forex_data() wasn't called."
            assert mock_cryptonator.was_called, "update_from_cryptonator_data() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_from_european_bank_data = update_ecb
            modules.convert.UpdateCurrencies.update_from_forex_data = update_forex
            modules.convert.UpdateCurrencies.update_from_cryptonator_data = update_cryptonator

    def test_update_all_fail_forex(self):
        # Mock out methods
        mock_ecb = MockUpdate(None)
        mock_forex = MockUpdate("HTTPException: 403")
        mock_cryptonator = MockUpdate(None)
        update_ecb = modules.convert.UpdateCurrencies.update_from_european_bank_data
        update_forex = modules.convert.UpdateCurrencies.update_from_forex_data
        update_cryptonator = modules.convert.UpdateCurrencies.update_from_cryptonator_data
        modules.convert.UpdateCurrencies.update_from_european_bank_data = mock_ecb.method
        modules.convert.UpdateCurrencies.update_from_forex_data = mock_forex.method_throws
        modules.convert.UpdateCurrencies.update_from_cryptonator_data = mock_cryptonator.method
        try:
            # Test update_all calls all 3, and gives reply
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "update currencies"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "Updated currency data from the European Central Bank" in data[0].text
            assert "Failed to update Forex data" in data[0].text
            assert "HTTPException: 403" in data[0].text
            assert "Updated currency data from Cryptonator" in data[0].text
            assert mock_ecb.was_called, "update_from_european_bank_data() wasn't called."
            assert mock_forex.was_called, "update_from_forex_data() wasn't called."
            assert mock_cryptonator.was_called, "update_from_cryptonator_data() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_from_european_bank_data = update_ecb
            modules.convert.UpdateCurrencies.update_from_forex_data = update_forex
            modules.convert.UpdateCurrencies.update_from_cryptonator_data = update_cryptonator

    def test_update_all_fail_cryptonator(self):
        # Mock out methods
        mock_ecb = MockUpdate(None)
        mock_forex = MockUpdate(None)
        mock_cryptonator = MockUpdate("HTTPException: 403")
        update_ecb = modules.convert.UpdateCurrencies.update_from_european_bank_data
        update_forex = modules.convert.UpdateCurrencies.update_from_forex_data
        update_cryptonator = modules.convert.UpdateCurrencies.update_from_cryptonator_data
        modules.convert.UpdateCurrencies.update_from_european_bank_data = mock_ecb.method
        modules.convert.UpdateCurrencies.update_from_forex_data = mock_forex.method
        modules.convert.UpdateCurrencies.update_from_cryptonator_data = mock_cryptonator.method_throws
        try:
            # Test update_all calls all 3, and gives reply
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "update currencies"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "Updated currency data from the European Central Bank" in data[0].text
            assert "Updated currency data from Forex" in data[0].text
            assert "Failed to update Cryptonator data" in data[0].text
            assert "HTTPException: 403" in data[0].text
            assert mock_ecb.was_called, "update_from_european_bank_data() wasn't called."
            assert mock_forex.was_called, "update_from_forex_data() wasn't called."
            assert mock_cryptonator.was_called, "update_from_cryptonator_data() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_from_european_bank_data = update_ecb
            modules.convert.UpdateCurrencies.update_from_forex_data = update_forex
            modules.convert.UpdateCurrencies.update_from_cryptonator_data = update_cryptonator

    def test_update_all_fail_all(self):
        # Mock out methods
        mock_ecb = MockUpdate("HTTPException: 403")
        mock_forex = MockUpdate("HTTPException: 500")
        mock_cryptonator = MockUpdate("HTTPException: 404")
        update_ecb = modules.convert.UpdateCurrencies.update_from_european_bank_data
        update_forex = modules.convert.UpdateCurrencies.update_from_forex_data
        update_cryptonator = modules.convert.UpdateCurrencies.update_from_cryptonator_data
        modules.convert.UpdateCurrencies.update_from_european_bank_data = mock_ecb.method_throws
        modules.convert.UpdateCurrencies.update_from_forex_data = mock_forex.method_throws
        modules.convert.UpdateCurrencies.update_from_cryptonator_data = mock_cryptonator.method_throws
        try:
            # Test update_all calls all 3, and gives reply
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "update currencies"))
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert "Failed to update European Central Bank data" in data[0].text
            assert "HTTPException: 403" in data[0].text
            assert "Failed to update Forex data" in data[0].text
            assert "HTTPException: 500" in data[0].text
            assert "Failed to update Cryptonator data" in data[0].text
            assert "HTTPException: 404" in data[0].text
            assert mock_ecb.was_called, "update_from_european_bank_data() wasn't called."
            assert mock_forex.was_called, "update_from_forex_data() wasn't called."
            assert mock_cryptonator.was_called, "update_from_cryptonator_data() wasn't called."
        finally:
            modules.convert.UpdateCurrencies.update_from_european_bank_data = update_ecb
            modules.convert.UpdateCurrencies.update_from_forex_data = update_forex
            modules.convert.UpdateCurrencies.update_from_cryptonator_data = update_cryptonator

    @pytest.mark.external_integration
    def test_update_ecb(self):
        # Set up test repo
        test_repo = modules.convert.ConvertRepo()
        test_type = modules.convert.ConvertType(test_repo, "currency")
        test_type.base_unit = modules.convert.ConvertUnit(test_type, ["EUR"], 1)
        test_repo.add_type(test_type)
        currency_codes = ["USD", "JPY", "BGN", "CZK", "DKK", "GBP", "HUF", "PLN", "RON", "SEK", "CHF", "ISK", "NOK",
                          "HRK", "RUB", "TRY", "AUD", "BRL", "CAD", "CNY", "HKD", "IDR", "ILS", "INR", "KRW", "MXN",
                          "NZD", "PHP", "SGD", "THB", "ZAR"]
        for code in currency_codes:
            test_unit = modules.convert.ConvertUnit(test_type, [code], 0)
            test_type.add_unit(test_unit)
        # Run update_from_european_bank_data
        c = modules.convert.UpdateCurrencies()
        c.update_from_european_bank_data(test_repo)
        # Check results
        for code in currency_codes:
            test_unit = test_type.get_unit_by_name(code)
            assert test_unit.value != 0, "Currency was not updated: {}".format(code)

    @pytest.mark.external_integration
    def test_update_forex(self):
        # Set up test repo
        test_repo = modules.convert.ConvertRepo()
        test_type = modules.convert.ConvertType(test_repo, "currency")
        test_type.base_unit = modules.convert.ConvertUnit(test_type, ["EUR"], 1)
        test_repo.add_type(test_type)
        currency_codes = ["USD", "CHF", "GBP", "JPY", "AUD", "CAD", "SEK", "NOK", "NZD", "TRY"]
        for code in currency_codes:
            test_unit = modules.convert.ConvertUnit(test_type, [code], 0)
            test_type.add_unit(test_unit)
        # Run update_from_forex_data
        c = modules.convert.UpdateCurrencies()
        c.update_from_forex_data(test_repo)
        # Check results
        for code in currency_codes:
            test_unit = test_type.get_unit_by_name(code)
            assert test_unit.value != 0, "Currency was not updated: {}".format(code)

    @pytest.mark.external_integration
    @pytest.mark.skip(reason="Cryptonator API occasionally returns HTML pages")
    def test_update_cryptonator(self):
        # Set up test repo
        test_repo = modules.convert.ConvertRepo()
        test_type = modules.convert.ConvertType(test_repo, "currency")
        test_type.base_unit = modules.convert.ConvertUnit(test_type, ["EUR"], 1)
        test_repo.add_type(test_type)
        currency_codes = ["LTC", "BTC", "BCH", "DOGE", "XMR", "ETH", "ETC", "DASH"]
        for code in currency_codes:
            test_unit = modules.convert.ConvertUnit(test_type, [code], 0)
            test_type.add_unit(test_unit)
        # Run update_from_cryptonator_data
        c = modules.convert.UpdateCurrencies()
        c.update_from_cryptonator_data(test_repo)
        # Check results
        for code in currency_codes:
            test_unit = test_type.get_unit_by_name(code)
            assert test_unit.value != 0, "Currency was not updated: {}".format(code)
