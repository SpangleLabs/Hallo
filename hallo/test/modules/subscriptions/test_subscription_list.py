from datetime import timedelta

import pytest
from yippi import YippiClient

from hallo.events import EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.test.modules.subscriptions.mock_subscriptions import mock_sub_repo


def test_no_feeds(tmp_path, hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    mock_sub_repo(tmp_path, test_hallo)
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "e621 sub list")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert "no subscriptions" in data[0].text.lower(), "Actual response: {}".format(
        data[0].text
    )


@pytest.mark.external_integration
def test_list_feeds(tmp_path, hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    mock_sub_repo(tmp_path, test_hallo)
    another_chan = test_hallo.test_server.get_channel_by_address("another_channel")
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    # Get feed list
    rss_check_class = test_hallo.function_dispatcher.get_function_by_name(
        "check subscription"
    )
    rss_check_obj = test_hallo.function_dispatcher.get_function_object(
        rss_check_class
    )  # type: SubscriptionCheck
    rfl = rss_check_obj.get_sub_repo(test_hallo)
    # Add RSS feeds to feed list
    rf1 = E621Source("cabinet", e6_client, test_hallo.test_user)
    sub1 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf1, timedelta(days=1), None, None)
    rfl.add_sub(sub1)
    rf2 = E621Source("clefable", e6_client, test_hallo.test_user)
    sub2 = Subscription(test_hallo.test_server, another_chan, rf2, timedelta(days=1), None, None)
    rfl.add_sub(sub2)
    rf3 = E621Source("fez", e6_client, test_hallo.test_user)
    sub3 = Subscription(test_hallo.test_server, test_hallo.test_chan, rf3, timedelta(days=1), None, None)
    rfl.add_sub(sub3)
    # Run FeedList and check output
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "e621 sub list")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    data_split = data[0].text.split("\n")
    assert (
            "subscriptions posting" in data_split[0].lower()
    ), "Missing title. Response data: " + str(data[0].text)
    assert "cabinet" in data_split[1].lower() or "cabinet" in data_split[2].lower()
    assert (
            "clefable" not in data_split[1].lower()
            and "clefable" not in data_split[2].lower()
    )
    assert "fez" in data_split[1].lower() or "fez" in data_split[2].lower()
