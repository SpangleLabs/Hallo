import unittest

from inc.Commons import Commons
from modules.Rss import RssFeedList, RssFeed


class TestRssFeedList(unittest.TestCase):

    def test_init(self):
        rfl = RssFeedList()
        assert rfl.feed_list == []

    def test_add_feed(self):
        rfl = RssFeedList()
        assert rfl.feed_list == []
        # Create example rss feed
        rf = RssFeed()
        rf.update_frequency = Commons.load_time_delta("P0T3600S")
        rf.url = "http://spangle.org.uk/hallo/test_feed.xml"
        rfl.add_feed(rf)
        assert len(rfl.feed_list) == 1
        assert rfl.feed_list[0] == rf
