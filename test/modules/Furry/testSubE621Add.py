import os
import unittest

from Server import Server
from modules.Furry import SubE621Check
from test.TestBase import TestBase


class E621SubAddTest(TestBase, unittest.TestCase):

    def setUp(self):
        try:
            os.rename("store/e621_subscriptions.json", "store/e621_subscriptions.json.tmp")
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
            os.rename("store/e621_subscriptions.json.tmp", "store/e621_subscriptions.json")
        except OSError:
            pass

    def test_invalid_search(self):
        self.function_dispatcher.dispatch("e621 sub add ::", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "error" in data[0][0].lower()

    def test_add_search(self):
        self.function_dispatcher.dispatch("e621 sub add cabinet", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert "added new e621 subscription" in data[0][0].lower()
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        rfl = e621_check_obj.e621_sub_list.sub_list
        assert len(rfl) == 1, "Actual length: "+str(len(rfl))
        assert rfl[0].search == "cabinet"
        assert rfl[0].server_name == self.server.name
        assert rfl[0].channel_address == self.test_chan.name
        assert rfl[0].user_address is None
        assert rfl[0].latest_ten_ids is not None
        assert len(rfl[0].latest_ten_ids) == 10
        assert rfl[0].last_check is not None
        assert rfl[0].update_frequency.seconds == 300
        assert rfl[0].update_frequency.days == 0

    def test_add_search_user(self):
        self.function_dispatcher.dispatch("e621 sub add cabinet", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "added new e621 subscription" in data[0][0].lower()
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        rfl = e621_check_obj.e621_sub_list.sub_list
        assert len(rfl) == 1, "Actual length: "+str(len(rfl))
        assert rfl[0].search == "cabinet"
        assert rfl[0].server_name == self.server.name
        assert rfl[0].channel_address is None
        assert rfl[0].user_address == self.test_user.name
        assert rfl[0].latest_ten_ids is not None
        assert len(rfl[0].latest_ten_ids) == 10
        assert rfl[0].last_check is not None
        assert rfl[0].update_frequency.seconds == 300
        assert rfl[0].update_frequency.days == 0

    def test_add_search_period(self):
        self.function_dispatcher.dispatch("e621 sub add cabinet PT3600S", self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        print(data)
        assert "added new e621 subscription" in data[0][0].lower()
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubE621Check
        rfl = e621_check_obj.e621_sub_list.sub_list
        assert len(rfl) == 1, "Actual length: "+str(len(rfl))
        assert rfl[0].search == "cabinet"
        assert rfl[0].server_name == self.server.name
        assert rfl[0].channel_address == self.test_chan.name
        assert rfl[0].user_address is None
        assert rfl[0].latest_ten_ids is not None
        assert len(rfl[0].latest_ten_ids) == 10
        assert rfl[0].last_check is not None
        assert rfl[0].update_frequency.seconds == 3600
        assert rfl[0].update_frequency.days == 0
