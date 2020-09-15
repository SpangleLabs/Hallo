import os
import unittest

import isodate
import pytest

from hallo.events import EventMessage
from hallo.modules.subscriptions import SubscriptionCheck, E621Sub
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class SubE621ListTest(TestBase, unittest.TestCase):
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
            EventMessage(self.server, self.test_chan, self.test_user, "e621 sub list")
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
        rf1 = E621Sub(
            self.server,
            self.test_chan,
            "cabinet",
            update_frequency=isodate.parse_duration("PT3600S"),
        )
        rfl.add_sub(rf1)
        rf2 = E621Sub(
            self.server,
            another_chan,
            "clefable",
            update_frequency=isodate.parse_duration("PT3600S"),
        )
        rfl.add_sub(rf2)
        rf3 = E621Sub(
            self.server,
            self.test_chan,
            "fez",
            update_frequency=isodate.parse_duration("PT3600S"),
        )
        rfl.add_sub(rf3)
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
