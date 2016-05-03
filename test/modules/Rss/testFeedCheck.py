import unittest

from Server import Server
from modules.Rss import FeedCheck
from test.TestBase import TestBase


class FeedCheckTest(TestBase, unittest.TestCase):

    def test_init(self):
        fc = FeedCheck()
        assert fc.rss_feed_list is not None
        assert fc.rss_feed_list.feed_list == []
