import unittest
from datetime import datetime
import time
from xml.etree import ElementTree

from Hallo import Hallo
from Server import Server
from inc.Commons import Commons
from modules.Rss import RssFeed
from test.ServerMock import ServerMock


class TestRssFeed(unittest.TestCase):

    def test_init(self):
        rf = RssFeed()
        keys = ["title", "url", "server_name", "channel_name",
                "user_name", "last_item_hash", "last_check", "update_frequency"]
        for key in keys:
            assert key in rf.__dict__, "Key is missing from RssFeed object: " + key

    def test_check_feed(self):
        # Check loading up an example feed
        test_rss_url = "http://spangle.org.uk/hallo/test_rss.xml"
        rf = RssFeed()
        rf.url = test_rss_url
        new_items = rf.check_feed()
        assert rf.title == "Example rss feed"
        assert len(new_items) == 3
        for new_item in new_items:
            format_item = rf.format_item(new_item)
            assert "Item 1" in format_item or \
                   "Item 2" in format_item or \
                   "Item 3" in format_item, "Item name not in formatted item: " + format_item
            assert "example.com/item1" in format_item or \
                   "example.com/item2" in format_item or \
                   "example.com/item3" in format_item, "Item link not in formatted item: " + format_item
        # Check that calling twice returns no more items
        next_items = rf.check_feed()
        assert len(next_items) == 0, "More items should not have been found."

    def test_format_item(self):
        feed_title = "feed_title1"
        item_title = "test_title1"
        item_link = "http://example.com/item1"
        rf = RssFeed()
        rf.title = feed_title
        rss_data = "<channel><item><title>" + item_title + "</title><link>" + item_link + "</link></item></channel>"
        rss_elem = ElementTree.fromstring(rss_data)
        item_elem = rss_elem.find("item")
        # Get output and check it
        output = rf.format_item(item_elem)
        assert feed_title in output
        assert item_title in output
        assert item_link in output

    def test_needs_check(self):
        rf1 = RssFeed()
        rf1.last_check = datetime.now()
        rf1.update_frequency = Commons.load_time_delta("P1TS")
        assert not rf1.needs_check()
        rf1.last_check = datetime.now() - Commons.load_time_delta("P2TS")
        assert rf1.needs_check()
        rf1.update_frequency = Commons.load_time_delta("P7TS")
        assert not rf1.needs_check()
        rf2 = RssFeed()
        rf2.last_check = datetime.now()
        rf2.update_frequency = Commons.load_time_delta("PT5S")
        assert not rf2.needs_check()
        time.sleep(10)
        assert rf2.needs_check()

    def test_output_item(self):
        # Create example rss item element
        item_title = "test_title1"
        item_link = "http://example.com/item1"
        feed_title = "feed_title1"
        rss_data = "<channel><item><title>" + item_title + "</title><link>" + item_link + "</link></item></channel>"
        rss_elem = ElementTree.fromstring(rss_data)
        item_elem = rss_elem.find("item")
        # Check output works with given server and channel
        rf1 = RssFeed()
        rf1.update_frequency = Commons.load_time_delta("P1TS")
        rf1.title = feed_title
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        chan1 = serv1.get_channel_by_address("test_chan1".lower(), "test_chan1")
        rf1.output_item(item_elem, None, serv1, chan1)
        data = serv1.get_send_data(1, chan1, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check output works with given server not channel
        rf2 = RssFeed()
        rf2.update_frequency = Commons.load_time_delta("P1TS")
        rf2.title = feed_title
        rf2.channel_name = "test_chan2"
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan2 = serv2.get_channel_by_address("test_chan2".lower(), "test_chan2")
        rf2.output_item(item_elem, None, serv2)
        data = serv2.get_send_data(1, chan2, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check output works with given server not user
        rf3 = RssFeed()
        rf3.update_frequency = Commons.load_time_delta("P1TS")
        rf3.title = feed_title
        rf3.user_name = "test_user3"
        serv3 = ServerMock(None)
        serv3.name = "test_serv3"
        user3 = serv3.get_user_by_address("test_user3","test_user3")
        rf3.output_item(item_elem, None, serv3)
        data = serv3.get_send_data(1, user3, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check output works without given server with given channel
        rf4 = RssFeed()
        rf4.update_frequency = Commons.load_time_delta("P1TS")
        rf4.title = feed_title
        rf4.server_name = "test_serv4"
        serv4 = ServerMock(None)
        serv4.name = "test_serv4"
        hallo4 = Hallo()
        hallo4.add_server(serv4)
        chan4 = serv4.get_channel_by_address("test_chan4".lower(), "test_chan4")
        rf4.output_item(item_elem, hallo4, None, chan4)
        data = serv4.get_send_data(1, chan4, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check output works without given server with given user
        rf5 = RssFeed()
        rf5.update_frequency = Commons.load_time_delta("P1TS")
        rf5.title = feed_title
        rf5.server_name = "test_serv5"
        serv5 = ServerMock(None)
        serv5.name = "test_serv5"
        hallo5 = Hallo()
        hallo5.add_server(serv5)
        chan5 = serv5.get_channel_by_address("test_chan5".lower(), "test_chan5")
        rf5.output_item(item_elem, hallo5, None, chan5)
        data = serv5.get_send_data(1, chan5, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check output works without given server or channel to channel
        rf6 = RssFeed()
        rf6.update_frequency = Commons.load_time_delta("P1TS")
        rf6.title = feed_title
        rf6.server_name = "test_serv6"
        rf6.channel_name = "test_chan6"
        serv6 = ServerMock(None)
        serv6.name = "test_serv6"
        hallo6 = Hallo()
        hallo6.add_server(serv6)
        chan6 = serv6.get_channel_by_address("test_chan6".lower(), "test_chan6")
        rf6.output_item(item_elem, hallo6)
        data = serv6.get_send_data(1, chan6, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check output works without given server or channel to user
        rf7 = RssFeed()
        rf7.update_frequency = Commons.load_time_delta("P1TS")
        rf7.title = feed_title
        rf7.server_name = "test_serv7"
        rf7.user_name = "test_user7"
        serv7 = ServerMock(None)
        serv7.name = "test_serv7"
        hallo7 = Hallo()
        hallo7.add_server(serv7)
        user7 = serv7.get_user_by_address("test_user7","test_user7")
        rf7.output_item(item_elem, hallo7)
        data = serv7.get_send_data(1, user7, Server.MSG_MSG)
        assert feed_title in data[0][0]
        assert item_title in data[0][0]
        assert item_link in data[0][0]
        # Check invalid server output (server name is none)
        rf8 = RssFeed()
        rf8.update_frequency = Commons.load_time_delta("P1TS")
        rf8.title = feed_title
        hallo8 = Hallo()
        resp = rf8.output_item(item_elem, hallo8)
        assert "error" in resp.lower()
        assert "server" in resp.lower()
        # Check invalid server output ( server name is not in hallo obj)
        rf9 = RssFeed()
        rf9.update_frequency = Commons.load_time_delta("P1TS")
        rf9.title = feed_title
        rf9.server_name = "not_a_server"
        hallo9 = Hallo()
        resp = rf9.output_item(item_elem, hallo9)
        assert "error" in resp.lower()
        assert "server" in resp.lower()
        # Check invalid channel/user output (only possible if channel name and user name are none) (with given server)
        rf10 = RssFeed()
        rf10.update_frequency = Commons.load_time_delta("P1TS")
        rf10.title = feed_title
        serv10 = ServerMock(None)
        serv10.name = "test_serv10"
        hallo10 = Hallo()
        hallo10.add_server(serv10)
        resp = rf10.output_item(item_elem, hallo10, serv10)
        assert "error" in resp.lower()
        assert "destination" in resp.lower()
        # Check invalid channel/user output (only possible if channel name and user name are none) (with named server)
        rf11 = RssFeed()
        rf11.update_frequency = Commons.load_time_delta("P1TS")
        rf11.title = feed_title
        rf11.server_name = "test_serv11"
        serv11 = ServerMock(None)
        serv11.name = "test_serv11"
        hallo11 = Hallo()
        hallo11.add_server(serv11)
        resp = rf11.output_item(item_elem, hallo11)
        assert "error" in resp.lower()
        assert "destination" in resp.lower()

    def test_xml(self):
        test_rss_url = "http://spangle.org.uk/hallo/test_rss.xml"
        test_seconds = 3600
        test_days = 0
        # Create example feed
        rf = RssFeed()
        rf.url = test_rss_url
        rf.update_frequency = Commons.load_time_delta("P"+str(test_days)+"T"+str(test_seconds)+"S")
        rf.server_name = "test_serv"
        rf.channel_name = "test_chan"
        # Clear off the current items
        rf.check_feed()
        # Ensure there are no new items
        new_items = rf.check_feed()
        assert len(new_items) == 0
        # Save to XML and load up new RssFeed
        rf_xml = rf.to_xml_string()
        rf2 = RssFeed.from_xml_string(rf_xml)
        # Ensure there's still no new items
        new_items = rf2.check_feed()
        assert len(new_items) == 0
        assert rf2.update_frequency.days == test_days
        assert rf2.update_frequency.seconds == test_seconds
