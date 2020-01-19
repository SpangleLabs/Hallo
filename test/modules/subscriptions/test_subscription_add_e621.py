import os
import unittest

import pytest

from events import EventMessage
from modules.subscriptions import SubscriptionCheck, E621Sub
from test.test_base import TestBase


@pytest.mark.external_integration
class E621SubAddTest(TestBase, unittest.TestCase):

    def setUp(self):
        try:
            os.rename("store/subscriptions.json", "store/subscriptions.json.tmp")
        except OSError:
            pass
        super().setUp()

    def tearDown(self):
        super().tearDown()
        try:
            os.remove("store/subscriptions.json")
        except OSError:
            pass
        try:
            os.rename("store/subscriptions.json.tmp", "store/subscriptions.json")
        except OSError:
            pass

    def test_invalid_search(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user, "e621 sub add ::"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower(), "No error in response. Response was: {}".format(data[0].text)

    def test_add_search(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "e621 sub add cabinet"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "created a new e621 subscription" in data[0].text.lower(), "Actual response: {}".format(data[0].text)
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubscriptionCheck
        rfl = e621_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(rfl) == 1, "Actual length: "+str(len(rfl))
        e6_sub = rfl[0]  # type: E621Sub
        assert e6_sub.search == "cabinet"
        assert e6_sub.server == self.server
        assert e6_sub.destination == self.test_chan
        assert e6_sub.latest_ids is not None
        assert len(e6_sub.latest_ids) == 10
        assert e6_sub.last_check is not None
        assert e6_sub.update_frequency.seconds == 300
        assert e6_sub.update_frequency.days == 0

    def test_add_search_user(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "e621 sub add cabinet"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "created a new e621 subscription" in data[0].text.lower(), "Actual response: {}".format(data[0].text)
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubscriptionCheck
        rfl = e621_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(rfl) == 1, "Actual length: "+str(len(rfl))
        e6_sub = rfl[0]  # type: E621Sub
        assert e6_sub.search == "cabinet"
        assert e6_sub.server == self.server
        assert e6_sub.destination == self.test_user
        assert e6_sub.latest_ids is not None
        assert len(e6_sub.latest_ids) == 10
        assert e6_sub.last_check is not None
        assert e6_sub.update_frequency.seconds == 300
        assert e6_sub.update_frequency.days == 0

    def test_add_search_period(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "e621 sub add cabinet PT3600S"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "created a new e621 subscription" in data[0].text.lower(), "Actual response: {}".format(data[0].text)
        # Check the search subscription was added
        e621_check_class = self.function_dispatcher.get_function_by_name("e621 sub check")
        e621_check_obj = self.function_dispatcher.get_function_object(e621_check_class)  # type: SubscriptionCheck
        rfl = e621_check_obj.get_sub_repo(self.hallo).sub_list
        assert len(rfl) == 1, "Actual length: "+str(len(rfl))
        e6_sub = rfl[0]  # type: E621Sub
        assert e6_sub.search == "cabinet"
        assert e6_sub.server == self.server
        assert e6_sub.destination == self.test_chan
        assert e6_sub.latest_ids is not None
        assert len(e6_sub.latest_ids) == 10
        assert e6_sub.last_check is not None
        assert e6_sub.update_frequency.seconds == 3600
        assert e6_sub.update_frequency.days == 0
