import os
import unittest
from datetime import timedelta

import pytest
from yippi import YippiClient

from hallo.events import EventMinute, EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.server_mock import ServerMock
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class SubscriptionCheckTest(TestBase, unittest.TestCase):
    def setUp(self):
        try:
            os.rename(SubscriptionRepo.STORE_FILE, SubscriptionRepo.STORE_FILE + ".tmp")
        except OSError:
            pass
        super().setUp()

    def tearDown(self):
        super().tearDown()
        try:
            os.remove(SubscriptionRepo.STORE_FILE)
        except OSError:
            pass
        try:
            os.rename(SubscriptionRepo.STORE_FILE + ".tmp", SubscriptionRepo.STORE_FILE)
        except OSError:
            pass

    def test_run_all(self):
        # Set up test servers and channels
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        user2 = serv2.get_user_by_address("test_user2".lower(), "test_user2")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            sub_repo = SubscriptionRepo(self.hallo)
            rf1 = E621Source("cabinet", e6_client, user1)
            sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
            sub_repo.add_sub(sub1)
            rf2 = E621Source("clefable", e6_client, user1)
            sub2 = Subscription(serv1, chan2, rf2, timedelta(days=1), None, None)
            sub_repo.add_sub(sub2)
            rf3 = E621Source("fez", e6_client, user2)
            sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
            sub_repo.add_sub(sub3)
            # Splice this rss feed list into the function dispatcher's rss check object
            e621_sub_check = self.function_dispatcher.get_function_by_name(
                "check subscription"
            )
            e621_sub_obj = self.function_dispatcher.get_function_object(
                e621_sub_check
            )  # type: SubscriptionCheck
            e621_sub_obj.subscription_repo = sub_repo
            # Test running all feed updates
            self.function_dispatcher.dispatch(
                EventMessage(
                    self.server, self.test_chan, self.test_user, "e621 sub check all"
                )
            )
            # Check original calling channel data
            serv0_data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert (
                    "subscription updates were found" in serv0_data[0].text.lower()
            ), "Actual message: {}".format(serv0_data[0].text)
            # Check test server 1 data
            serv1_data = serv1.get_send_data(150)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line.channel == chan1:
                    chan1_count += 1
                if data_line.channel == chan2:
                    chan2_count += 1
            assert chan1_count == 75
            assert chan2_count == 75
            # Check test server 2 data
            serv2.get_send_data(75, chan3, EventMessage)
            # Test running with no new updates.
            self.function_dispatcher.dispatch(
                EventMessage(
                    self.server, self.test_chan, self.test_user, "e621 sub check all"
                )
            )
            data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "no updates" in data[0].text, "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_by_search(self):
        # Set up test servers and channels
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        user1 = serv1.get_user_by_address("test_user1", "test_user1")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        user2 = serv2.get_user_by_address("test_user2", "test_user2")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            sub_repo = SubscriptionRepo(self.hallo)
            rf1 = E621Source("cabinet", e6_client, user1)
            sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
            sub_repo.add_sub(sub1)
            rf2 = E621Source("clefable", e6_client, user1)
            sub2 = Subscription(serv1, chan2, rf2, timedelta(days=1), None, None)
            sub_repo.add_sub(sub2)
            rf3 = E621Source("fez", e6_client, user2)
            sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
            sub_repo.add_sub(sub3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name(
                "check subscription"
            )
            rss_check_obj = self.function_dispatcher.get_function_object(
                rss_check_class
            )  # type: SubscriptionCheck
            rss_check_obj.subscription_repo = sub_repo
            # Invalid title
            self.function_dispatcher.dispatch(
                EventMessage(
                    self.server,
                    self.test_chan,
                    self.test_user,
                    "e621 sub check Not a valid search",
                )
            )
            data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "error" in data[0].text.lower()
            # Correct title but wrong channel
            self.function_dispatcher.dispatch(
                EventMessage(serv1, chan1, user1, "e621 sub check clefable")
            )
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            # Correct title check update
            self.function_dispatcher.dispatch(
                EventMessage(serv1, chan2, user1, "e621 sub check clefable")
            )
            data = serv1.get_send_data(76, chan2, EventMessage)
            has_photo_id = 0
            for x in range(75):
                assert "update on" in data[x].text.lower()
                if hasattr(data[x], "photo_id") and data[x].photo_id is not None:
                    has_photo_id += 1
                assert "clefable" in data[x].text
            assert has_photo_id > 40, "Almost all subscription updates should have a photo"
            assert (
                    "subscription updates were found" in data[75].text.lower()
            ), "Actual message: {}".format(data[0].text)
            # No updates
            self.function_dispatcher.dispatch(
                EventMessage(serv1, chan2, user1, "e621 sub check clefable")
            )
            data = serv1.get_send_data(1, chan2, EventMessage)
            assert "no updates" in data[0].text, "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_passive(self):
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        user1 = serv1.get_user_by_address("test_user1", "test_user2")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        user2 = serv2.get_user_by_address("test_user2", "test_user2")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            sub_repo = SubscriptionRepo(self.hallo)
            rf1 = E621Source("cabinet", e6_client, user1)
            sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
            sub_repo.add_sub(sub1)
            rf2 = E621Source("clefable", e6_client, user1)
            sub2 = Subscription(serv1, chan2, rf2, timedelta(days=1), None, None)
            sub_repo.add_sub(sub2)
            rf3 = E621Source("fez", e6_client, user2)
            sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
            sub_repo.add_sub(sub3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name(
                "check subscription"
            )
            rss_check_obj = self.function_dispatcher.get_function_object(
                rss_check_class
            )  # type: SubscriptionCheck
            rss_check_obj.subscription_repo = sub_repo
            # Test passive feed updates
            self.function_dispatcher.dispatch_passive(EventMinute())
            # Check test server 1 data
            serv1_data = serv1.get_send_data(150)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line.channel == chan1:
                    chan1_count += 1
                if data_line.channel == chan2:
                    chan2_count += 1
            assert chan1_count == 75
            assert chan2_count == 75
            # Check test server 2 data
            serv2.get_send_data(75, chan3, EventMessage)
            # Test that no updates are found the second run
            rf1.last_check = None
            rf2.last_check = None
            rf3.last_check = None
            self.function_dispatcher.dispatch_passive(EventMinute())
            serv1.get_send_data(0)
            serv2.get_send_data(0)
            # Test that no feeds are checked before timeout, set urls to none and see if anything explodes.
            self.failed = False
            rf1.check_feed = self.do_not_call
            rf2.check_feed = self.do_not_call
            rf3.check_feed = self.do_not_call
            self.function_dispatcher.dispatch_passive(EventMinute())
            serv1.get_send_data(0)
            serv2.get_send_data(0)
            assert (
                not self.failed
            ), "check_feed() should not have been called on any feed."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def do_not_call(self):
        self.failed = True
        return []
