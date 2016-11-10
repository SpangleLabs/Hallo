import os
import unittest

from Function import Function
from Server import Server
from inc.Commons import Commons
from modules.Furry import SubE621Check, E621SubList, E621Sub
from modules.Rss import FeedCheck, RssFeedList, RssFeed
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class SubE621CheckTest(TestBase, unittest.TestCase):

    def test_init(self):
        try:
            try:
                os.rename("store/e621_subscriptions.xml", "store/e621_subscriptions.xml.tmp")
            except OSError:
                pass
            fc = SubE621Check()
            assert fc.e621_sub_list is not None
            assert fc.e621_sub_list.sub_list == []
        finally:
            try:
                os.rename("store/e621_subscriptions.xml.tmp", "store/e621_subscriptions.xml")
            except OSError:
                pass

    def test_save_function(self):
        fc = SubE621Check()
        # Mock out the rss feed list
        mfl = MockSubList()
        fc.e621_sub_list = mfl
        fc.save_function()
        assert mfl.to_xml_called

    def test_run_all(self):
        # Set up test servers and channels
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan2 = serv1.get_channel_by_name("test_chan2")
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_name("test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = E621SubList()
            rf1 = E621Sub()
            rf1.search = "butt"
            rf1.server_name = chan1.server.name
            rf1.channel_name = chan1.name
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf1)
            rf2 = E621Sub()
            rf2.search = "deer"
            rf2.server_name = chan2.server.name
            rf2.channel_name = chan2.name
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf2)
            rf3 = E621Sub()
            rf3.search = "dragon"
            rf3.server_name = chan3.server.name
            rf3.channel_name = chan3.name
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            e621_sub_check = self.function_dispatcher.get_function_by_name("e621 sub check")
            e621_sub_obj = self.function_dispatcher.get_function_object(e621_sub_check)  # type: SubE621Check
            e621_sub_obj.e621_sub_list = rfl
            # Test running all feed updates
            self.function_dispatcher.dispatch("e621 sub check all", self.test_user, self.test_chan)
            # Check original calling channel data
            serv0_data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "search updates were found" in serv0_data[0][0]
            # Check test server 1 data
            serv1_data = serv1.get_send_data(100)
            chan1_count = 0
            chan2_count = 0
            for data_line in serv1_data:
                if data_line[1] == chan1:
                    chan1_count += 1
                if data_line[1] == chan2:
                    chan2_count += 1
            assert chan1_count == 50
            assert chan2_count == 50
            # Check test server 2 data
            serv2_data = serv2.get_send_data(50, chan3, Server.MSG_MSG)
            # Test running with no new updates.
            self.function_dispatcher.dispatch("e621 sub check all", self.test_user, self.test_chan)
            data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "no e621 search subscription updates" in data[0][0], "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    def test_run_by_search(self):
        # Set up test servers and channels
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_name("test_chan1")
        chan2 = serv1.get_channel_by_name("test_chan2")
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        chan3 = serv2.get_channel_by_name("test_chan1")
        try:
            self.hallo.add_server(serv1)
            self.hallo.add_server(serv2)
            # Set up rss feeds
            rfl = E621SubList()
            rf1 = E621Sub()
            rf1.search = "butt"
            rf1.server_name = chan1.server.name
            rf1.channel_name = chan1.name
            rf1.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf1)
            rf2 = E621Sub()
            rf2.search = "deer"
            rf2.server_name = chan2.server.name
            rf2.channel_name = chan2.name
            rf2.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf2)
            rf3 = E621Sub()
            rf3.search = "dragon"
            rf3.server_name = chan3.server.name
            rf3.channel_name = chan3.name
            rf3.update_frequency = Commons.load_time_delta("PT3600S")
            rfl.add_sub(rf3)
            # Splice this rss feed list into the function dispatcher's rss check object
            rss_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
            rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubE621Check
            rss_check_obj.e621_sub_list = rfl
            # Invalid title
            self.function_dispatcher.dispatch("e621 sub check Not a valid search", self.test_user, self.test_chan)
            data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            # Correct title but wrong channel
            self.function_dispatcher.dispatch("e621 sub check deer", self.test_user, chan1)
            data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
            assert "error" in data[0][0].lower()
            # Correct title check update
            self.function_dispatcher.dispatch("e621 sub check deer", self.test_user, chan2)
            data = serv1.get_send_data(1, chan2, Server.MSG_MSG)
            assert "search updates were found" in data[0][0].lower()
            assert len(data[0][0].lower().split("\n")) == 51
            # No updates
            self.function_dispatcher.dispatch("e621 sub check deer", self.test_user, chan2)
            data = serv1.get_send_data(1, chan2, Server.MSG_MSG)
            assert "no updates" in data[0][0], "No further updates should be found."
        finally:
            self.hallo.remove_server(serv2)
            self.hallo.remove_server(serv1)

    # def test_run_passive(self):
    #     # Set up test servers and channels
    #     serv1 = ServerMock(None)
    #     serv1.name = "test_serv1"
    #     chan1 = serv1.get_channel_by_name("test_chan1")
    #     chan2 = serv1.get_channel_by_name("test_chan2")
    #     serv2 = ServerMock(None)
    #     serv2.name = "test_serv2"
    #     chan3 = serv2.get_channel_by_name("test_chan1")
    #     try:
    #         self.hallo.add_server(serv1)
    #         self.hallo.add_server(serv2)
    #         # Set up rss feeds
    #         rfl = RssFeedList()
    #         rf1 = RssFeed()
    #         rf1.url = "http://spangle.org.uk/hallo/test_rss.xml?1"
    #         rf1.title = "test_feed1"
    #         rf1.server_name = chan1.server.name
    #         rf1.channel_name = chan1.name
    #         rf1.update_frequency = Commons.load_time_delta("PT3600S")
    #         rfl.add_feed(rf1)
    #         rf2 = RssFeed()
    #         rf2.url = "http://spangle.org.uk/hallo/test_rss.xml?2"
    #         rf2.title = "test_feed2"
    #         rf2.server_name = chan2.server.name
    #         rf2.channel_name = chan2.name
    #         rf2.update_frequency = Commons.load_time_delta("PT3600S")
    #         rfl.add_feed(rf2)
    #         rf3 = RssFeed()
    #         rf3.url = "http://spangle.org.uk/hallo/test_rss.xml?3"
    #         rf3.title = "test_feed1"
    #         rf3.server_name = chan3.server.name
    #         rf3.channel_name = chan3.name
    #         rf3.update_frequency = Commons.load_time_delta("PT3600S")
    #         rfl.add_feed(rf3)
    #         # Splice this rss feed list into the function dispatcher's rss check object
    #         rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
    #         rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
    #         rss_check_obj.rss_feed_list = rfl
    #         # Test passive feed updates
    #         self.function_dispatcher.dispatch_passive(Function.EVENT_MINUTE, None, None, None, None)
    #         # Check test server 1 data
    #         serv1_data = serv1.get_send_data(6)
    #         chan1_count = 0
    #         chan2_count = 0
    #         for data_line in serv1_data:
    #             if data_line[1] == chan1:
    #                 chan1_count += 1
    #             if data_line[1] == chan2:
    #                 chan2_count += 1
    #         assert chan1_count == 3
    #         assert chan2_count == 3
    #         # Check test server 2 data
    #         serv2_data = serv2.get_send_data(3, chan3, Server.MSG_MSG)
    #         # Test that no updates are found the second run
    #         rf1.last_check = None
    #         rf2.last_check = None
    #         rf3.last_check = None
    #         self.function_dispatcher.dispatch_passive(Function.EVENT_MINUTE, None, None, None, None)
    #         serv1.get_send_data(0)
    #         serv2.get_send_data(0)
    #         # Test that no feeds are checked before timeout, set urls to none and see if anything explodes.
    #         self.failed = False
    #         rf1.check_feed = self.do_not_call
    #         rf2.check_feed = self.do_not_call
    #         rf3.check_feed = self.do_not_call
    #         self.function_dispatcher.dispatch_passive(Function.EVENT_MINUTE, None, None, None, None)
    #         serv1.get_send_data(0)
    #         serv2.get_send_data(0)
    #         assert not self.failed, "check_feed() should not have been called on any feed."
    #     finally:
    #         self.hallo.remove_server(serv2)
    #         self.hallo.remove_server(serv1)
    #
    # def do_not_call(self):
    #     self.failed = True
    #     return []


class MockSubList:

    def __init__(self):
        self.to_xml_called = False

    def to_xml(self):
        print("ARGH")
        self.to_xml_called = True
