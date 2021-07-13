import importlib
import inspect
import os
import unittest
from typing import Dict, List, Type

import pytest
from yippi import YippiClient

import hallo.modules.subscriptions.subscription
from hallo.events import EventMessage
from hallo.inc.commons import inherits_from
from hallo.modules.subscriptions.common_fa_key import FAKey
from hallo.modules.subscriptions.source import Source
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.source_e621_tagging import E621TaggingSource
from hallo.modules.subscriptions.source_fa_favs import FAFavsSource
from hallo.modules.subscriptions.source_fa_notes import FANotesSource, FANotesInboxSource, FANotesOutboxSource
from hallo.modules.subscriptions.source_fa_notif_comments import FACommentNotificationsSource, \
    FASubmissionCommentSource, FAJournalCommentSource, FAShoutSource
from hallo.modules.subscriptions.source_fa_notif_favs import FAFavNotificationsSource
from hallo.modules.subscriptions.source_fa_watchers import FAUserWatchersSource, FAWatchersSource
from hallo.modules.subscriptions.source_reddit import RedditSource
from hallo.modules.subscriptions.source_rss import RssSource
# from hallo.modules.subscriptions.source_twitter import TwitterSource
from hallo.modules.subscriptions.subscription_factory import SubscriptionFactory
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo

from hallo.test.test_base import TestBase


@pytest.mark.external_integration
class TestAllSourceClasses(TestBase, unittest.TestCase):
    cookie_a = os.getenv("test_cookie_a")
    cookie_b = os.getenv("test_cookie_b")

    def get_source_objects(self) -> List[Source]:
        fa_key = FAKey(self.test_user, self.cookie_a, self.cookie_b)
        e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
        sub_repo = SubscriptionRepo(self.hallo)
        sub_objs = list()
        sub_objs.append(E621Source("cabinet", e6_client, self.test_user))
        sub_objs.append(E621TaggingSource("cabinet", e6_client, sub_repo, self.test_user, ["door"]))
        sub_objs.append(RssSource("http://spangle.org.uk/hallo/test_rss.xml"))
        sub_objs.append(FANotesSource(fa_key, FANotesInboxSource(fa_key), FANotesOutboxSource(fa_key)))
        sub_objs.append(FAFavsSource(fa_key, "zephyr42"))
        sub_objs.append(FAUserWatchersSource(fa_key, "zephyr42"))
        sub_objs.append(FAWatchersSource(fa_key))
        sub_objs.append(FAFavNotificationsSource(fa_key))
        sub_objs.append(FACommentNotificationsSource(
            fa_key,
            FASubmissionCommentSource(fa_key),
            FAJournalCommentSource(fa_key),
            FAShoutSource(fa_key)
        ))
        sub_objs.append(RedditSource("deer"))
        # sub_objs.append(TwitterSource("telegram", None))
        return sub_objs

    def get_source_create_arguments(self) -> Dict[Type[Source], str]:
        sub_repo = SubscriptionRepo(self.hallo)
        fa_key = FAKey(self.test_user, self.cookie_a, self.cookie_b)
        fa_commons = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
        fa_commons.add_key(fa_key)
        sub_evts = dict()
        sub_evts[E621Source] = "cabinet"
        sub_evts[E621TaggingSource] = "cabinet tags=door"
        sub_evts[RssSource] = "http://spangle.org.uk/hallo/test_rss.xml"
        sub_evts[FANotesSource] = ""
        sub_evts[FAFavsSource] = "zephyr42"
        sub_evts[FAUserWatchersSource] = "zephyr42"
        sub_evts[FAWatchersSource] = ""
        sub_evts[FAFavNotificationsSource] = ""
        sub_evts[FACommentNotificationsSource] = ""
        sub_evts[RedditSource] = "r/deer"
        # sub_evts[TwitterSource] = "telegram"
        return sub_evts

    def test_all_source_classes_in_sub_objs(self):
        """
        Tests that all subscription classes have an object in the get_sub_objects method here.
        """
        for sub_class in SubscriptionFactory.sub_sources:
            with self.subTest(sub_class.__name__):
                assert sub_class in [
                    sub_obj.__class__ for sub_obj in self.get_source_objects()
                ]

    def test_all_source_classes_in_sub_create_arguments(self):
        """
        Tests that all subscription classes have an EventMessage object in the get_sub_create_events method here.
        """
        for sub_class in SubscriptionFactory.sub_sources:
            with self.subTest(sub_class.__name__):
                assert sub_class in self.get_source_create_arguments()
                assert isinstance(self.get_source_create_arguments()[sub_class], str)

    def test_to_json_contains_sub_type(self):
        """
        Test that to_json() for each source type remembers to set "type" in the json dict
        """
        for sub_obj in self.get_source_objects():
            with self.subTest(sub_obj.__class__.__name__):
                json_obj = sub_obj.to_json()
                assert "type" in json_obj

    def test_sub_class_names_dont_overlap(self):
        """
        Test that source classes don't have names values which overlap each other
        """
        all_names = []
        for sub_class in SubscriptionFactory.sub_sources:
            for name in sub_class.type_names:
                assert name not in all_names
                all_names.append(name)

    def test_sub_class_type_name_doesnt_overlap(self):
        """
        Test that source classes don't have type_name values which overlap each other
        """
        all_type_names = []
        for sub_class in SubscriptionFactory.sub_sources:
            assert sub_class.type_name not in all_type_names
            all_type_names.append(sub_class.type_name)

    def test_sub_class_has_names(self):
        """
        Test that each source class has a non-empty list of names
        """
        for sub_class in SubscriptionFactory.sub_sources:
            with self.subTest(sub_class.__name__):
                assert len(sub_class.type_names) != 0

    def test_sub_class_names_lower_case(self):
        """
        Test that source class names are all lower case
        """
        for sub_class in SubscriptionFactory.sub_sources:
            with self.subTest(sub_class.__name__):
                for name in sub_class.type_names:
                    assert name == name.lower()

    def test_sub_class_has_type_name(self):
        """
        Test that the type_name value has been set for each source class, and that it is lower case
        """
        for sub_class in SubscriptionFactory.sub_sources:
            with self.subTest(sub_class.__name__):
                assert len(sub_class.type_name) != 0
                assert sub_class.type_name == sub_class.type_name.lower()

    def test_sub_classes_added_to_factory(self):
        """
        Test tht all source classes which are implemented are added to SubscriptionFactory
        """
        module_obj = importlib.import_module("hallo.modules.subscriptions")
        # Loop through module, searching for Subscriptions subclasses.
        for function_tuple in inspect.getmembers(module_obj, inspect.isclass):
            function_class = function_tuple[1]
            # Only look at subclasses of Source
            if not inherits_from(function_class, "Source"):
                continue
            # Only look at implemented classes.
            sub_repo = SubscriptionRepo()
            # noinspection PyBroadException
            try:
                function_class.from_input(
                    "hello",
                    self.test_user,
                    sub_repo,
                )
            except NotImplementedError:
                continue
            except Exception:
                pass
            # Check it's in SubscriptionFactory
            assert function_class.__name__ in [
                sub_class.__name__ for sub_class in SubscriptionFactory.sub_sources
            ]
