import os
import unittest

import pytest

from events import EventMessage
from inc.commons import Commons
from modules.subscriptions import SubscriptionCheck, RssSub
from test.test_base import TestBase


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

    def test_remove_by_title(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("check subscription")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf1)
        rf2 = RssSub(
            self.server, another_chan, "http://spangle.org.uk/hallo/test_rss.xml?2",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf2)
        rf3 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?3",
            title="test_feed3", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf3)
        # Remove test feed
        self.function_dispatcher.dispatch(EventMessage(
            self.server, self.test_chan, self.test_user, "rss remove test_feed1")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "removed rss subscription to test_feed1" in data[0].text.lower(), \
            "Response did not contain expected string. Response was: {}".format(data[0].text)
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list

    def test_remove_multiple_matching_titles(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("check subscription")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S"))
        rfl.add_sub(rf1)
        rf2 = RssSub(
            self.server, another_chan, "http://spangle.org.uk/hallo/test_rss.xml?2",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S"))
        rfl.add_sub(rf2)
        rf3 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?3",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S"))
        rfl.add_sub(rf3)
        # Remove test feed
        self.function_dispatcher.dispatch(EventMessage(
            self.server, self.test_chan, self.test_user, "rss remove test_feed1"
        ))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "removed 2 subscriptions" in data[0].text.lower(), "Response was: {}".format(data[0].text)
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 not in rfl.sub_list

    def test_remove_no_match(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("check subscription")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S"))
        rfl.add_sub(rf1)
        rf2 = RssSub(
            self.server, another_chan, "http://spangle.org.uk/hallo/test_rss.xml?2",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S"))
        rfl.add_sub(rf2)
        rf3 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?3",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S"))
        rfl.add_sub(rf3)
        # Remove test feed
        self.function_dispatcher.dispatch(EventMessage(
            self.server, self.test_chan, self.test_user, "rss remove not_a_feed"
        ))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        assert rf1 in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list

    def test_remove_by_url(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("check subscription")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf1)
        rf2 = RssSub(
            self.server, another_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf2)
        rf3 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?3",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf3)
        # Remove test feed
        self.function_dispatcher.dispatch(EventMessage(
            self.server, self.test_chan, self.test_user,
            "rss remove http://spangle.org.uk/hallo/test_rss.xml?1")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower()
        assert "removed" in data[0].text.lower()
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list

    def test_remove_multiple_matching_urls(self):
        another_chan = self.server.get_channel_by_address("another_channel")
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("check subscription")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo)
        # Add RSS feeds to feed list
        rf1 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf1)
        rf2 = RssSub(
            self.server, another_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf2)
        rf3 = RssSub(
            self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml?1",
            title="test_feed1", update_frequency=Commons.load_time_delta("PT3600S")
        )
        rfl.add_sub(rf3)
        # Remove test feed
        self.function_dispatcher.dispatch(EventMessage(
            self.server, self.test_chan, self.test_user,
            "rss remove http://spangle.org.uk/hallo/test_rss.xml?1")
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" not in data[0].text.lower(), "Actual response: {}".format(data[0].text)
        assert "removed" in data[0].text.lower()
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 not in rfl.sub_list
