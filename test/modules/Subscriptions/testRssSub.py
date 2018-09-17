import unittest
from datetime import datetime
import time
from xml.etree import ElementTree

from Events import EventMessage
from Hallo import Hallo
from inc.Commons import Commons
from modules.Subscriptions import RssSub, SubscriptionRepo
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class TestRssFeed(TestBase, unittest.TestCase):

    def test_init(self):
        rf = RssSub(self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml")
        keys = ["title", "url", "server", "destination", "last_item_hash", "last_check", "update_frequency"]
        for key in keys:
            assert key in rf.__dict__, "Key is missing from RssFeed object: " + key

    def test_check_feed(self):
        # Check loading up an example feed
        test_rss_url = "http://spangle.org.uk/hallo/test_rss.xml"
        rf = RssSub(self.server, self.test_chan, test_rss_url)
        rf.url = test_rss_url
        new_items = rf.check()
        assert rf.title == "Example rss feed"
        assert len(new_items) == 3
        for new_item in new_items:
            format_item = rf.format_item(new_item).text
            assert "Item 1" in format_item or \
                   "Item 2" in format_item or \
                   "Item 3" in format_item, "Item name not in formatted item: " + format_item
            assert "example.com/item1" in format_item or \
                   "example.com/item2" in format_item or \
                   "example.com/item3" in format_item, "Item link not in formatted item: " + format_item
        # Check that calling twice returns no more items
        next_items = rf.check()
        assert len(next_items) == 0, "More items should not have been found."

    def test_format_item(self):
        feed_title = "feed_title1"
        item_title = "test_title1"
        item_link = "http://example.com/item1"
        rf = RssSub(self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml", title=feed_title)
        rss_data = "<channel><item><title>" + item_title + "</title><link>" + item_link + "</link></item></channel>"
        rss_elem = ElementTree.fromstring(rss_data)
        item_elem = rss_elem.find("item")
        # Get output and check it
        output = rf.format_item(item_elem).text
        assert feed_title in output
        assert item_title in output
        assert item_link in output

    def test_needs_check(self):
        rf1 = RssSub(self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml",
                     last_check=datetime.now(), update_frequency=Commons.load_time_delta("P1TS"))
        assert not rf1.needs_check()
        rf1.last_check = datetime.now() - Commons.load_time_delta("P2TS")
        assert rf1.needs_check()
        rf1.update_frequency = Commons.load_time_delta("P7TS")
        assert not rf1.needs_check()
        rf2 = RssSub(self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml",
                     last_check=datetime.now(), update_frequency=Commons.load_time_delta("PT5S"))
        assert not rf2.needs_check()
        time.sleep(10)
        assert rf2.needs_check()

    def test_output_item(self):
        # Create example rss item element
        example_url = "http://spangle.org.uk/hallo/test_rss.xml"
        item_title = "test_title1"
        item_link = "http://example.com/item1"
        feed_title = "feed_title1"
        rss_data = "<channel><item><title>" + item_title + "</title><link>" + item_link + "</link></item></channel>"
        rss_elem = ElementTree.fromstring(rss_data)
        item_elem = rss_elem.find("item")
        # Check output works with given server and channel
        serv1 = ServerMock(self.hallo)
        serv1.name = "test_serv1"
        self.hallo.add_server(serv1)
        chan1 = serv1.get_channel_by_address("test_chan1")
        rf1 = RssSub(serv1, chan1, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf1.send_item(item_elem)
        data = serv1.get_send_data(1, chan1, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text
        # Check output works with given server not channel
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        self.hallo.add_server(serv2)
        chan2 = serv2.get_channel_by_address("test_chan2")
        rf2 = RssSub(serv2, chan2, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf2.send_item(item_elem)
        data = serv2.get_send_data(1, chan2, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text
        # Check output works with given server not user
        serv3 = ServerMock(self.hallo)
        serv3.name = "test_serv3"
        self.hallo.add_server(serv3)
        user3 = serv3.get_user_by_address("test_user3")
        rf3 = RssSub(serv3, user3, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf3.send_item(item_elem)
        data = serv3.get_send_data(1, user3, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text
        # Check output works without given server with given channel
        hallo4 = Hallo()
        serv4 = ServerMock(hallo4)
        serv4.name = "test_serv4"
        hallo4.add_server(serv4)
        chan4 = serv4.get_channel_by_address("test_chan4")
        rf4 = RssSub(serv4, chan4, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf4.send_item(item_elem)
        data = serv4.get_send_data(1, chan4, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text
        # Check output works without given server with given user
        hallo5 = Hallo()
        serv5 = ServerMock(hallo5)
        serv5.name = "test_serv5"
        hallo5.add_server(serv5)
        chan5 = serv5.get_channel_by_address("test_chan5")
        rf5 = RssSub(serv5, chan5, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf5.send_item(item_elem)
        data = serv5.get_send_data(1, chan5, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text
        # Check output works without given server or channel to channel
        hallo6 = Hallo()
        serv6 = ServerMock(hallo6)
        serv6.name = "test_serv6"
        hallo6.add_server(serv6)
        chan6 = serv6.get_channel_by_address("test_chan6")
        rf6 = RssSub(serv6, chan6, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf6.send_item(item_elem)
        data = serv6.get_send_data(1, chan6, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text
        # Check output works without given server or channel to user
        hallo7 = Hallo()
        serv7 = ServerMock(hallo7)
        serv7.name = "test_serv7"
        hallo7.add_server(serv7)
        user7 = serv7.get_user_by_address("test_user7")
        rf7 = RssSub(serv7, user7, example_url, title=feed_title, update_frequency=Commons.load_time_delta("P1TS"))
        rf7.send_item(item_elem)
        data = serv7.get_send_data(1, user7, EventMessage)
        assert feed_title in data[0].text
        assert item_title in data[0].text
        assert item_link in data[0].text

    def test_xml(self):
        test_rss_url = "http://spangle.org.uk/hallo/test_rss.xml"
        test_seconds = 3600
        test_days = 0
        # Create example feed
        sub_repo = SubscriptionRepo()
        rf = RssSub(self.server, self.test_chan, test_rss_url,
                    update_frequency=Commons.load_time_delta("P"+str(test_days)+"T"+str(test_seconds)+"S"))
        # Clear off the current items
        rf.check()
        # Ensure there are no new items
        new_items = rf.check()
        assert len(new_items) == 0
        # Save to XML and load up new RssFeed
        rf_xml = rf.to_json()
        rf2 = RssSub.from_json(rf_xml, self.hallo, sub_repo)
        # Ensure there's still no new items
        new_items = rf2.check()
        assert len(new_items) == 0
        assert rf2.update_frequency.days == test_days
        assert rf2.update_frequency.seconds == test_seconds
