import os
import unittest

from Events import EventMinute, EventMessage
from Server import Server
from inc.Commons import Commons
from modules.Rss import FeedCheck, RssFeedList, RssFeed
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class FeedCheckTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        try:
            os.rename("store/rss_feeds.xml", "store/rss_feeds.xml.tmp")
        except OSError:
            pass

    def tearDown(self):
        super().tearDown()
        try:
            os.remove("store/rss_feeds.xml")
        except OSError:
            pass
        try:
            os.rename("store/rss_feeds.xml.tmp", "store/rss_feeds.xml")
        except OSError:
            pass

    def test_init(self):
        try:
            try:
                os.rename("store/rss_feeds.xml", "store/rss_feeds.xml.tmp")
            except OSError:
                pass
            fc = FeedCheck()
            assert fc.rss_feed_list is not None
            assert fc.rss_feed_list.feed_list == []
        finally:
            try:
                os.rename("store/rss_feeds.xml.tmp", "store/rss_feeds.xml")
            except OSError:
                pass

    def test_save_function(self):
        fc = FeedCheck()
        # Mock out the rss feed list
        mfl = MockRssFeedList()
        fc.rss_feed_list = mfl
        fc.save_function()
        assert mfl.to_xml_called

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
            rfl = RssFeedList()
            rf1 = RssFeed()
            rf1.url = "http://spangle.org.uk/hallo/test_rss.xml?1"
            rf1.title = "test_feed1"
            rf1.server_name = chan1.server.name
            rf1.channel_name = chan1.name
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf1)
            rf2 = RssFeed()
            rf2.url = "http://spangle.org.uk/hallo/test_rss.xml?2"
            rf2.title = "test_feed2"
            rf2.server_name = chan2.server.name
            rf2.channel_name = chan2.name
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf2)
            rf3 = RssFeed()
            rf3.url = "http://spangle.org.uk/hallo/test_rss.xml?3"
            rf3.title = "test_feed1"
            rf3.server_name = chan3.server.name
            rf3.channel_name = chan3.name
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
            rss_check_obj.rss_feed_list = rfl
            # Test running all feed updates
            self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                           "rss check all"))
            # Check original calling channel data
            serv0_data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "feed updates were found" in serv0_data[0][0]
            # Check test server 1 data
            serv1_data = serv1.get_send_data(6)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line[1] == chan1:
                    chan1_count += 1
                if data_line[1] == chan2:
                    chan2_count += 1
            assert chan1_count == 3
            assert chan2_count == 3
            # Check test server 2 data
            serv2_data = serv2.get_send_data(3, chan3, Server.MSG_MSG)
            # Test running with no new updates.
            self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                           "rss check all"))
            data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "no feed updates" in data[0][0], "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_by_title(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = RssFeedList()
            rf1 = RssFeed()
            rf1.url = "http://spangle.org.uk/hallo/test_rss.xml?1"
            rf1.title = "test_feed1"
            rf1.server_name = chan1.server.name
            rf1.channel_name = chan1.name
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf1)
            rf2 = RssFeed()
            rf2.url = "http://spangle.org.uk/hallo/test_rss.xml?2"
            rf2.title = "test_feed2"
            rf2.server_name = chan2.server.name
            rf2.channel_name = chan2.name
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf2)
            rf3 = RssFeed()
            rf3.url = "http://spangle.org.uk/hallo/test_rss.xml?3"
            rf3.title = "test_feed1"
            rf3.server_name = chan3.server.name
            rf3.channel_name = chan3.name
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
            rss_check_obj.rss_feed_list = rfl
            # Invalid title
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "rss check Not a valid feed"))
            data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            # Correct title but wrong channel
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1, "rss check test_feed2"))
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            # Correct title check update
            self.function_dispatcher.dispatch(EventMessage(serv1, chan2, user1, "rss check test_feed2"))
            data = serv1.get_send_data(1, chan2, Server.MSG_MSG)
            assert "feed updates were found" in data[0][0].lower()
            assert len(data[0][0].lower().split("\n")) == 4
            # No updates
            rf2.title = "test_feed2"
            self.function_dispatcher.dispatch(EventMessage(serv1, chan2, user1, "rss check test_feed2"))
            data = serv1.get_send_data(1, chan2, Server.MSG_MSG)
            assert "no updates" in data[0][0], "No further updates should be found."
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
            rfl = RssFeedList()
            rf1 = RssFeed()
            rf1.url = "http://spangle.org.uk/hallo/test_rss.xml?1"
            rf1.title = "test_feed1"
            rf1.server_name = chan1.server.name
            rf1.channel_name = chan1.name
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf1)
            rf2 = RssFeed()
            rf2.url = "http://spangle.org.uk/hallo/test_rss.xml?2"
            rf2.title = "test_feed2"
            rf2.server_name = chan2.server.name
            rf2.channel_name = chan2.name
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf2)
            rf3 = RssFeed()
            rf3.url = "http://spangle.org.uk/hallo/test_rss.xml?3"
            rf3.title = "test_feed1"
            rf3.server_name = chan3.server.name
            rf3.channel_name = chan3.name
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_feed(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
            rss_check_obj.rss_feed_list = rfl
            # Test passive feed updates
            self.function_dispatcher.dispatch_passive(EventMinute())
            # Check test server 1 data
            serv1_data = serv1.get_send_data(6)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line[1] == chan1:
                    chan1_count += 1
                if data_line[1] == chan2:
                    chan2_count += 1
            assert chan1_count == 3
            assert chan2_count == 3
            # Check test server 2 data
            serv2_data = serv2.get_send_data(3, chan3, Server.MSG_MSG)
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
            assert not self.failed, "check_feed() should not have been called on any feed."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def do_not_call(self):
        self.failed = True
        return []


class MockRssFeedList:

    def __init__(self):
        self.to_xml_called = False

    def to_xml(self):
        self.to_xml_called = True
