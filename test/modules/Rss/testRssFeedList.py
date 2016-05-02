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

    def test_remove_feed(self):
        # Setup a feed list
        rfl = RssFeedList()
        rf1 = RssFeed()
        rf1.url = "http://spangle.org.uk/hallo/test_feed.xml?1"
        rfl.add_feed(rf1)
        rf2 = RssFeed()
        rf2.url = "http://spangle.org.uk/hallo/test_feed.xml?2"
        rfl.add_feed(rf2)
        assert len(rfl.feed_list) == 2
        # Remove an item from the feed list
        rfl.remove_feed(rf1)
        assert len(rfl.feed_list) == 1
        assert rfl.feed_list[0] == rf2
