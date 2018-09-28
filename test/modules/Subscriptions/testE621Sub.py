import unittest
from datetime import datetime
import time

from Events import EventMessage
from Hallo import Hallo
from inc.Commons import Commons
from modules.Subscriptions import E621Sub, SubscriptionRepo
from test.ServerMock import ServerMock
from test.TestBase import TestBase


class TestE621Sub(TestBase, unittest.TestCase):

    def test_init(self):
        rf = E621Sub(self.server, self.test_chan, "cabinet")
        keys = ["search", "server", "destination", "latest_ids", "last_check",
                "update_frequency"]
        for key in keys:
            assert key in rf.__dict__, "Key is missing from E621Sub object: " + key

    def test_check_search(self):
        # Check loading up an example search
        test_search = "cabinet"
        rf = E621Sub(self.server, self.test_chan, test_search)
        new_items = rf.check()
        assert len(new_items) == 50
        for new_item in new_items:
            format_item = rf.format_item(new_item).text
            assert "(Explicit)" in format_item or \
                   "(Questionable)" in format_item or \
                   "(Safe)" in format_item, "Rating not in formatted item: " + format_item
            assert "e621.net/post/show/", "E621 link not in formatted item: " + format_item
        # Check that calling twice returns no more items
        next_items = rf.check()
        assert len(next_items) == 0, "More items should not have been found. Found "+str(len(next_items))

    def test_format_item(self):
        item_id = "572912"
        item_rating = "q"
        rf = E621Sub(self.server, self.test_chan, "cabinet")
        json_data = dict()
        json_data["id"] = item_id
        json_data["rating"] = item_rating
        json_data["file_url"] = "http://spangle.org.uk/haskell.jpg"
        json_data["file_ext"] = "jpg"
        # Get output and check it
        output = rf.format_item(json_data).text
        assert item_id in output
        assert "(Questionable)" in output

    def test_needs_check(self):
        rf1 = E621Sub(self.server, self.test_chan, "cabinet",
                      last_check=datetime.now(), update_frequency=Commons.load_time_delta("P1TS"))
        assert not rf1.needs_check()
        rf1.last_check = datetime.now() - Commons.load_time_delta("P2TS")
        assert rf1.needs_check()
        rf1.update_frequency = Commons.load_time_delta("P7TS")
        assert not rf1.needs_check()
        rf2 = E621Sub(self.server, self.test_chan, "cabinet",
                      last_check=datetime.now(), update_frequency=Commons.load_time_delta("PT5S"))
        assert not rf2.needs_check()
        time.sleep(10)
        assert rf2.needs_check()

    def test_output_item(self):
        # Create example e621 sub element
        item_id = "652362"
        item_rate = "q"
        item_rating = "(Questionable)"
        item_elem = {"id": item_id, "rating": item_rate, "file_url": "12345", "file_ext": "png"}
        # Check output works with given server and channel
        rf1 = E621Sub(self.server, self.test_chan, "cabinet")
        rf1.update_frequency = Commons.load_time_delta("P1TS")
        rf1.send_item(item_elem)
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text
        # Check output works with given server not channel
        serv2 = ServerMock(self.hallo)
        serv2.name = "test_serv2"
        self.hallo.add_server(serv2)
        chan2 = serv2.get_channel_by_address("test_chan2".lower(), "test_chan2")
        rf2 = E621Sub(serv2, chan2, "clefable", update_frequency=Commons.load_time_delta("P1TS"))
        rf2.send_item(item_elem)
        data = serv2.get_send_data(1, chan2, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text
        # Check output works with given server not user
        serv3 = ServerMock(self.hallo)
        serv3.name = "test_serv3"
        self.hallo.add_server(serv3)
        user3 = serv3.get_user_by_address("test_user3".lower(), "test_user3")
        rf3 = E621Sub(serv3, user3, "fez", update_frequency=Commons.load_time_delta("P1TS"))
        rf3.send_item(item_elem)
        data = serv3.get_send_data(1, user3, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text
        # Check output works without given server with given channel
        hallo4 = Hallo()
        serv4 = ServerMock(hallo4)
        serv4.name = "test_serv4"
        hallo4.add_server(serv4)
        chan4 = serv4.get_channel_by_address("test_chan4".lower(), "test_chan4")
        rf4 = E621Sub(serv4, chan4, "cabinet", update_frequency=Commons.load_time_delta("P1TS"))
        rf4.send_item(item_elem)
        data = serv4.get_send_data(1, chan4, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text
        # Check output works without given server with given user
        hallo5 = Hallo()
        serv5 = ServerMock(hallo5)
        serv5.name = "test_serv5"
        hallo5.add_server(serv5)
        chan5 = serv5.get_channel_by_address("test_chan5".lower(), "test_chan5")
        rf5 = E621Sub(serv5, chan5, "clefable", update_frequency=Commons.load_time_delta("P1TS"))
        rf5.send_item(item_elem)
        data = serv5.get_send_data(1, chan5, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text
        # Check output works without given server or channel to channel
        hallo6 = Hallo()
        serv6 = ServerMock(hallo6)
        serv6.name = "test_serv6"
        hallo6.add_server(serv6)
        chan6 = serv6.get_channel_by_address("test_chan6".lower(), "test_chan6")
        rf6 = E621Sub(serv6, chan6, "fez", update_frequency=Commons.load_time_delta("P1TS"))
        rf6.server_name = "test_serv6"
        rf6.channel_address = "test_chan6"
        rf6.send_item(item_elem)
        data = serv6.get_send_data(1, chan6, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text
        # Check output works without given server or channel to user
        hallo7 = Hallo()
        serv7 = ServerMock(hallo7)
        serv7.name = "test_serv7"
        hallo7.add_server(serv7)
        user7 = serv7.get_user_by_address("test_user7".lower(), "test_user7")
        rf7 = E621Sub(serv7, user7, "clefable", update_frequency=Commons.load_time_delta("P1TS"))
        rf7.send_item(item_elem)
        data = serv7.get_send_data(1, user7, EventMessage)
        assert item_id in data[0].text
        assert item_rating in data[0].text

    def test_json(self):
        test_e621_search = "cabinet"
        test_seconds = 3600
        test_days = 0
        # Create example feed
        sub_repo = SubscriptionRepo()
        rf = E621Sub(self.server, self.test_chan, test_e621_search,
                     update_frequency=Commons.load_time_delta("P"+str(test_days)+"T"+str(test_seconds)+"S"))
        # Clear off the current items
        rf.check()
        # Ensure there are no new items
        new_items = rf.check()
        assert len(new_items) == 0
        # Save to json and load up new E621Sub
        rf_json = rf.to_json()
        rf2 = E621Sub.from_json(rf_json, self.hallo, sub_repo)
        # Ensure there's still no new items
        new_items = rf2.check()
        assert len(new_items) == 0
        assert rf2.update_frequency.days == test_days
        assert rf2.update_frequency.seconds == test_seconds
