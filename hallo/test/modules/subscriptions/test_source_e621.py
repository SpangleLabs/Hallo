import pytest
from yippi import YippiClient

from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


def test_init(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("cabinet", e6_client, test_hallo.test_user)
    keys = [
        "search",
        "last_keys"
    ]
    for key in keys:
        assert key in rf.__dict__, "Key is missing from E621Sub object: " + key


def test_matches_name(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("Cabinet ", e6_client, test_hallo.test_user)

    assert rf.matches_name("cabinet")


def test_title(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("cabinet", e6_client, test_hallo.test_user)

    assert "\"cabinet\"" in rf.title


def test_from_input(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(test_hallo)

    rf = E621Source.from_input("cabinet", test_hallo.test_user, sub_repo)

    assert rf.search == "cabinet"


@pytest.mark.external_integration
def test_current_state(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("cabinet", e6_client, test_hallo.test_user)

    state = rf.current_state()

    assert isinstance(state, list)
    assert len(state) > 0
    last_id = None
    for post in state:
        # Check tag is in tags
        assert "cabinet" in [x for v in post.tags.values() for x in v]
        # Check id is decreasing
        if last_id is None:
            last_id = post.id
            continue
        assert last_id > post.id
        last_id = post.id


@pytest.mark.external_integration
def test_item_to_key(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("cabinet", e6_client, test_hallo.test_user)
    item = e6_client.post(1092773)

    assert rf.item_to_key(item) == 1092773


@pytest.mark.external_integration
def test_item_to_event(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("chital", e6_client, test_hallo.test_user)
    item = e6_client.post(1092773)

    event = rf.item_to_event(test_hallo.test_server, test_hallo.test_chan, None, item)

    assert isinstance(event, EventMessageWithPhoto)
    assert event.photo_id == "https://static1.e621.net/data/02/7e/027e18f9db1fd4906d98b987b202066e.png"
    assert event.server == test_hallo.test_server
    assert event.channel == test_hallo.test_chan
    assert event.user is None
    assert "\"chital\"" in event.text
    assert "1092773" in event.text
    assert "Safe" in event.text


@pytest.mark.external_integration
def test_item_to_event__no_embed(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    rf = E621Source("acrobatics", e6_client, test_hallo.test_user)
    item = e6_client.post(257069)

    event = rf.item_to_event(test_hallo.test_server, test_hallo.test_chan, None, item)

    assert isinstance(event, EventMessage)
    assert not isinstance(event, EventMessageWithPhoto)
    assert event.server == test_hallo.test_server
    assert event.channel == test_hallo.test_chan
    assert event.user is None
    assert "\"acrobatics\"" in event.text
    assert "257069" in event.text
    assert "Safe" in event.text


def test_json(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    test_e621_search = "cabinet"
    # Create example source
    rf = E621Source(test_e621_search, e6_client, test_hallo.test_user)
    rf.last_keys = [1234, 2345, 3456]
    # Save to json and load up new E621Sub
    rf_json = rf.to_json()

    assert "type" in rf_json
    assert "last_keys" in rf_json
    assert "search" in rf_json
    assert rf_json["type"] == E621Source.type_name

    rf2 = E621Source.from_json(rf_json, test_hallo.test_chan, sub_repo)

    assert rf2.search == test_e621_search
    assert rf2.last_keys == rf.last_keys
    assert rf2.owner == rf.owner
