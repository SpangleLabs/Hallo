import os
import unittest

from inc.Commons import Commons
from modules.Furry import E621SubList, E621Sub
from test.ServerMock import ServerMock


class TestE621SubList(unittest.TestCase):

    def test_init(self):
        rfl = E621SubList()
        assert rfl.sub_list == []

    def test_add_sub(self):
        rfl = E621SubList()
        assert rfl.sub_list == []
        # Create example rss feed
        rf = E621Sub()
        rf.update_frequency = Commons.load_time_delta("P0T3600S")
        rf.search = "cabinet"
        rfl.add_sub(rf)
        assert len(rfl.sub_list) == 1
        assert rfl.sub_list[0] == rf

    def test_get_subs_by_destination(self):
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        chan3 = serv2.get_channel_by_name("test_chan3")
        # Setup a feed list
        rfl = E621SubList()
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.server_name = chan1.server.name
        rf1.channel_name = chan1.name
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.server_name = user2.server.name
        rf2.user_name = user2.name
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "fez"
        rf3.server_name = chan3.server.name
        rf3.channel_name = chan3.name
        rfl.add_sub(rf3)
        rf4 = E621Sub()
        rf4.search = "tail_cuff"
        rf4.server_name = chan3.server.name
        rf4.channel_name = chan3.name
        rfl.add_sub(rf4)
        rf5 = E621Sub()
        rf5.search = "score:>50"
        rf5.server_name = chan3.server.name
        rf5.channel_name = chan3.name
        rfl.add_sub(rf5)
        # Check function
        feed_list = rfl.get_subs_by_destination(chan3)
        assert len(feed_list) == 3
        assert rf4 in feed_list
        assert rf3 in feed_list
        assert rf5 in feed_list

    def test_get_subs_by_search(self):
        serv1 = ServerMock(None)
        serv1.name = "test_serv1"
        serv2 = ServerMock(None)
        serv2.name = "test_serv2"
        chan1 = serv1.get_channel_by_name("test_chan1")
        user2 = serv1.get_user_by_address("test_user2".lower(), "test_user2")
        chan3 = serv2.get_channel_by_name("test_chan3")
        # Setup a feed list
        rfl = E621SubList()
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.server_name = chan1.server.name
        rf1.channel_name = chan1.name
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.server_name = user2.server.name
        rf2.user_name = user2.name
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "fez"
        rf3.server_name = chan3.server.name
        rf3.channel_name = chan3.name
        rfl.add_sub(rf3)
        rf4 = E621Sub()
        rf4.search = "tail_cuff"
        rf4.server_name = chan3.server.name
        rf4.channel_name = chan3.name
        rfl.add_sub(rf4)
        rf5 = E621Sub()
        rf5.search = "fez"
        rf5.server_name = chan3.server.name
        rf5.channel_name = chan3.name
        rfl.add_sub(rf5)
        # Check function
        feed_list = rfl.get_subs_by_search("fez", chan3)
        assert len(feed_list) == 2
        assert rf3 in feed_list
        assert rf5 in feed_list

    def test_remove_sub(self):
        # Setup a feed list
        rfl = E621SubList()
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rfl.add_sub(rf2)
        assert len(rfl.sub_list) == 2
        # Remove an item from the feed list
        rfl.remove_sub(rf1)
        assert len(rfl.sub_list) == 1
        assert rfl.sub_list[0] == rf2

    def test_xml(self):
        # Setup a feed list
        rfl = E621SubList()
        rf1 = E621Sub()
        rf1.search = "cabinet"
        rf1.update_frequency = Commons.load_time_delta("P0T3600S")
        rf1.server_name = "test_serv1"
        rf1.channel_name = "test_chan1"
        rfl.add_sub(rf1)
        rf2 = E621Sub()
        rf2.search = "clefable"
        rf2.update_frequency = Commons.load_time_delta("P1TS")
        rf2.server_name = "test_serv2"
        rf2.channel_name = "test_chan2"
        rfl.add_sub(rf2)
        rf3 = E621Sub()
        rf3.search = "fez"
        rf3.update_frequency = Commons.load_time_delta("PT60S")
        rf3.server_name = "test_serv3"
        rf3.user_name = "test_user3"
        rfl.add_sub(rf3)
        # Save to XML and load
        try:
            try:
                os.rename("store/e621_subscriptions.xml", "store/e621_subscriptions.xml.tmp")
            except OSError:
                pass
            rfl.to_xml()
            new_rfl = E621SubList.from_xml()
            assert len(new_rfl.sub_list) == 3
        finally:
            try:
                os.remove("store/e621_subscriptions.xml")
            except OSError:
                pass
            try:
                os.rename("store/e621_subscriptions.xml.tmp", "store/e621_subscriptions.xml")
            except OSError:
                pass
