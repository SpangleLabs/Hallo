import os
import unittest

import pytest

from hallo.events import EventMessage
from hallo.modules.subscriptions import SubscriptionCheck, RssSub
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class FeedAddTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        try:
            os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
        except OSError:
            pass

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

    def test_invalid_url(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server, self.test_chan, self.test_user, "rss add not_a_url"
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()

    def test_invalid_rss(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                self.test_chan,
                self.test_user,
                "rss add http://example.com",
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()

    def test_add_feed(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                self.test_chan,
                self.test_user,
                "rss add http://spangle.org.uk/hallo/test_rss.xml",
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
            "created a new rss subscription" in data[0].text.lower()
        ), "Actual response: {}".format(data[0].text)
        # Check the rss feed was added
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(rfl) == 1
        rss_sub = rfl[0]  # type: RssSub
        assert rss_sub.url == "http://spangle.org.uk/hallo/test_rss.xml"
        assert rss_sub.server == self.server
        assert rss_sub.destination == self.test_chan
        assert rss_sub.last_item_hash is not None
        assert rss_sub.last_check is not None
        assert rss_sub.update_frequency.seconds == 600
        assert rss_sub.update_frequency.days == 0

    def test_add_feed_user(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "rss add http://spangle.org.uk/hallo/test_rss.xml",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "created a new rss subscription" in data[0].text.lower()
        ), "Actual response: {}".format(data[0].text)
        # Check the rss feed was added
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(rfl) == 1
        rss_sub = rfl[0]  # type: RssSub
        assert rss_sub.url == "http://spangle.org.uk/hallo/test_rss.xml"
        assert rss_sub.server == self.server
        assert rss_sub.destination == self.test_user
        assert rss_sub.last_item_hash is not None
        assert rss_sub.last_check is not None
        assert rss_sub.update_frequency.seconds == 600
        assert rss_sub.update_frequency.days == 0

    def test_add_feed_period(self):
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                self.test_chan,
                self.test_user,
                "rss add http://spangle.org.uk/hallo/test_rss.xml PT300S",
            )
        )
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert (
            "created a new rss subscription" in data[0].text.lower()
        ), "Actual response: {}".format(data[0].text)
        # Check the rss feed was added
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rfl = rss_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(rfl) == 1
        rss_sub = rfl[0]  # type: RssSub
        assert rss_sub.url == "http://spangle.org.uk/hallo/test_rss.xml"
        assert rss_sub.server == self.server
        assert rss_sub.destination == self.test_chan
        assert rss_sub.last_item_hash is not None
        assert rss_sub.last_check is not None
        assert rss_sub.update_frequency.seconds == 300
        assert rss_sub.update_frequency.days == 0
