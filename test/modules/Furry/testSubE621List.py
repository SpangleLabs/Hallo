import os
import unittest

from Events import EventMessage
from inc.Commons import Commons
from modules.Furry import SubE621Check, E621Sub
from test.TestBase import TestBase


class SubE621ListTest(TestBase, unittest.TestCase):

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

    def test_no_feeds(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "e621 sub list"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "no e621 search subscriptions" in data[0].text.lower()

    def test_list_feeds(self):
        # Get feed list
        rss_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: SubE621Check
        rfl = rss_check_obj.e621_sub_list
        # Add RSS feeds to feed list
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.server_name = self.server.name
        rf1.channel_address = self.test_chan.address
        rf1.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.server_name = self.server.name
        rf2.channel_address = "another_channel"
        rf2.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "fez"
        rf3.server_name = self.server.name
        rf3.channel_address = self.test_chan.address
        rf3.update_frequency = Commons.load_time_delta("PT3600S")
        rfl.add_sub(rf3)
        # Run FeedList and check output
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "e621 sub list"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        data_split = data[0].text.split("\n")
        assert "e621 search subscriptions posting" in data_split[0].lower(), "Missing title. Response data: "+str(data)
        assert "cabinet" in data_split[1].lower() or "cabinet" in data_split[2].lower()
        assert "clefable" not in data_split[1].lower() and "clefable" not in data_split[2].lower()
        assert "fez" in data_split[1].lower() or "fez" in data_split[2].lower()
