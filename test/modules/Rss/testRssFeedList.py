import os
import unittest

from inc.Commons import Commons
from modules.Rss import RssFeedList, RssFeed
from test.ServerMock import ServerMock


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

    def test_get_feeds_by_destination(self):
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user2 = serv1.get_user_by_name("test_user2")
        chan3 = serv2.get_channel_by_name("test_chan3")
        # Setup a feed list
        rfl = RssFeedList()
        rf1 = RssFeed()
        rf1.url = "http://spangle.org.uk/hallo/test_feed.xml?1"
        rf1.server_name = chan1.server.name
        rf1.channel_name = chan1.name
        rfl.add_feed(rf1)
        rf2 = RssFeed()
        rf2.url = "http://spangle.org.uk/hallo/test_feed.xml?2"
        rf2.server_name = user2.server.name
        rf2.user_name = user2.name
        rfl.add_feed(rf2)
        rf3 = RssFeed()
        rf3.url = "http://spangle.org.uk/hallo/test_feed.xml?3"
        rf3.server_name = chan3.server.name
        rf3.channel_name = chan3.name
        rfl.add_feed(rf3)
        rf4 = RssFeed()
        rf4.url = "http://spangle.org.uk/hallo/test_feed.xml?4"
        rf4.server_name = chan3.server.name
        rf4.channel_name = chan3.name
        rfl.add_feed(rf4)
        rf5 = RssFeed()
        rf5.url = "http://spangle.org.uk/hallo/test_feed.xml?5"
        rf5.title = "test_feed3"
        rf5.server_name = chan3.server.name
        rf5.channel_name = chan3.name
        rfl.add_feed(rf5)
        # Check function
        feed_list = rfl.get_feeds_by_destination(chan3)
        assert len(feed_list) == 3
        assert rf4 in feed_list
        assert rf3 in feed_list
        assert rf5 in feed_list

    def test_get_feeds_by_title(self):
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user2 = serv1.get_user_by_name("test_user2")
        chan3 = serv2.get_channel_by_name("test_chan3")
        # Setup a feed list
        rfl = RssFeedList()
        rf1 = RssFeed()
        rf1.url = "http://spangle.org.uk/hallo/test_feed.xml?1"
        rf1.title = "test_feed1"
        rf1.server_name = chan1.server.name
        rf1.channel_name = chan1.name
        rfl.add_feed(rf1)
        rf2 = RssFeed()
        rf2.url = "http://spangle.org.uk/hallo/test_feed.xml?2"
        rf2.title = "test_feed2"
        rf2.server_name = user2.server.name
        rf2.user_name = user2.name
        rfl.add_feed(rf2)
        rf3 = RssFeed()
        rf3.url = "http://spangle.org.uk/hallo/test_feed.xml?3"
        rf3.title = "test_feed3"
        rf3.server_name = chan3.server.name
        rf3.channel_name = chan3.name
        rfl.add_feed(rf3)
        rf4 = RssFeed()
        rf4.url = "http://spangle.org.uk/hallo/test_feed.xml?4"
        rf4.title = "test_feed4"
        rf4.server_name = chan3.server.name
        rf4.channel_name = chan3.name
        rfl.add_feed(rf4)
        rf5 = RssFeed()
        rf5.url = "http://spangle.org.uk/hallo/test_feed.xml?5"
        rf5.title = "test_feed3"
        rf5.server_name = chan3.server.name
        rf5.channel_name = chan3.name
        rfl.add_feed(rf5)
        # Check function
        feed_list = rfl.get_feeds_by_title("test_feed3", chan3)
        assert len(feed_list) == 2
        assert rf3 in feed_list
        assert rf5 in feed_list

    def test_get_feeds_by_url(self):
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user2 = serv1.get_user_by_name("test_user2")
        chan3 = serv2.get_channel_by_name("test_chan3")
        # Setup a feed list
        rfl = RssFeedList()
        rf1 = RssFeed()
        rf1.url = "http://spangle.org.uk/hallo/test_feed.xml?1"
        rf1.title = "test_feed1"
        rf1.server_name = chan1.server.name
        rf1.channel_name = chan1.name
        rfl.add_feed(rf1)
        rf2 = RssFeed()
        rf2.url = "http://spangle.org.uk/hallo/test_feed.xml?2"
        rf2.title = "test_feed2"
        rf2.server_name = user2.server.name
        rf2.user_name = user2.name
        rfl.add_feed(rf2)
        rf3 = RssFeed()
        rf3.url = "http://spangle.org.uk/hallo/test_feed.xml?3"
        rf3.title = "test_feed3"
        rf3.server_name = chan3.server.name
        rf3.channel_name = chan3.name
        rfl.add_feed(rf3)
        rf4 = RssFeed()
        rf4.url = "http://spangle.org.uk/hallo/test_feed.xml?4"
        rf4.title = "test_feed4"
        rf4.server_name = chan3.server.name
        rf4.channel_name = chan3.name
        rfl.add_feed(rf4)
        rf5 = RssFeed()
        rf5.url = "http://spangle.org.uk/hallo/test_feed.xml?4"
        rf5.title = "test_feed3"
        rf5.server_name = chan3.server.name
        rf5.channel_name = chan3.name
        rfl.add_feed(rf5)
        # Check function
        feed_list = rfl.get_feeds_by_url("http://spangle.org.uk/hallo/test_feed.xml?4", chan3)
        assert len(feed_list) == 2
        assert rf4 in feed_list
        assert rf5 in feed_list

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

    def test_xml(self):
        # Setup a feed list
        rfl = RssFeedList()
        rf1 = RssFeed()
        rf1.url = "http://spangle.org.uk/hallo/test_feed.xml?1"
        rf1.title = "test_feed1"
        rf1.update_frequency = Commons.load_time_delta("P0T3600S")
        rf1.server_name = "test_serv1"
        rf1.channel_name = "test_chan1"
        rfl.add_feed(rf1)
        rf2 = RssFeed()
        rf2.url = "http://spangle.org.uk/hallo/test_feed.xml?2"
        rf2.title = "test_feed2"
        rf2.update_frequency = Commons.load_time_delta("P1TS")
        rf2.server_name = "test_serv2"
        rf2.channel_name = "test_chan2"
        rfl.add_feed(rf2)
        rf3 = RssFeed()
        rf3.url = "http://spangle.org.uk/hallo/test_feed.xml?3"
        rf3.title = "test_feed3"
        rf3.update_frequency = Commons.load_time_delta("PT60S")
        rf3.server_name = "test_serv3"
        rf3.user_name = "test_user3"
        rfl.add_feed(rf3)
        # Save to XML and load
        try:
            try:
                os.rename("store/rss_feeds.xml", "store/rss_feeds.xml.tmp")
            except FileNotFoundError:
                pass
            rfl.to_xml()
            new_rfl = RssFeedList.from_xml()
            assert len(new_rfl.feed_list) == 3
        finally:
            try:
                os.remove("store/rss_feeds.xml")
            except FileNotFoundError:
                pass
            try:
                os.rename("store/rss_feeds.xml.tmp", "store/rss_feeds.xml")
            except FileNotFoundError:
                pass
