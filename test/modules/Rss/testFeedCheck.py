import os
import unittest

from Server import Server
from inc.Commons import Commons
from modules.Rss import FeedCheck, RssFeedList, RssFeed
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class FeedCheckTest(TestBase, unittest.TestCase):

    def test_init(self):
        try:
            try:
                os.rename("store/rss_feeds.xml", "store/rss_feeds.xml.tmp")
            except FileNotFoundError:
                pass
            fc = FeedCheck()
            assert fc.rss_feed_list is not None
            assert fc.rss_feed_list.feed_list == []
        finally:
            try:
                os.rename("store/rss_feeds.xml.tmp", "store/rss_feeds.xml")
            except FileNotFoundError:
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
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan2 = serv1.get_channel_by_name("test_chan2")
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_name("test_chan1")
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
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)
            rss_check_obj.rss_feed_list = rfl
            # Test running all feed updates
            self.function_dispatcher.dispatch("rss check all", self.test_user, self.test_chan)
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
            self.function_dispatcher.dispatch("rss check all", self.test_user, self.test_chan)
            data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "no feed updates" in data[0][0], "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_by_title(self):
        pass  # TODO
        # Invalid title
        # Correct title check update
        # Correct title but wrong channel
        # No updates

    def test_run_passive(self):
        pass  # TODO
        # Test running all feed updates
        # Test running with no new updates


class MockRssFeedList:

    def __init__(self):
        self.to_xml_called = False

    def to_xml(self):
        self.to_xml_called = True
