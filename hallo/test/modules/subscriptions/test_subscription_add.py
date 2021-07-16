import os
import unittest

import pytest

from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class SubscriptionAddTest(TestBase, unittest.TestCase):
    def setUp(self):
        try:
            os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
        except OSError:
            pass
        try:
            os.rename(SubscriptionRepo.MENU_STORE_FILE, SubscriptionRepo.MENU_STORE_FILE + ".tmp")
        except OSError:
            pass
        super().setUp()

    def tearDown(self):
        super().tearDown()
        try:
            os.remove("store/subscriptions.json")
        except OSError:
            pass
        try:
            os.rename("store/subscriptions.json.tmp", "store/subscriptions.json")
        except OSError:
            pass
        try:
            os.remove(SubscriptionRepo.MENU_STORE_FILE)
        except OSError:
            pass
        try:
            os.rename(SubscriptionRepo.MENU_STORE_FILE + ".tmp", SubscriptionRepo.MENU_STORE_FILE)
        except OSError:
            pass

    def test_invalid_subscription(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "rss sub add ::")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
            "error" in data[0].text.lower()
        ), "No error in response. Response was: {}".format(data[0].text)

    def test_add_search(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "e621 sub add cabinet"
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
            "created a new e621 subscription" in data[0].text.lower()
        ), "Actual response: {}".format(data[0].text)
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name(
            "e621 sub check"
        )
        e621_check_obj = self.function_dispatcher.get_function_object(
            e621_check_class
        )  # type: SubscriptionCheck
        sub_repo = e621_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(sub_repo) == 1, "Actual length: " + str(len(sub_repo))
        e6_sub: Subscription = sub_repo[0]
        assert e6_sub.server == self.server
        assert e6_sub.destination == self.test_chan
        assert e6_sub.last_check is not None
        assert e6_sub.last_update is None
        assert e6_sub.period.seconds == 600
        assert e6_sub.period.days == 0
        assert e6_sub.source.type_name == E621Source.type_name
        assert e6_sub.source.search == "cabinet"
        assert e6_sub.source.last_keys is not None
        assert len(e6_sub.source.last_keys) >= 50

    def test_add_search_user(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "e621 sub add cabinet")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "created a new e621 subscription" in data[0].text.lower()
        ), "Actual response: {}".format(data[0].text)
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name(
            "e621 sub check"
        )
        e621_check_obj = self.function_dispatcher.get_function_object(
            e621_check_class
        )  # type: SubscriptionCheck
        sub_repo = e621_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(sub_repo) == 1, "Actual length: " + str(len(sub_repo))
        e6_sub: Subscription = sub_repo[0]
        assert e6_sub.server == self.server
        assert e6_sub.destination == self.test_user
        assert e6_sub.last_check is not None
        assert e6_sub.last_update is None
        assert e6_sub.period.seconds == 600
        assert e6_sub.period.days == 0
        assert e6_sub.source.type_name == E621Source.type_name
        assert e6_sub.source.search == "cabinet"
        assert e6_sub.source.last_keys is not None
        assert len(e6_sub.source.last_keys) >= 50

    def test_add_search_period(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                self.test_chan,
                self.test_user,
                "e621 sub add cabinet PT3600S",
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
            "created a new e621 subscription" in data[0].text.lower()
        ), "Actual response: {}".format(data[0].text)
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name(
            "e621 sub check"
        )
        e621_check_obj = self.function_dispatcher.get_function_object(
            e621_check_class
        )  # type: SubscriptionCheck
        sub_repo = e621_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(sub_repo) == 1, "Actual length: " + str(len(sub_repo))
        e6_sub: Subscription = sub_repo[0]
        assert e6_sub.server == self.server
        assert e6_sub.destination == self.test_chan
        assert e6_sub.last_check is not None
        assert e6_sub.last_update is None
        assert e6_sub.period.seconds == 3600
        assert e6_sub.period.days == 0
        assert e6_sub.source.type_name == E621Source.type_name
        assert e6_sub.source.search == "cabinet"
        assert e6_sub.source.last_keys is not None
        assert len(e6_sub.source.last_keys) >= 50
