import os

import pytest
from yippi import YippiClient

from hallo.events import EventMessage, EventMessageWithPhoto
from hallo.modules.subscriptions.source_e621_tagging import E621TaggingSource
import hallo.modules.subscriptions.subscription_exception
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.modules.user_data import E6KeyData


def test_init(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    rf = E621TaggingSource("cabinet", e6_client, sub_repo, test_hallo.test_user, ["table", "legs"])
    keys = [
        "search",
        "owner",
        "tags",
        "last_keys"
    ]
    for key in keys:
        assert key in rf.__dict__, "Key is missing from E621Sub object: " + key


def test_matches_name(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    rf = E621TaggingSource("Cabinet ", e6_client, sub_repo, test_hallo.test_user, ["table", "legs"])

    assert rf.matches_name("cabinet")


def test_title(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    rf = E621TaggingSource("cabinet", e6_client, sub_repo, test_hallo.test_user, ["table", "legs"])

    assert "\"cabinet\"" in rf.title


def test_from_input(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(test_hallo)
    test_hallo.test_user.extra_data_dict[E6KeyData.type_name] = E6KeyData("test_username", "test_api_key").to_json()

    rf = E621TaggingSource.from_input("cabinet tags=\"table legs\"", test_hallo.test_user, sub_repo)

    assert rf.search == "cabinet"
    assert rf.tags == ["table", "legs"]
    assert rf.e6_client._login == ("test_username", "test_api_key")


def test_from_input__no_user_data(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(test_hallo)

    with pytest.raises(hallo.modules.subscriptions.subscription_exception.SubscriptionException) as e:
        E621TaggingSource.from_input("cabinet tags=\"table legs\"", test_hallo.test_user, sub_repo)

    assert "you must specify an e621 username and api key" in str(e).lower()
    assert "setup e621 user data <username> <api_key>" in str(e).lower()


@pytest.mark.external_integration
def test_current_state(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    rf = E621TaggingSource("cabinet", e6_client, sub_repo, test_hallo.test_user, ["table", "legs"])

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
    sub_repo = SubscriptionRepo(test_hallo)
    rf = E621TaggingSource("cabinet", e6_client, sub_repo, test_hallo.test_user, ["table", "legs"])
    item = e6_client.post(1092773)

    assert rf.item_to_key(item) == 1092773


@pytest.mark.external_integration
def test_item_to_event(hallo_getter, tmp_path):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    sub_repo.MENU_STORE_FILE = tmp_path / "subscription_menus.json"
    sub_repo.load_menu_cache(test_hallo)
    rf = E621TaggingSource("chital", e6_client, sub_repo, test_hallo.test_user, ["deer-spangle", "fallow"])
    item = e6_client.post(1092773)

    event = rf.item_to_event(test_hallo.test_server, test_chat, None, item)

    assert isinstance(event, EventMessageWithPhoto)
    assert event.photo_id == "https://static1.e621.net/data/02/7e/027e18f9db1fd4906d98b987b202066e.png"
    assert event.server == test_hallo.test_server
    assert event.channel == test_chat
    assert event.user is None
    assert "\"chital\"" in event.text
    assert "1092773" in event.text
    assert "Safe" in event.text
    button_texts = [
        button.text
        for row in event.menu_buttons
        for button in row
    ]
    button_data = [
        button.data
        for row in event.menu_buttons
        for button in row
    ]
    assert "\u2714 deer-spangle" in button_texts
    assert "tag:deer-spangle" in button_data
    assert "\u274C fallow" in button_texts
    assert "tag:fallow" in button_data


@pytest.mark.external_integration
def test_item_to_event__no_embed(hallo_getter, tmp_path):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    sub_repo.MENU_STORE_FILE = tmp_path / "subscription_menus.json"
    sub_repo.load_menu_cache(test_hallo)
    rf = E621TaggingSource("acrobatics", e6_client, sub_repo, test_hallo.test_user, ["chital", "tirrel"])
    item = e6_client.post(257069)

    event = rf.item_to_event(test_hallo.test_server, test_chat, None, item)

    assert isinstance(event, EventMessage)
    assert not isinstance(event, EventMessageWithPhoto)
    assert event.server == test_hallo.test_server
    assert event.channel == test_chat
    assert event.user is None
    assert "\"acrobatics\"" in event.text
    assert "257069" in event.text
    assert "Safe" in event.text
    button_texts = [
        button.text
        for row in event.menu_buttons
        for button in row
    ]
    button_data = [
        button.data
        for row in event.menu_buttons
        for button in row
    ]
    assert "\u2714 tirrel" in button_texts
    assert "tag:tirrel" in button_data
    assert "\u274C chital" in button_texts
    assert "tag:chital" in button_data


def test_json(hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    test_e621_search = "cabinet"
    test_tags = ["table", "legs"]
    # Create example source
    rf = E621TaggingSource(test_e621_search, e6_client, sub_repo, test_hallo.test_user, test_tags)
    rf.last_keys = [1234, 2345, 3456]
    # Save to json and load up new E621Sub
    rf_json = rf.to_json()

    assert "type" in rf_json
    assert "last_keys" in rf_json
    assert "search" in rf_json
    assert "tags" in rf_json
    assert rf_json["type"] == E621TaggingSource.type_name

    rf2 = E621TaggingSource.from_json(rf_json, test_hallo.test_chan, sub_repo)

    assert rf2.search == test_e621_search
    assert rf2.last_keys == rf.last_keys
    assert rf2.tags == rf.tags
    assert rf2.owner == rf.owner
