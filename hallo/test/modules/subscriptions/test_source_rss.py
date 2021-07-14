from xml.etree import ElementTree

import pytest

from hallo.modules.subscriptions.source_rss import RssSource
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo

TEST_RSS = "http://spangle.org.uk/hallo/test_rss.xml"


@pytest.mark.external_integration
def test_init():
    rf = RssSource(TEST_RSS)
    keys = [
        "feed_title",
        "url",
        "last_keys",
    ]
    for key in keys:
        assert key in rf.__dict__, "Key is missing from RssFeed object: " + key


def test_init__with_name():
    # Ensure it doesn't call somewhere, by giving a fake url
    rf = RssSource("example.rss", "feed title")
    keys = [
        "feed_title",
        "url",
        "last_keys",
    ]
    for key in keys:
        assert key in rf.__dict__, "Key is missing from RssFeed object: " + key


def test_matches_name():
    rf = RssSource(TEST_RSS)

    assert rf.matches_name(TEST_RSS)
    assert rf.matches_name("example rss feed")


def test_title():
    rf = RssSource(TEST_RSS)

    assert TEST_RSS in rf.title
    assert "Example rss feed" in rf.title


def test_from_input(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(hallo)

    rf = RssSource.from_input(TEST_RSS, test_user, sub_repo)

    assert rf.url == TEST_RSS
    assert rf.feed_title == "Example rss feed"


@pytest.mark.external_integration
def test_current_state():
    rf = RssSource(TEST_RSS)

    state = rf.current_state()

    assert isinstance(state, list)
    assert len(state) == 3
    assert isinstance(state[0], ElementTree.Element)
    assert state[0].find("title").text == "Item 3"
    assert state[0].find("link").text == "http://example.com/item3"


def test_item_to_key():
    rss_data = (
        """<item>
            <guid>GUID1234</guid>
            <title>Item title</title>
            <link>http://example.com/item</link>
        </item>"""
    )
    rss_elem = ElementTree.fromstring(rss_data)
    rf = RssSource(TEST_RSS)

    assert rf.item_to_key(rss_elem) == "GUID1234"


def test_item_to_key__no_guid():
    rss_data = (
        """<item>
            <title>Item title</title>
            <link>http://example.com/item</link>
        </item>"""
    )
    rss_elem = ElementTree.fromstring(rss_data)
    rf = RssSource(TEST_RSS)

    assert rf.item_to_key(rss_elem) == "http://example.com/item"


def test_item_to_key__no_guid_or_link():
    rss_data = (
        """<item>
            <title>Item title</title>
        </item>"""
    )
    rss_elem = ElementTree.fromstring(rss_data)
    rf = RssSource(TEST_RSS)

    assert rf.item_to_key(rss_elem) != "Item title"

    key1 = rf.item_to_key(rss_elem)
    key2 = rf.item_to_key(rss_elem)

    assert key1 == key2


def test_item_to_event(hallo_getter):
    hallo, test_server, test_chat, test_user = hallo_getter({"subscriptions"})
    rf = RssSource(TEST_RSS, "feed title")
    rss_data = (
        """<item>
            <title>Item title</title>
            <link>http://example.com/item</link>
        </item>"""
    )
    rss_elem = ElementTree.fromstring(rss_data)

    event = rf.item_to_event(test_server, test_chat, None, rss_elem)

    assert event.server == test_server
    assert event.channel == test_chat
    assert event.user is None
    assert "\"feed title\"" in event.text
    assert "Item title" in event.text
    assert "http://example.com/item" in event.text


def test_json(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(hallo)
    rf = RssSource(TEST_RSS)
    rf.last_keys = ["item3", "item2", "item1"]

    rf_json = rf.to_json()

    assert "type" in rf_json
    assert "last_keys" in rf_json
    assert "url" in rf_json
    assert "title" in rf_json

    rf2 = RssSource.from_json(rf_json, test_channel, sub_repo)

    assert rf2.url == TEST_RSS
    assert rf2.feed_title == rf.feed_title
    assert rf2.last_keys == rf.last_keys
