from datetime import timedelta
from unittest.mock import Mock

from yippi import YippiClient

from hallo.events import EventMinute, EventMessage
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription import Subscription
from hallo.modules.subscriptions.subscription_check import SubscriptionCheck
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.server_mock import ServerMock


def test_run_all(tmp_path, hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menus.json"
    # Set up test servers and channels
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    user1 = serv1.get_user_by_address("test_user1".lower(), "test_user1")
    serv2 = ServerMock(test_hallo)
    serv2.name = "test_serv2"
    chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user2 = serv2.get_user_by_address("test_user2".lower(), "test_user2")
    try:
        test_hallo.add_server(serv1)
        test_hallo.add_server(serv2)
        # Set up rss feeds
        sub_repo = SubscriptionRepo(test_hallo)
        rf1 = E621Source("cabinet", e6_client, user1)
        sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
        sub_repo.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, user1)
        sub2 = Subscription(serv1, chan2, rf2, timedelta(days=1), None, None)
        sub_repo.add_sub(sub2)
        rf3 = E621Source("fez", e6_client, user2)
        sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
        sub_repo.add_sub(sub3)
        # Splice this rss feed list into the function dispatcher's rss check object
        e621_sub_check = test_hallo.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        e621_sub_obj = test_hallo.function_dispatcher.get_function_object(
            e621_sub_check
        )  # type: SubscriptionCheck
        e621_sub_obj.subscription_repo = sub_repo
        # Test running all feed updates
        test_hallo.function_dispatcher.dispatch(
            EventMessage(
                test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "e621 sub check all"
            )
        )
        # Check original calling channel data
        serv0_data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
        assert (
                "subscription updates were found" in serv0_data[0].text.lower()
        ), "Actual message: {}".format(serv0_data[0].text)
        # Check test server 1 data
        serv1_data = serv1.get_send_data(150)
        chan1_count = 0
        chan2_count = 0
        for data_line in serv1_data:
            if data_line.channel == chan1:
                chan1_count += 1
            if data_line.channel == chan2:
                chan2_count += 1
        assert chan1_count == 75
        assert chan2_count == 75
        # Check test server 2 data
        serv2.get_send_data(75, chan3, EventMessage)
        # Test running with no new updates.
        test_hallo.function_dispatcher.dispatch(
            EventMessage(
                test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "e621 sub check all"
            )
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
        assert "no updates" in data[0].text, "No further updates should be found."
    finally:
        test_hallo.remove_server(serv2)
        test_hallo.remove_server(serv1)


def test_run_by_search(tmp_path, hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menus.json"
    # Set up test servers and channels
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    user1 = serv1.get_user_by_address("test_user1", "test_user1")
    serv2 = ServerMock(test_hallo)
    serv2.name = "test_serv2"
    chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user2 = serv2.get_user_by_address("test_user2", "test_user2")
    try:
        test_hallo.add_server(serv1)
        test_hallo.add_server(serv2)
        # Set up rss feeds
        sub_repo = SubscriptionRepo(test_hallo)
        rf1 = E621Source("cabinet", e6_client, user1)
        sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
        sub_repo.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, user1)
        sub2 = Subscription(serv1, chan2, rf2, timedelta(days=1), None, None)
        sub_repo.add_sub(sub2)
        rf3 = E621Source("fez", e6_client, user2)
        sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
        sub_repo.add_sub(sub3)
        # Splice this rss feed list into the function dispatcher's rss check object
        rss_check_class = test_hallo.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        rss_check_obj = test_hallo.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rss_check_obj.subscription_repo = sub_repo
        # Invalid title
        test_hallo.function_dispatcher.dispatch(
            EventMessage(
                test_hallo.test_server,
                test_hallo.test_chan,
                test_hallo.test_user,
                "e621 sub check Not a valid search",
            )
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
        assert "error" in data[0].text.lower()
        # Correct title but wrong channel
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan1, user1, "e621 sub check clefable")
        )
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert "error" in data[0].text.lower()
        # Correct title check update
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan2, user1, "e621 sub check clefable")
        )
        data = serv1.get_send_data(76, chan2, EventMessage)
        has_photo_id = 0
        for x in range(75):
            assert "update on" in data[x].text.lower()
            if hasattr(data[x], "photo_id") and data[x].photo_id is not None:
                has_photo_id += 1
            assert "clefable" in data[x].text
        assert has_photo_id > 40, "Almost all subscription updates should have a photo"
        assert (
                "subscription updates were found" in data[75].text.lower()
        ), "Actual message: {}".format(data[0].text)
        # No updates
        test_hallo.function_dispatcher.dispatch(
            EventMessage(serv1, chan2, user1, "e621 sub check clefable")
        )
        data = serv1.get_send_data(1, chan2, EventMessage)
        assert "no updates" in data[0].text, "No further updates should be found."
    finally:
        test_hallo.remove_server(serv2)
        test_hallo.remove_server(serv1)


def test_run_passive(tmp_path, hallo_getter):
    test_hallo = hallo_getter({"subscriptions"})
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menus.json"
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    # Set up test servers and channels
    serv1 = ServerMock(test_hallo)
    serv1.name = "test_serv1"
    chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
    chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
    user1 = serv1.get_user_by_address("test_user1", "test_user2")
    serv2 = ServerMock(test_hallo)
    serv2.name = "test_serv2"
    chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
    user2 = serv2.get_user_by_address("test_user2", "test_user2")
    try:
        test_hallo.add_server(serv1)
        test_hallo.add_server(serv2)
        # Set up rss feeds
        sub_repo = SubscriptionRepo(test_hallo)
        rf1 = E621Source("cabinet", e6_client, user1)
        sub1 = Subscription(serv1, chan1, rf1, timedelta(days=1), None, None)
        sub_repo.add_sub(sub1)
        rf2 = E621Source("clefable", e6_client, user1)
        sub2 = Subscription(serv1, chan2, rf2, timedelta(days=1), None, None)
        sub_repo.add_sub(sub2)
        rf3 = E621Source("fez", e6_client, user2)
        sub3 = Subscription(serv2, chan3, rf3, timedelta(days=1), None, None)
        sub_repo.add_sub(sub3)
        # Splice this rss feed list into the function dispatcher's rss check object
        rss_check_class = test_hallo.function_dispatcher.get_function_by_name(
            "check subscription"
        )
        rss_check_obj = test_hallo.function_dispatcher.get_function_object(
            rss_check_class
        )  # type: SubscriptionCheck
        rss_check_obj.subscription_repo = sub_repo
        # Test passive feed updates
        test_hallo.function_dispatcher.dispatch_passive(EventMinute())
        # Check test server 1 data
        serv1_data = serv1.get_send_data(150)
        chan1_count = 0
        chan2_count = 0
        for data_line in serv1_data:
            if data_line.channel == chan1:
                chan1_count += 1
            if data_line.channel == chan2:
                chan2_count += 1
        assert chan1_count == 75
        assert chan2_count == 75
        # Check test server 2 data
        serv2.get_send_data(75, chan3, EventMessage)
        # Test that no updates are found the second run
        rf1.last_check = None
        rf2.last_check = None
        rf3.last_check = None
        test_hallo.function_dispatcher.dispatch_passive(EventMinute())
        serv1.get_send_data(0)
        serv2.get_send_data(0)
        # Test that no feeds are checked before timeout, set urls to none and see if anything explodes.
        rf1.check_feed = Mock()
        rf2.check_feed = Mock()
        rf3.check_feed = Mock()
        test_hallo.function_dispatcher.dispatch_passive(EventMinute())
        serv1.get_send_data(0)
        serv2.get_send_data(0)
        rf1.check_feed.assert_not_called()
        rf2.check_feed.assert_not_called()
        rf3.check_feed.assert_not_called()
    finally:
        test_hallo.remove_server(serv2)
        test_hallo.remove_server(serv1)


def do_not_call(self):
    self.failed = True
    return []
