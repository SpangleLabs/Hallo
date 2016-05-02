import unittest
from modules.Rss import RssFeedList


class TestRssFeedList(unittest.TestCase):

    def test_init(self):
        rfl = RssFeedList()
        assert rfl.feed_list == []
