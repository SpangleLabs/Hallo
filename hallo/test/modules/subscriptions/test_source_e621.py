import pytest

from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


def test_init():
    rf = E621Source("cabinet")
    keys = [
        "search",
        "last_keys"
    ]
    for key in keys:
        assert key in rf.__dict__, "Key is missing from E621Sub object: " + key


def test_matches_name():
    rf = E621Source("Cabinet ")

    assert rf.matches_name("cabinet")


def test_title():
    rf = E621Source("cabinet")

    assert "\"cabinet\"" in rf.title


def test_from_input(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo()

    rf = E621Source.from_input("cabinet", test_user, sub_repo)

    assert rf.search == "cabinet"


@pytest.mark.external_integration
def test_current_state():
    rf = E621Source("cabinet")

    state = rf.current_state()

    assert isinstance(state, list)
    assert len(state) > 0
    last_id = None
    for post in state:
        # Check tag is in tags
        assert "cabinet" in [x for v in post["tags"].values() for x in v]
        # Check id is decreasing
        if last_id is None:
            last_id = post["id"]
            continue
        assert last_id > post["id"]
        last_id = post["id"]


def test_item_to_key():
    rf = E621Source("cabinet")
    item = {"id": 1234, "rating": "s", "file": {"ext": "png", "url": "example.png"}}

    assert rf.item_to_key(item) == 1234


def test_item_to_event(hallo_getter):
    hallo, test_server, test_chat, test_user = hallo_getter({"subscriptions"})
    rf = E621Source("cabinet")
    item = {"id": 1234, "rating": "s", "file": {"ext": "png", "url": "example.png"}}

    event = rf.item_to_event(test_server, test_chat, None, item)

    assert isinstance(event, EventMessageWithPhoto)
    assert event.photo_id == "example.png"
    assert event.server == test_server
    assert event.channel == test_chat
    assert event.user is None
    assert "\"cabinet\"" in event.text
    assert "1234" in event.text
    assert "Safe" in event.text


def test_item_to_event__no_embed(hallo_getter):
    hallo, test_server, test_chat, test_user = hallo_getter({"subscriptions"})
    rf = E621Source("cabinet")
    item = {"id": 1234, "rating": "s", "file": {"ext": "swf", "url": "example.swf"}}

    event = rf.item_to_event(test_server, test_chat, None, item)

    assert isinstance(event, EventMessage)
    assert not isinstance(event, EventMessageWithPhoto)
    assert event.server == test_server
    assert event.channel == test_chat
    assert event.user is None
    assert "\"cabinet\"" in event.text
    assert "1234" in event.text
    assert "Safe" in event.text


def test_item_to_event__no_url(hallo_getter):
    hallo, test_server, test_chat, test_user = hallo_getter({"subscriptions"})
    rf = E621Source("cabinet")
    item = {"id": 1234, "rating": "s", "file": {"ext": "png", "url": None}}

    event = rf.item_to_event(test_server, test_chat, None, item)

    assert isinstance(event, EventMessage)
    assert not isinstance(event, EventMessageWithPhoto)
    assert event.server == test_server
    assert event.channel == test_chat
    assert event.user is None
    assert "\"cabinet\"" in event.text
    assert "1234" in event.text
    assert "Safe" in event.text


def test_json(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo()
    test_e621_search = "cabinet"
    # Create example source
    rf = E621Source(test_e621_search)
    rf.last_keys = [1234, 2345, 3456]
    # Save to json and load up new E621Sub
    rf_json = rf.to_json()

    assert "type" in rf_json
    assert "last_keys" in rf_json
    assert "search" in rf_json
    assert rf_json["type"] == E621Source.type_name

    rf2 = E621Source.from_json(rf_json, test_channel, sub_repo)

    assert rf2.search == test_e621_search
    assert rf2.last_keys == rf.last_keys
