from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


def test_invalid_subscription(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "rss sub add ::")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert (
            "error" in data[0].text.lower()
    ), "No error in response. Response was: {}".format(data[0].text)


def test_add_search(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "e621 sub add cabinet"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert (
            "created a new e621 subscription" in data[0].text.lower()
    ), "Actual response: {}".format(data[0].text)
    # Check the search subscription was added
    e621_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "e621 sub check"
    )
    e621_check_obj = test_hallo.function_dispatcher.get_function_object(
        e621_check_class
    )  # type: SubscriptionCheck
    sub_repo = e621_check_obj.get_sub_repo(test_hallo).sub_list
    assert len(sub_repo) == 1, "Actual length: " + str(len(sub_repo))
    e6_sub: Subscription = sub_repo[0]
    assert e6_sub.server == test_hallo.test_server
    assert e6_sub.destination == test_hallo.test_chan
    assert e6_sub.last_check is not None
    assert e6_sub.last_update is None
    assert e6_sub.period.seconds == 600
    assert e6_sub.period.days == 0
    assert e6_sub.source.type_name == E621Source.type_name
    assert e6_sub.source.search == "cabinet"
    assert e6_sub.source.last_keys is not None
    assert len(e6_sub.source.last_keys) >= 50


def test_add_search_user(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "e621 sub add cabinet")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
            "created a new e621 subscription" in data[0].text.lower()
    ), "Actual response: {}".format(data[0].text)
    # Check the search subscription was added
    e621_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "e621 sub check"
    )
    e621_check_obj = test_hallo.function_dispatcher.get_function_object(
        e621_check_class
    )  # type: SubscriptionCheck
    sub_repo = e621_check_obj.get_sub_repo(test_hallo).sub_list
    assert len(sub_repo) == 1, "Actual length: " + str(len(sub_repo))
    e6_sub: Subscription = sub_repo[0]
    assert e6_sub.server == test_hallo.test_server
    assert e6_sub.destination == test_hallo.test_user
    assert e6_sub.last_check is not None
    assert e6_sub.last_update is None
    assert e6_sub.period.seconds == 600
    assert e6_sub.period.days == 0
    assert e6_sub.source.type_name == E621Source.type_name
    assert e6_sub.source.search == "cabinet"
    assert e6_sub.source.last_keys is not None
    assert len(e6_sub.source.last_keys) >= 50


def test_add_search_period(tmp_path, hallo_getter):
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menu.json"
    test_hallo = hallo_getter({"subscriptions"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            test_hallo.test_chan,
            test_hallo.test_user,
            "e621 sub add cabinet PT3600S",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert (
            "created a new e621 subscription" in data[0].text.lower()
    ), "Actual response: {}".format(data[0].text)
    # Check the search subscription was added
    e621_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "e621 sub check"
    )
    e621_check_obj = test_hallo.function_dispatcher.get_function_object(
        e621_check_class
    )  # type: SubscriptionCheck
    sub_repo = e621_check_obj.get_sub_repo(test_hallo).sub_list
    assert len(sub_repo) == 1, "Actual length: " + str(len(sub_repo))
    e6_sub: Subscription = sub_repo[0]
    assert e6_sub.server == test_hallo.test_server
    assert e6_sub.destination == test_hallo.test_chan
    assert e6_sub.last_check is not None
    assert e6_sub.last_update is None
    assert e6_sub.period.seconds == 3600
    assert e6_sub.period.days == 0
    assert e6_sub.source.type_name == E621Source.type_name
    assert e6_sub.source.search == "cabinet"
    assert e6_sub.source.last_keys is not None
    assert len(e6_sub.source.last_keys) >= 50
