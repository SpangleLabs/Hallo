import os

from inc.commons import Commons
from modules.subscriptions import SubscriptionRepo, RssSub
from test.server_mock import ServerMock


def test_init():
    rfl = SubscriptionRepo()
    assert rfl.sub_list == []


def test_add_feed(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    rfl = SubscriptionRepo()
    assert rfl.sub_list == []
    # Create example rss feed
    rf = RssSub(
        test_server,
        test_channel,
        "http://spangle.org.uk/hallo/test_rss.xml",
        update_frequency=Commons.load_time_delta("P0T3600S"),
    )
    rfl.add_sub(rf)
    assert len(rfl.sub_list) == 1
    assert rfl.sub_list[0] == rf


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
    rfl = SubscriptionRepo()
    rf1 = RssSub(chan1.server, chan1, "http://spangle.org.uk/hallo/test_rss.xml?1")
    rfl.add_sub(rf1)
    rf2 = RssSub(user2.server, user2, "http://spangle.org.uk/hallo/test_rss.xml?2")
    rfl.add_sub(rf2)
    rf3 = RssSub(chan3.server, chan3, "http://spangle.org.uk/hallo/test_rss.xml?3")
    rfl.add_sub(rf3)
    rf4 = RssSub(chan3.server, chan3, "http://spangle.org.uk/hallo/test_rss.xml?4")
    rfl.add_sub(rf4)
    rf5 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_rss.xml?5",
        title="test_feed3",
    )
    rfl.add_sub(rf5)
    # Check function
    feed_list = rfl.get_subs_by_destination(chan3)
    assert len(feed_list) == 3
    assert rf4 in feed_list
    assert rf3 in feed_list
    assert rf5 in feed_list


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
    rfl = SubscriptionRepo()
    rf1 = RssSub(
        chan1.server,
        chan1,
        "http://spangle.org.uk/hallo/test_feed.xml?1",
        title="test_feed1",
    )
    rfl.add_sub(rf1)
    rf2 = RssSub(
        user2.server,
        user2,
        "http://spangle.org.uk/hallo/test_feed.xml?2",
        title="test_feed2",
    )
    rfl.add_sub(rf2)
    rf3 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_feed.xml?3",
        title="test_feed3",
    )
    rfl.add_sub(rf3)
    rf4 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_feed.xml?4",
        title="test_feed4",
    )
    rfl.add_sub(rf4)
    rf5 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_feed.xml?5",
        title="test_feed3",
    )
    rfl.add_sub(rf5)
    # Check function
    feed_list = rfl.get_subs_by_name("test_feed3", chan3)
    assert len(feed_list) == 2
    assert rf3 in feed_list
    assert rf5 in feed_list


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
    rfl = SubscriptionRepo()
    rf1 = RssSub(
        chan1.server,
        chan1,
        "http://spangle.org.uk/hallo/test_feed.xml?1",
        title="test_feed1",
    )
    rfl.add_sub(rf1)
    rf2 = RssSub(
        user2.server,
        user2,
        "http://spangle.org.uk/hallo/test_feed.xml?2",
        title="test_feed2",
    )
    rfl.add_sub(rf2)
    rf3 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_feed.xml?3",
        title="test_feed3",
    )
    rfl.add_sub(rf3)
    rf4 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_feed.xml?4",
        title="test_feed4",
    )
    rfl.add_sub(rf4)
    rf5 = RssSub(
        chan3.server,
        chan3,
        "http://spangle.org.uk/hallo/test_feed.xml?4",
        title="test_feed3",
    )
    rfl.add_sub(rf5)
    # Check function
    feed_list = rfl.get_subs_by_name(
        "http://spangle.org.uk/hallo/test_feed.xml?4", chan3
    )
    assert len(feed_list) == 2
    assert rf4 in feed_list
    assert rf5 in feed_list


def test_remove_feed(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    # Setup a feed list
    rfl = SubscriptionRepo()
    rf1 = RssSub(
        test_server, test_channel, "http://spangle.org.uk/hallo/test_rss.xml?1"
    )
    rfl.add_sub(rf1)
    rf2 = RssSub(
        test_server, test_channel, "http://spangle.org.uk/hallo/test_rss.xml?2"
    )
    rfl.add_sub(rf2)
    assert len(rfl.sub_list) == 2
    # Remove an item from the feed list
    rfl.remove_sub(rf1)
    assert len(rfl.sub_list) == 1
    assert rfl.sub_list[0] == rf2


def test_json(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    # Setup a feed list
    rfl = SubscriptionRepo()
    rf1 = RssSub(
        test_server,
        test_channel,
        "http://spangle.org.uk/hallo/test_rss.xml?1",
        title="test_feed1",
        update_frequency=Commons.load_time_delta("P0T3600S"),
    )
    rfl.add_sub(rf1)
    rf2 = RssSub(
        test_server,
        test_channel,
        "http://spangle.org.uk/hallo/test_rss.xml?2",
        title="test_feed2",
        update_frequency=Commons.load_time_delta("P1TS"),
    )
    rfl.add_sub(rf2)
    rf3 = RssSub(
        test_server,
        test_channel,
        "http://spangle.org.uk/hallo/test_rss.xml?3",
        title="test_feed3",
        update_frequency=Commons.load_time_delta("PT60S"),
    )
    rfl.add_sub(rf3)
    # Save to JSON and load
    try:
        try:
            os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
        except OSError:
            pass
        rfl.save_json()
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
