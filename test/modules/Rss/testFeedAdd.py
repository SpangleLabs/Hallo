import os
import unittest

from Events import EventMessage
from modules.Rss import FeedCheck
from test.TestBase import TestBase


class FeedAddTest(TestBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        try:
            os.rename("store/rss_feeds.xml", "store/rss_feeds.xml.tmp")
        except OSError:
            pass

    def tearDown(self):
        super().tearDown()
        try:
            os.remove("store/rss_feeds.xml")
        except OSError:
            pass
        try:
            os.rename("store/rss_feeds.xml.tmp", "store/rss_feeds.xml")
        except OSError:
            pass

    def test_invalid_url(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "rss add not_a_url"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()

    def test_invalid_period(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "rss add http://spangle.org.uk/hallo/test_rss.xml PTTS"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()

    def test_invalid_rss(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "rss add http://example.com"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "error" in data[0].text.lower()

    def test_add_feed(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "rss add http://spangle.org.uk/hallo/test_rss.xml"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        print(data)
        assert "added new rss feed" in data[0].text.lower()
        # Check the rss feed was added
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
        rfl = rss_check_obj.rss_feed_list.feed_list
        assert len(rfl) == 1
        assert rfl[0].url == "http://spangle.org.uk/hallo/test_rss.xml"
        assert rfl[0].server_name == self.server.name
        assert rfl[0].channel_name == self.test_chan.name
        assert rfl[0].user_name is None
        assert rfl[0].last_item_hash is not None
        assert rfl[0].last_check is not None
        assert rfl[0].update_frequency.seconds == 3600
        assert rfl[0].update_frequency.days == 0

    def test_add_feed_user(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "rss add http://spangle.org.uk/hallo/test_rss.xml"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        print(data)
        assert "added new rss feed" in data[0].text.lower()
        # Check the rss feed was added
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
        rfl = rss_check_obj.rss_feed_list.feed_list
        assert len(rfl) == 1
        assert rfl[0].url == "http://spangle.org.uk/hallo/test_rss.xml"
        assert rfl[0].server_name == self.server.name
        assert rfl[0].channel_name is None
        assert rfl[0].user_name == self.test_user.name
        assert rfl[0].last_item_hash is not None
        assert rfl[0].last_check is not None
        assert rfl[0].update_frequency.seconds == 3600
        assert rfl[0].update_frequency.days == 0

    def test_add_feed_period(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, self.test_chan, self.test_user,
                                                       "rss add http://spangle.org.uk/hallo/test_rss.xml PT300S"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert "added new rss feed" in data[0].text.lower()
        # Check the rss feed was added
        rss_check_class = self.function_dispatcher.get_function_by_name("rss check")
        rss_check_obj = self.function_dispatcher.get_function_object(rss_check_class)  # type: FeedCheck
        rfl = rss_check_obj.rss_feed_list.feed_list
        assert len(rfl) == 1
        assert rfl[0].url == "http://spangle.org.uk/hallo/test_rss.xml"
        assert rfl[0].server_name == self.server.name
        assert rfl[0].channel_name == self.test_chan.name
        assert rfl[0].user_name is None
        assert rfl[0].last_item_hash is not None
        assert rfl[0].last_check is not None
        assert rfl[0].update_frequency.seconds == 300
        assert rfl[0].update_frequency.days == 0
