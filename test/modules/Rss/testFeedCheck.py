import unittest

from Server import Server
from modules.Rss import FeedCheck
from test.TestBase import TestBase


class FeedCheckTest(TestBase, unittest.TestCase):

    def test_init(self):
        fc = FeedCheck()
        assert fc.rss_feed_list is not None
        assert fc.rss_feed_list.feed_list == []

    def test_save_function(self):
        fc = FeedCheck()
        # Mock out the rss feed list
        mfl = MockRssFeedList()
        fc.rss_feed_list = mfl
        assert mfl.to_xml_called


class MockRssFeedList:

    def __init__(self):
        self.to_xml_called = False

    def to_xml(self):
        self.to_xml_called = True
