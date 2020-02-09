import os
import unittest

import pytest

from events import EventMessage
from inc.commons import Commons
from modules.subscriptions import SubscriptionCheck, RssSub
from test.test_base import TestBase


@pytest.mark.external_integration
class FeedListTest(TestBase, unittest.TestCase):
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

    def test_no_feeds(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "rss list")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "no subscriptions" in data[0].text.lower(), "Actual response: {}".format(
            data[0].text
        )

    def test_list_feeds(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        rss_check_obj = self.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = RssSub(
            self.server,
            self.test_chan,
            "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1",
            update_frequency=Commons.load_time_delta("PT3600S"),
        )
        rfl.add_sub(rf1)
        rf2 = RssSub(
            self.server,
            another_chan,
            "http://spangle.org.uk/hallo/test_rss.xml?2",
            title="test_feed2",
            update_frequency=Commons.load_time_delta("PT3600S"),
        )
        rfl.add_sub(rf2)
        rf3 = RssSub(
            self.server,
            self.test_chan,
            "http://spangle.org.uk/hallo/test_rss.xml?3",
            title="test_feed3",
            update_frequency=Commons.load_time_delta("PT3600S"),
        )
        rfl.add_sub(rf3)
        # Run FeedList and check output
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "rss list")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        data_split = data[0].text.split("\n")
        assert (
            "subscriptions posting" in data_split[0].lower()
        ), "Actual message: {}".format(data[0].text)
        assert (
            "test_feed1" in data_split[1].lower()
            or "test_feed1" in data_split[2].lower()
        )
        assert (
            "test_feed3" in data_split[1].lower()
            or "test_feed3" in data_split[2].lower()
        )
        assert (
            "http://spangle.org.uk/hallo/test_rss.xml?1" in data_split[1].lower()
            or "http://spangle.org.uk/hallo/test_rss.xml?1" in data_split[2].lower()
        )
        assert (
            "http://spangle.org.uk/hallo/test_rss.xml?3" in data_split[1].lower()
            or "http://spangle.org.uk/hallo/test_rss.xml?3" in data_split[2].lower()
        )
        assert (
            "test_feed2" not in data_split[1].lower()
            and "test_feed2" not in data_split[2].lower()
        )
        assert (
            "http://spangle.org.uk/hallo/test_rss.xml?2" not in data_split[1].lower()
            and "http://spangle.org.uk/hallo/test_rss.xml?2"
            not in data_split[2].lower()
        )
