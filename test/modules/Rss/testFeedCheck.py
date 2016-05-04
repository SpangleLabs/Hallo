import unittest

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
        fc.save_function()
        assert mfl.to_xml_called

    def test_run_all(self):
        assert False
        # Test running all feed updates
        # Test running with no new updates.

    def test_run_by_title(self):
        assert False
        # Invalid title
        # Correct title check update
        # Correct title but wrong channel
        # No updates

    def test_run_passive(self):
        assert False
        # Test running all feed updates
        # Test running with no new updates


class MockRssFeedList:

    def __init__(self):
        self.to_xml_called = False

    def to_xml(self):
        self.to_xml_called = True
