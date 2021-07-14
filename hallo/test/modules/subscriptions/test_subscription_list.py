import os
import unittest
from datetime import timedelta

import pytest
from yippi import YippiClient

from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class SubscriptionListTest(TestBase, unittest.TestCase):
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

    def test_no_feeds(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "e621 sub list")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "no subscriptions" in data[0].text.lower(), "Actual response: {}".format(
            data[0].text
        )

    def test_list_feeds(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        rss_check_obj = self.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = E621Source("cabinet", e6_client, self.test_user)
        sub1 = Subscription(self.server, self.test_chan, rf1, timedelta(days=1), None, None)
        rfl.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, self.test_user)
        sub2 = Subscription(self.server, another_chan, rf2, timedelta(days=1), None, None)
        rfl.add_sub(sub2)
        rf3 = E621Source("fez", e6_client, self.test_user)
        sub3 = Subscription(self.server, self.test_chan, rf3, timedelta(days=1), None, None)
        rfl.add_sub(sub3)
        # Run FeedList and check output
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "e621 sub list")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        data_split = data[0].text.split("\n")
        assert (
                "subscriptions posting" in data_split[0].lower()
        ), "Missing title. Response data: " + str(data[0].text)
        assert "cabinet" in data_split[1].lower() or "cabinet" in data_split[2].lower()
        assert (
                "clefable" not in data_split[1].lower()
                and "clefable" not in data_split[2].lower()
        )
        assert "fez" in data_split[1].lower() or "fez" in data_split[2].lower()
