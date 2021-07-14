import os
import unittest
from datetime import timedelta

import isodate
import pytest
from yippi import YippiClient

from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class SubscriptionRemoveTest(TestBase, unittest.TestCase):
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

    def test_remove_by_search(self):
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get subscription list
        e621_check_class = self.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        e621_check_obj = self.function_dispatcher.get_function_object(
            e621_check_class
        )  # type: SubscriptionCheck
        sub_repo = e621_check_obj.get_sub_repo(self.hallo)
        # Add E621 searches to subscription list
        rf1 = E621Source("cabinet", e6_client, self.test_user)
        sub1 = Subscription(self.server, self.test_chan, rf1, timedelta(days=1), None, None)
        sub_repo.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, self.test_user)
        sub2 = Subscription(self.server, another_chan, rf2, timedelta(days=1), None, None)
        sub_repo.add_sub(sub2)
        rf3 = E621Source("fez", e6_client, self.test_user)
        sub3 = Subscription(self.server, self.test_chan, rf3, timedelta(days=1), None, None)
        sub_repo.add_sub(sub3)
        # Remove test search
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "e621 sub remove cabinet"
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "removed subscription" in data[0].text.lower()
        assert "e621" in data[0].text.lower()
        assert "\"cabinet\"" in data[0].text.lower()
        assert sub1 not in sub_repo.sub_list
        assert sub2 in sub_repo.sub_list
        assert sub3 in sub_repo.sub_list

    def test_remove_multiple_matching_searches(self):
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get subscription list
        e621_check_class = self.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        e621_check_obj = self.function_dispatcher.get_function_object(
            e621_check_class
        )  # type: SubscriptionCheck
        rfl = e621_check_obj.get_sub_repo(self.hallo)
        # Add E621 searches to subscription list
        rf1 = E621Source("cabinet", e6_client, self.test_user)
        sub1 = Subscription(self.server, self.test_chan, rf1, timedelta(days=1), None, None)
        rfl.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, self.test_user)
        sub2 = Subscription(self.server, another_chan, rf2, timedelta(days=1), None, None)
        rfl.add_sub(sub2)
        rf3 = E621Source("cabinet", e6_client, self.test_user)
        sub3 = Subscription(self.server, self.test_chan, rf3, timedelta(days=1), None, None)
        rfl.add_sub(sub3)
        # Remove test feed
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "e621 sub remove cabinet"
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
                "removed 2 subscriptions" in data[0].text.lower()
        ), "Response did not contain expected string. Response was {}".format(
            data[0].text
        )
        assert (
                "cabinet" in data[0].text.lower()
        ), "Response did not contain expected string. Response was {}".format(
            data[0].text
        )
        assert (
                "e621" in data[0].text.lower()
        ), "Response did not contain expected string. Response was {}".format(
            data[0].text
        )
        assert sub1 not in rfl.sub_list
        assert sub2 in rfl.sub_list
        assert sub3 not in rfl.sub_list

    def test_remove_no_match(self):
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get subscription list
        e621_check_class = self.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        e621_check_obj = self.function_dispatcher.get_function_object(
            e621_check_class
        )  # type: SubscriptionCheck
        sub_repo = e621_check_obj.get_sub_repo(self.hallo)
        # Add E621 searches to subscription list
        rf1 = E621Source("cabinet", e6_client, self.test_user)
        sub1 = Subscription(self.server, self.test_chan, rf1, timedelta(days=1), None, None)
        sub_repo.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, self.test_user)
        sub2 = Subscription(self.server, another_chan, rf2, timedelta(days=1), None, None)
        sub_repo.add_sub(sub2)
        rf3 = E621Source("fez", e6_client, self.test_user)
        sub3 = Subscription(self.server, self.test_chan, rf3, timedelta(days=1), None, None)
        sub_repo.add_sub(sub3)
        # Try to remove invalid search
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                self.test_chan,
                self.test_user,
                "e621 sub remove not_a_search",
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert sub1 in sub_repo.sub_list
        assert sub2 in sub_repo.sub_list
        assert sub3 in sub_repo.sub_list
