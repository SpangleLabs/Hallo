import os
import unittest

import isodate
import pytest

from hallo.events import EventMinute, EventMessage
from hallo.modules.subscriptions.sub_rss import RssSub
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.server_mock import ServerMock
from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class FeedCheckTest(TestBase, unittest.TestCase):
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

    def test_init(self):
        try:
            try:
                os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
            except OSError:
                pass
            fc = SubscriptionCheck()
            assert fc.subscription_repo is None
            assert fc.get_sub_repo(self.hallo) is not None
            assert fc.subscription_repo is not None
            assert fc.subscription_repo.sub_list == []
        finally:
            try:
                os.rename("store/subscriptions.json.tmp", "store/subscriptions.json")
            except OSError:
                pass

    def test_save_function(self):
        fc = SubscriptionCheck()
        # Mock out the rss feed list
        mfl = MockSubscriptionList()
        fc.subscription_repo = mfl
        fc.save_function()
        assert mfl.save_json_called

    def test_run_all(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = SubscriptionRepo()
            rf1 = RssSub(
                chan1.server,
                chan1,
                "http://spangle.org.uk/hallo/test_rss.xml?1",
                title="test_feed1",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf1)
            rf2 = RssSub(
                chan2.server,
                chan2,
                "http://spangle.org.uk/hallo/test_rss.xml?2",
                title="test_feed2",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf2)
            rf3 = RssSub(
                chan3.server,
                chan3,
                "http://spangle.org.uk/hallo/test_rss.xml?3",
                title="test_feed1",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name(
                "check subscription"
            )
            rss_check_obj = self.function_dispatcher.get_function_object(
                rss_check_class
            )  # type: SubscriptionCheck
            rss_check_obj.subscription_repo = rfl
            # Test running all feed updates
            self.function_dispatcher.dispatch(
                EventMessage(
                    self.server, self.test_chan, self.test_user, "rss check all"
                )
            )
            # Check original calling channel data
            serv0_data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "subscription updates were found" in serv0_data[0].text
            # Check test server 1 data
            serv1_data = serv1.get_send_data(6)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line.channel == chan1:
                    chan1_count += 1
                if data_line.channel == chan2:
                    chan2_count += 1
            assert chan1_count == 3
            assert chan2_count == 3
            # Check test server 2 data
            serv2.get_send_data(3, chan3, EventMessage)
            # Test running with no new updates.
            self.function_dispatcher.dispatch(
                EventMessage(
                    self.server, self.test_chan, self.test_user, "rss check all"
                )
            )
            data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "no updates" in data[0].text, "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_by_title(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2")
        user1 = serv1.get_user_by_address("test_user1")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = SubscriptionRepo()
            rf1 = RssSub(
                chan1.server,
                chan1,
                "http://spangle.org.uk/hallo/test_rss.xml?1",
                title="test_feed1",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf1)
            rf2 = RssSub(
                chan2.server,
                chan2,
                "http://spangle.org.uk/hallo/test_rss.xml?2",
                title="test_feed2",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf2)
            rf3 = RssSub(
                chan3.server,
                chan3,
                "http://spangle.org.uk/hallo/test_rss.xml?3",
                title="test_feed1",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name(
                "check subscription"
            )
            rss_check_obj = self.function_dispatcher.get_function_object(
                rss_check_class
            )  # type: SubscriptionCheck
            rss_check_obj.subscription_repo = rfl
            # Invalid title
            self.function_dispatcher.dispatch(
                EventMessage(
                    self.server,
                    self.test_chan,
                    self.test_user,
                    "rss check Not a valid feed",
                )
            )
            data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "error" in data[0].text.lower()
            # Correct title but wrong channel
            self.function_dispatcher.dispatch(
                EventMessage(serv1, chan1, user1, "rss check test_feed2")
            )
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            # Correct title check update
            self.function_dispatcher.dispatch(
                EventMessage(serv1, chan2, user1, "rss check test_feed2")
            )
            data = serv1.get_send_data(4, chan2, EventMessage)
            for x in range(3):
                assert "update on" in data[x].text.lower()
                assert "rss feed" in data[x].text.lower()
            assert (
                "updates were found" in data[3].text.lower()
            ), "Actual message: {}".format(data[0].text)
            # No updates
            rf2.title = "test_feed2"
            self.function_dispatcher.dispatch(
                EventMessage(serv1, chan2, user1, "rss check test_feed2")
            )
            data = serv1.get_send_data(1, chan2, EventMessage)
            assert "no updates" in data[0].text, "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_passive(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = SubscriptionRepo()
            rf1 = RssSub(
                chan1.server,
                chan1,
                "http://spangle.org.uk/hallo/test_rss.xml?1",
                title="test_feed1",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf1)
            rf2 = RssSub(
                chan2.server,
                chan2,
                "http://spangle.org.uk/hallo/test_rss.xml?2",
                title="test_feed2",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf2)
            rf3 = RssSub(
                chan3.server,
                chan3,
                "http://spangle.org.uk/hallo/test_rss.xml?3",
                title="test_feed1",
                update_frequency=isodate.parse_duration("PT3600S"),
            )
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name(
                "check subscription"
            )
            rss_check_obj = self.function_dispatcher.get_function_object(
                rss_check_class
            )  # type: SubscriptionCheck
            rss_check_obj.subscription_repo = rfl
            # Test passive feed updates
            self.function_dispatcher.dispatch_passive(EventMinute())
            # Check test server 1 data
            serv1_data = serv1.get_send_data(6)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line.channel == chan1:
                    chan1_count += 1
                if data_line.channel == chan2:
                    chan2_count += 1
            assert chan1_count == 3
            assert chan2_count == 3
            # Check test server 2 data
            serv2.get_send_data(3, chan3, EventMessage)
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


class MockSubscriptionList:
    def __init__(self):
        self.save_json_called = False

    def save_json(self):
        self.save_json_called = True
