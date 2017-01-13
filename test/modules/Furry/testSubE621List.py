import os
import unittest

from Server import Server
from inc.Commons import Commons
from modules.Furry import SubE621Check, E621Sub, E621SubList
from test.TestBase import TestBase


class SubE621ListTest(TestBase, unittest.TestCase):

    def setUp(self):
        try:
            os.rename("store/e621_subscriptions.xml", "store/e621_subscriptions.xml.tmp")
        except OSError:
            pass
        super().setUp()
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        e621_check_obj.e621_sub_list = E621SubList()

    def tearDown(self):
        super().tearDown()
        try:
            os.remove("store/e621_subscriptions.xml")
        except OSError:
            pass
        try:
            os.rename("store/e621_subscriptions.xml.tmp", "store/e621_subscriptions.xml")
        except OSError:
            pass

    def test_no_feeds(self):
        self.function_dispatcher.dispatch("e621 sub list", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "no e621 search subscriptions" in data[0][0].lower()

    def test_list_feeds(self):
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubE621Check
        rfl = rss_check_obj.e621_sub_list
        # Add RSS feeds to feed list
        rf1 = E621Sub()
        rf1.search = "butt"
        rf1.server_name = self.server.name
        rf1.channel_name = self.test_chan.name
        rf1.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "deer"
        rf2.server_name = self.server.name
        rf2.channel_name = "another_channel"
        rf2.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "dragon"
        rf3.server_name = self.server.name
        rf3.channel_name = self.test_chan.name
        rf3.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf3)
        # Run FeedList and check output
        self.function_dispatcher.dispatch("e621 sub list", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        data_split = data[0][0].split("\n")
        assert "e621 search subscriptions posting" in data_split[0].lower()
        assert "butt" in data_split[1].lower() or "butt" in data_split[2].lower()
        assert "deer" not in data_split[1].lower() and "deer" not in data_split[2].lower()
        assert "dragon" in data_split[1].lower() or "dragon" in data_split[2].lower()
