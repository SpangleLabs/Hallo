import os
from datetime import timedelta

import pytest

from hallo.modules.subscriptions.source_rss import RssSource
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.server_mock import ServerMock


def test_init(hallo_getter):
    hallo_obj, test_server, test_chan, test_user = hallo_getter({"subscriptions"})
    rfl = SubscriptionRepo(hallo_obj)
    assert rfl.sub_list == []


def test_add_feed(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(hallo)
    assert sub_repo.sub_list == []
    # Create example rss feed
    rf = RssSource("http://spangle.org.uk/hallo/test_rss.xml", "feed title")
    sub = Subscription(test_server, test_channel, rf, timedelta(days=1), None, None)
    sub_repo.add_sub(sub)
    assert len(sub_repo.sub_list) == 1
    assert sub_repo.sub_list[0] == sub


def test_get_feeds_by_destination(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv2 = ServerMock(hallo)
    serv2.name = "test_serv2"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user2 = serv1.get_user_by_address("test_user2", "test_user2")
    chan3 = serv2.get_channel_by_address("test_chan3".lower(), "test_chan3")
    # Setup a feed list
    rfl = SubscriptionRepo(hallo)
    rf1 = RssSource("http://spangle.org.uk/hallo/test_rss.xml?1", "feed 1")
    sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
    rfl.add_sub(sub1)
    rf2 = RssSource("http://spangle.org.uk/hallo/test_rss.xml?2", "feed 2")
    sub2 = Subscription(serv1, user2, rf2, timedelta(days=1), None, None)
    rfl.add_sub(sub2)
    rf3 = RssSource("http://spangle.org.uk/hallo/test_rss.xml?3", "feed 3")
    sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
    rfl.add_sub(sub3)
    rf4 = RssSource("http://spangle.org.uk/hallo/test_rss.xml?4", "feed 4")
    sub4 = Subscription(serv2, chan3, rf4, timedelta(days=1), None, None)
    rfl.add_sub(sub4)
    rf5 = RssSource(
        "http://spangle.org.uk/hallo/test_rss.xml?5",
        feed_title="feed 5",
    )
    sub5 = Subscription(serv2, chan3, rf5, timedelta(days=1), None, None)
    rfl.add_sub(sub5)
    # Check function
    feed_list = rfl.get_subs_by_destination(chan3)
    assert len(feed_list) == 3
    assert sub4 in feed_list
    assert sub3 in feed_list
    assert sub5 in feed_list


def test_get_feeds_by_title(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv2 = ServerMock(hallo)
    serv2.name = "test_serv2"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user2 = serv1.get_user_by_address("test_user2", "test_user2")
    chan3 = serv2.get_channel_by_address("test_chan3".lower(), "test_chan3")
    # Setup a feed list
    sub_repo = SubscriptionRepo(hallo)
    rf1 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?1",
        feed_title="test_feed1",
    )
    sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
    sub_repo.add_sub(sub1)
    rf2 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?2",
        feed_title="test_feed2",
    )
    sub2 = Subscription(serv1, user2, rf2, timedelta(days=1), None, None)
    sub_repo.add_sub(sub2)
    rf3 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?3",
        feed_title="test_feed3",
    )
    sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
    sub_repo.add_sub(sub3)
    rf4 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?4",
        feed_title="test_feed4",
    )
    sub4 = Subscription(serv2, chan3, rf4, timedelta(days=1), None, None)
    sub_repo.add_sub(sub4)
    rf5 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?5",
        feed_title="test_feed3",
    )
    sub5 = Subscription(serv2, chan3, rf5, timedelta(days=1), None, None)
    sub_repo.add_sub(sub5)
    # Check function
    feed_list = sub_repo.get_subs_by_name("test_feed3", chan3)
    assert len(feed_list) == 2
    assert sub3 in feed_list
    assert sub5 in feed_list


def test_get_feeds_by_url(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    serv1 = ServerMock(hallo)
    serv1.name = "test_serv1"
    serv2 = ServerMock(hallo)
    serv2.name = "test_serv2"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user2 = serv1.get_user_by_address("test_user2", "test_user2")
    chan3 = serv2.get_channel_by_address("test_chan3".lower(), "test_chan3")
    # Setup a feed list
    sub_repo = SubscriptionRepo(hallo)
    rf1 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?1",
        feed_title="test_feed1",
    )
    sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
    sub_repo.add_sub(sub1)
    rf2 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?2",
        feed_title="test_feed2",
    )
    sub2 = Subscription(serv1, user2, rf2, timedelta(days=1), None, None)
    sub_repo.add_sub(sub2)
    rf3 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?3",
        feed_title="test_feed3",
    )
    sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
    sub_repo.add_sub(sub3)
    rf4 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?4",
        feed_title="test_feed4",
    )
    sub4 = Subscription(serv2, chan3, rf4, timedelta(days=1), None, None)
    sub_repo.add_sub(sub4)
    rf5 = RssSource(
        "http://spangle.org.uk/hallo/test_feed.xml?4",
        feed_title="test_feed3",
    )
    sub5 = Subscription(serv2, chan3, rf5, timedelta(days=1), None, None)
    sub_repo.add_sub(sub5)
    # Check function
    feed_list = sub_repo.get_subs_by_name(
        "http://spangle.org.uk/hallo/test_feed.xml?4", chan3
    )
    assert len(feed_list) == 2
    assert sub4 in feed_list
    assert sub5 in feed_list


def test_remove_feed(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    # Setup a feed list
    sub_repo = SubscriptionRepo(hallo)
    rf1 = RssSource(
        "http://spangle.org.uk/hallo/test_rss.xml?1", "title1"
    )
    sub1 = Subscription(test_server, test_channel, rf1, timedelta(days=1), None, None)
    sub_repo.add_sub(sub1)
    rf2 = RssSource(
        "http://spangle.org.uk/hallo/test_rss.xml?2", "title2"
    )
    sub2 = Subscription(test_server, test_channel, rf2, timedelta(days=1), None, None)
    sub_repo.add_sub(sub2)
    assert len(sub_repo.sub_list) == 2
    # Remove an item from the feed list
    sub_repo.remove_sub(sub1)
    assert len(sub_repo.sub_list) == 1
    assert sub_repo.sub_list[0] == sub2


def test_json(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    # Setup a feed list
    sub_repo = SubscriptionRepo(hallo)
    rf1 = RssSource(
        "http://spangle.org.uk/hallo/test_rss.xml?1",
        feed_title="test_feed1",
    )
    sub1 = Subscription(test_server, test_channel, rf1, timedelta(days=1), None, None)
    sub_repo.add_sub(sub1)
    rf2 = RssSource(
        "http://spangle.org.uk/hallo/test_rss.xml?2",
        feed_title="test_feed2",
    )
    sub2 = Subscription(test_server, test_user, rf2, timedelta(days=1), None, None)
    sub_repo.add_sub(sub2)
    rf3 = RssSource(
        "http://spangle.org.uk/hallo/test_rss.xml?3",
        feed_title="test_feed3",
    )
    sub3 = Subscription(test_server, test_channel, rf3, timedelta(hours=1), None, None)
    sub_repo.add_sub(sub3)
    # Save to JSON and load
    try:
        try:
            os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
        except OSError:
            pass
        sub_repo.save_json()
        new_rfl = SubscriptionRepo.load_json(hallo)
        assert len(new_rfl.sub_list) == 3
    finally:
        try:
            os.remove("store/subscriptions.json")
        except OSError:
            pass
        try:
            os.rename("store/subscriptions.json.tmp", "store/subscriptions.json")
        except OSError:
            pass
