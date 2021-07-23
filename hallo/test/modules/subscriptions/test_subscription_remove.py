from datetime import timedelta

from yippi import YippiClient

from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


def test_remove_by_search(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    another_chan = test_hallo.test_server.get_channel_by_address("another_channel")
    # Get subscription list
    e621_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "check subscription"
    )
    e621_check_obj = test_hallo.function_dispatcher.get_function_object(
        e621_check_class
    )  # type: SubscriptionCheck
    sub_repo = e621_check_obj.get_sub_repo(test_hallo)
    # Add E621 searches to subscription list
    rf1 = E621Source("cabinet", e6_client, test_hallo.test_zser)
    sub1 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf1, timedelta(days=1), None, None)
    sub_repo.add_sub(sub1)
    rf2 = E621Source("clefable", e6_client, test_hallo.test_zser)
    sub2 = Subscription(test_hallo.test_server, another_chan, rf2, timedelta(days=1), None, None)
    sub_repo.add_sub(sub2)
    rf3 = E621Source("fez", e6_client, test_hallo.test_zser)
    sub3 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf3, timedelta(days=1), None, None)
    sub_repo.add_sub(sub3)
    # Remove test search
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_zser, "e621 sub remove cabinet"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "removed subscription" in data[0].text.lower()
    assert "e621" in data[0].text.lower()
    assert "\"cabinet\"" in data[0].text.lower()
    assert sub1 not in sub_repo.sub_list
    assert sub2 in sub_repo.sub_list
    assert sub3 in sub_repo.sub_list


def test_remove_multiple_matching_searches(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    another_chan = test_hallo.test_server.get_channel_by_address("another_channel")
    # Get subscription list
    e621_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "check subscription"
    )
    e621_check_obj = test_hallo.function_dispatcher.get_function_object(
        e621_check_class
    )  # type: SubscriptionCheck
    rfl = e621_check_obj.get_sub_repo(test_hallo)
    # Add E621 searches to subscription list
    rf1 = E621Source("cabinet", e6_client, test_hallo.test_zser)
    sub1 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf1, timedelta(days=1), None, None)
    rfl.add_sub(sub1)
    rf2 = E621Source("clefable", e6_client, test_hallo.test_zser)
    sub2 = Subscription(test_hallo.test_server, another_chan, rf2, timedelta(days=1), None, None)
    rfl.add_sub(sub2)
    rf3 = E621Source("cabinet", e6_client, test_hallo.test_zser)
    sub3 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf3, timedelta(days=1), None, None)
    rfl.add_sub(sub3)
    # Remove test feed
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_zser, "e621 sub remove cabinet"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert (
            "removed 2 subscriptions" in data[0].text.lower()
    ), "Response did not contain expected string. Response was {}".format(
        data[0].text
    )
    assert (
            "cabinet" in data[0].text.lower()
    ), "Response did not contain expected string. Response was {}".format(
        data[0].text
    )
    assert (
            "e621" in data[0].text.lower()
    ), "Response did not contain expected string. Response was {}".format(
        data[0].text
    )
    assert sub1 not in rfl.sub_list
    assert sub2 in rfl.sub_list
    assert sub3 not in rfl.sub_list


def test_remove_no_match(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    another_chan = test_hallo.test_server.get_channel_by_address("another_channel")
    # Get subscription list
    e621_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "check subscription"
    )
    e621_check_obj = test_hallo.function_dispatcher.get_function_object(
        e621_check_class
    )  # type: SubscriptionCheck
    sub_repo = e621_check_obj.get_sub_repo(test_hallo)
    # Add E621 searches to subscription list
    rf1 = E621Source("cabinet", e6_client, test_hallo.test_zser)
    sub1 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf1, timedelta(days=1), None, None)
    sub_repo.add_sub(sub1)
    rf2 = E621Source("clefable", e6_client, test_hallo.test_zser)
    sub2 = Subscription(test_hallo.test_server, another_chan, rf2, timedelta(days=1), None, None)
    sub_repo.add_sub(sub2)
    rf3 = E621Source("fez", e6_client, test_hallo.test_zser)
    sub3 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf3, timedelta(days=1), None, None)
    sub_repo.add_sub(sub3)
    # Try to remove invalid search
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_zser,
            "e621 sub remove not_a_search",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "error" in data[0].text.lower()
    assert sub1 in sub_repo.sub_list
    assert sub2 in sub_repo.sub_list
    assert sub3 in sub_repo.sub_list
