import os
import unittest

from Events import EventMessage
from inc.Commons import Commons
from modules.Rss import FeedCheck
from modules.Rss import RssFeed
from test.TestBase import TestBase


class FeedListTest(TestBase, unittest.TestCase):

    def setUp(self):
        try:
            os.rename("store/rss_feeds.xml", "store/rss_feeds.xml.tmp")
        except OSError:
            pass
        super().setUp()

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

    def test_no_feeds(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "rss list"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "no rss feeds" in data[0].text.lower()

    def test_list_feeds(self):
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
        rfl = rss_check_obj.rss_feed_list
        # Add RSS feeds to feed list
        rf1 = RssFeed()
        rf1.url = "http://spangle.org.uk/hallo/test_rss.xml?1"
        rf1.title = "test_feed1"
        rf1.server_name = self.server.name
        rf1.channel_name = self.test_chan.name
        rf1.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_feed(rf1)
        rf2 = RssFeed()
        rf2.url = "http://spangle.org.uk/hallo/test_rss.xml?2"
        rf2.title = "test_feed2"
        rf2.server_name = self.server.name
        rf2.channel_name = "another_channel"
        rf2.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_feed(rf2)
        rf3 = RssFeed()
        rf3.url = "http://spangle.org.uk/hallo/test_rss.xml?3"
        rf3.title = "test_feed3"
        rf3.server_name = self.server.name
        rf3.channel_name = self.test_chan.name
        rf3.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_feed(rf3)
        # Run FeedList and check output
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "rss list"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        data_split = data[0].text.split("\n")
        assert "rss feeds posting" in data_split[0].lower()
        assert "test_feed1" in data_split[1].lower() or "test_feed1" in data_split[2].lower()
        assert "test_feed3" in data_split[1].lower() or "test_feed3" in data_split[2].lower()
        assert "http://spangle.org.uk/hallo/test_rss.xml?1" in data_split[1].lower() or \
               "http://spangle.org.uk/hallo/test_rss.xml?1" in data_split[2].lower()
        assert "http://spangle.org.uk/hallo/test_rss.xml?3" in data_split[1].lower() or \
               "http://spangle.org.uk/hallo/test_rss.xml?3" in data_split[2].lower()
        assert "test_feed2" not in data_split[1].lower() and "test_feed2" not in data_split[2].lower()
        assert "http://spangle.org.uk/hallo/test_rss.xml?2" not in data_split[1].lower() and \
               "http://spangle.org.uk/hallo/test_rss.xml?2" not in data_split[2].lower()
