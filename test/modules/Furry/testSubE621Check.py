import os
import unittest

from Events import EventMinute, EventMessage
from inc.Commons import Commons
from modules.Furry import SubE621Check, E621SubList, E621Sub
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class SubE621CheckTest(TestBase, unittest.TestCase):

    def setUp(self):
        try:
            os.rename("store/e621_subscriptions.json", "store/e621_subscriptions.json.tmp")
        except OSError:
            pass
        super().setUp()

    def tearDown(self):
        super().tearDown()
        try:
            os.remove("store/e621_subscriptions.json")
        except OSError:
            pass
        try:
            os.rename("store/e621_subscriptions.json.tmp", "store/e621_subscriptions.json")
        except OSError:
            pass

    def test_init(self):
        try:
            try:
                os.rename("store/e621_subscriptions.json", "store/e621_subscriptions.json.tmp")
            except OSError:
                pass
            fc = SubE621Check()
            assert fc.e621_sub_list is not None
            assert fc.e621_sub_list.sub_list == []
        finally:
            try:
                os.rename("store/e621_subscriptions.json.tmp", "store/e621_subscriptions.json")
            except OSError:
                pass

    def test_save_function(self):
        fc = SubE621Check()
        # Mock out the rss feed list
        mfl = MockSubList()
        fc.e621_sub_list = mfl
        fc.save_function()
        assert mfl.save_json_called

    def test_run_all(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = E621SubList()
            rf1 = E621Sub()
            rf1.search = "cabinet"
            rf1.server_name = chan1.server.name
            rf1.channel_address = chan1.address
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf1)
            rf2 = E621Sub()
            rf2.search = "clefable"
            rf2.server_name = chan2.server.name
            rf2.channel_address = chan2.address
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf2)
            rf3 = E621Sub()
            rf3.search = "fez"
            rf3.server_name = chan3.server.name
            rf3.channel_address = chan3.address
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            e621_sub_check = self.function_dispatcher.get_function_by_name("e621 sub check")
            e621_sub_obj = self.function_dispatcher.get_function_object(e621_sub_check)  # type: SubE621Check
            e621_sub_obj.e621_sub_list = rfl
            # Test running all feed updates
            self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                           "e621 sub check all"))
            # Check original calling channel data
            serv0_data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "search updates were found" in serv0_data[0].text
            # Check test server 1 data
            serv1_data = serv1.get_send_data(100)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line.channel == chan1:
                    chan1_count += 1
                if data_line.channel == chan2:
                    chan2_count += 1
            assert chan1_count == 50
            assert chan2_count == 50
            # Check test server 2 data
            serv2_data = serv2.get_send_data(50, chan3, EventMessage)
            # Test running with no new updates.
            self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                           "e621 sub check all"))
            data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "no e621 search subscription updates" in data[0].text, "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_by_search(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        user1 = serv1.get_user_by_address("test_user1", "test_user1")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = E621SubList()
            rf1 = E621Sub()
            rf1.search = "cabinet"
            rf1.server_name = chan1.server.name
            rf1.channel_address = chan1.address
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf1)
            rf2 = E621Sub()
            rf2.search = "clefable"
            rf2.server_name = chan2.server.name
            rf2.channel_address = chan2.address
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf2)
            rf3 = E621Sub()
            rf3.search = "fez"
            rf3.server_name = chan3.server.name
            rf3.channel_address = chan3.address
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubE621Check
            rss_check_obj.e621_sub_list = rfl
            # Invalid title
            self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                           "e621 sub check Not a valid search"))
            data = self.server.get_send_data(1, self.test_chan, EventMessage)
            assert "error" in data[0].text.lower()
            # Correct title but wrong channel
            self.function_dispatcher.dispatch(EventMessage(serv1, chan1, user1,
                                                           "e621 sub check clefable"))
            data = serv1.get_send_data(1, chan1, EventMessage)
            assert "error" in data[0].text.lower()
            # Correct title check update
            self.function_dispatcher.dispatch(EventMessage(serv1, chan2, user1,
                                                           "e621 sub check clefable"))
            data = serv1.get_send_data(1, chan2, EventMessage)
            assert "search updates were found" in data[0].text.lower()
            assert len(data[0].text.lower().split("\n")) == 51
            # No updates
            self.function_dispatcher.dispatch(EventMessage(serv1, chan2, user1,
                                                           "e621 sub check clefable"))
            data = serv1.get_send_data(1, chan2, EventMessage)
            assert "no updates" in data[0].text, "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_passive(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        chan2 = serv1.get_channel_by_address("test_chan2".lower(), "test_chan2")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_address("test_chan1".lower(), "test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = E621SubList()
            rf1 = E621Sub()
            rf1.search = "cabinet"
            rf1.server_name = chan1.server.name
            rf1.channel_address = chan1.address
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf1)
            rf2 = E621Sub()
            rf2.search = "clefable"
            rf2.server_name = chan2.server.name
            rf2.channel_address = chan2.address
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf2)
            rf3 = E621Sub()
            rf3.search = "fez"
            rf3.server_name = chan3.server.name
            rf3.channel_address = chan3.address
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubE621Check
            rss_check_obj.e621_sub_list = rfl
            # Test passive feed updates
            self.function_dispatcher.dispatch_passive(EventMinute())
            # Check test server 1 data
            serv1_data = serv1.get_send_data(100)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line.channel == chan1:
                    chan1_count += 1
                if data_line.channel == chan2:
                    chan2_count += 1
            assert chan1_count == 50
            assert chan2_count == 50
            # Check test server 2 data
            serv2_data = serv2.get_send_data(50, chan3, EventMessage)
            # Test that no updates are found the second run
            rf1.last_check = None
            rf2.last_check = None
            rf3.last_check = None
            self.function_dispatcher.dispatch_passive(EventMinute())
            serv1.get_send_data(0)
            serv2.get_send_data(0)
            # Test that no feeds are checked before timeout, set urls to none and see if anything explodes.
            self.failed = False
            rf1.check_feed = self.do_not_call
            rf2.check_feed = self.do_not_call
            rf3.check_feed = self.do_not_call
            self.function_dispatcher.dispatch_passive(EventMinute())
            serv1.get_send_data(0)
            serv2.get_send_data(0)
            assert not self.failed, "check_feed() should not have been called on any feed."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def do_not_call(self):
        self.failed = True
        return []


class MockSubList:

    def __init__(self):
        self.save_json_called = False

    def save_json(self):
        self.save_json_called = True
