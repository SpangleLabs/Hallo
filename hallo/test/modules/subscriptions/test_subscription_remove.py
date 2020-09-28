import os
import unittest

import isodate
import pytest

from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class FeedRemoveTest(TestBase, unittest.TestCase):
    def setUp(self):
        try:
            os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
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

    def test_remove_by_search(self):
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
        rf1 = E621Source("cabinet")
        rfl.add_sub(rf1)
        rf2 = E621Source("clefable")
        rfl.add_sub(rf2)
        rf3 = E621Source("fez")
        rfl.add_sub(rf3)
        # Remove test search
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "e621 sub remove cabinet"
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
                'removed e621 subscription to search for "cabinet"' in data[0].text.lower()
        ), "Response did not contain expected string. Response was {}".format(
            data[0].text
        )
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list

    def test_remove_multiple_matching_searches(self):
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
        rf1 = E621Source("cabinet")
        rfl.add_sub(rf1)
        rf2 = E621Source("clefable")
        rfl.add_sub(rf2)
        rf3 = E621Source("cabinet")
        rfl.add_sub(rf3)
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
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 not in rfl.sub_list

    def test_remove_no_match(self):
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
        rf1 = E621Source("cabinet")
        rfl.add_sub(rf1)
        rf2 = E621Source("clefable")
        rfl.add_sub(rf2)
        rf3 = E621Source("fez")
        rfl.add_sub(rf3)
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
        assert rf1 in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list
