import os
import unittest

from Server import Server
from inc.Commons import Commons
from modules.Furry import SubE621Check, E621Sub
from test.TestBase import TestBase


class FeedRemoveTest(TestBase, unittest.TestCase):

    def setUp(self):
        try:
            os.rename("store/e621_subscriptions.xml", "store/e621_subscriptions.xml.tmp")
        except OSError:
            pass
        super().setUp()

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

    def test_remove_by_search(self):
        # Get subscription list
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        rfl = e621_check_obj.e621_sub_list
        # Add E621 searches to subscription list
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.server_name = self.server.name
        rf1.channel_name = self.test_chan.name
        rf1.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.server_name = self.server.name
        rf2.channel_name = "another_channel"
        rf2.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "fez"
        rf3.server_name = self.server.name
        rf3.channel_name = self.test_chan.name
        rf3.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf3)
        # Remove test search
        self.function_dispatcher.dispatch("e621 sub remove cabinet", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "removed \"cabinet\"" in data[0][0].lower()
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list

    def test_remove_multiple_matching_searches(self):
        # Get subscription list
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        rfl = e621_check_obj.e621_sub_list
        # Add E621 searches to subscription list
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.server_name = self.server.name
        rf1.channel_name = self.test_chan.name
        rf1.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.server_name = self.server.name
        rf2.channel_name = "another_channel"
        rf2.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "cabinet"
        rf3.server_name = self.server.name
        rf3.channel_name = self.test_chan.name
        rf3.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf3)
        # Remove test feed
        self.function_dispatcher.dispatch("e621 sub remove cabinet", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "removed \"cabinet\"" in data[0][0].lower()
        assert rf1 not in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 not in rfl.sub_list

    def test_remove_no_match(self):
        # Get subscription list
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        rfl = e621_check_obj.e621_sub_list
        # Add E621 searches to subscription list
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.server_name = self.server.name
        rf1.channel_name = self.test_chan.name
        rf1.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.server_name = self.server.name
        rf2.channel_name = "another_channel"
        rf2.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "fez"
        rf3.server_name = self.server.name
        rf3.channel_name = self.test_chan.name
        rf3.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf3)
        # Try to remove invalid search
        self.function_dispatcher.dispatch("e621 sub remove not_a_search", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()
        assert rf1 in rfl.sub_list
        assert rf2 in rfl.sub_list
        assert rf3 in rfl.sub_list
