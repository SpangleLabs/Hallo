import importlib
import inspect
import os
from typing import Dict, List, Type

import pytest
from yippi import YippiClient

import hallo.modules.subscriptions.subscription
from hallo.destination import User
from hallo.inc.commons import inherits_from
from hallo.modules.subscriptions.common_fa_key import FAKey
from hallo.modules.subscriptions.source import Source
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.source_e621_backlog import E621BacklogTaggingSource
from hallo.modules.subscriptions.source_e621_tagging import E621TaggingSource
from hallo.modules.subscriptions.source_fa_favs import FAFavsSource
from hallo.modules.subscriptions.source_fa_notes import FANotesSource, FANotesInboxSource, FANotesOutboxSource
from hallo.modules.subscriptions.source_fa_notif_comments import FACommentNotificationsSource, \
    FASubmissionCommentSource, FAJournalCommentSource, FAShoutSource
from hallo.modules.subscriptions.source_fa_notif_favs import FAFavNotificationsSource
from hallo.modules.subscriptions.source_fa_watchers import FAUserWatchersSource, FAWatchersSource
from hallo.modules.subscriptions.source_reddit import RedditSource
from hallo.modules.subscriptions.source_rss import RssSource
from hallo.modules.subscriptions.subscription_factory import SubscriptionFactory
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo


def fa_key_from_env(test_user: User) -> FAKey:
    cookie_a = os.getenv("test_cookie_a")
    cookie_b = os.getenv("test_cookie_b")
    return FAKey(test_user, cookie_a, cookie_b)


@pytest.fixture
def source_objects(hallo_getter) -> List[Source]:
    test_hallo = hallo_getter({"subscriptions"})
    fa_key = fa_key_from_env(test_hallo.test_user)
    e6_client = YippiClient("hallo_test", "0.1.0", "dr-spangle")
    sub_repo = SubscriptionRepo(test_hallo)
    sub_objs = list()
    sub_objs.append(E621Source("cabinet", e6_client, test_hallo.test_user))
    sub_objs.append(E621TaggingSource("cabinet", e6_client, sub_repo, test_hallo.test_user, ["door"]))
    sub_objs.append(E621BacklogTaggingSource("cabinet", e6_client, sub_repo, test_hallo.test_user, ["door"]))
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


@pytest.fixture
def source_creation_arguments(hallo_getter) -> Dict[Type[Source], str]:
    test_hallo = hallo_getter({"subscriptions"})
    sub_repo = SubscriptionRepo(test_hallo)
    fa_key = fa_key_from_env(test_hallo.test_user)
    fa_commons = sub_repo.get_common_config_by_type(hallo.modules.subscriptions.common_fa_key.FAKeysCommon)
    fa_commons.add_key(fa_key)
    sub_evts = dict()
    sub_evts[E621Source] = "cabinet"
    sub_evts[E621TaggingSource] = "cabinet tags=door"
    sub_evts[E621BacklogTaggingSource] = "cabinet tags=door"
    sub_evts[RssSource] = "https://spangle.org.uk/hallo/test_rss.xml"
    sub_evts[FANotesSource] = ""
    sub_evts[FAFavsSource] = "zephyr42"
    sub_evts[FAUserWatchersSource] = "zephyr42"
    sub_evts[FAWatchersSource] = ""
    sub_evts[FAFavNotificationsSource] = ""
    sub_evts[FACommentNotificationsSource] = ""
    sub_evts[RedditSource] = "r/deer"
    # sub_evts[TwitterSource] = "telegram"
    return sub_evts


@pytest.mark.parametrize(
    "sub_class",
    SubscriptionFactory.sub_sources
)
def test_all_source_classes_in_sub_objs(source_objects, sub_class):
    """
    Tests that all subscription classes have an object in the get_sub_objects method here.
    """
    assert sub_class in [
        sub_obj.__class__ for sub_obj in source_objects
    ]


@pytest.mark.parametrize(
    "sub_class",
    SubscriptionFactory.sub_sources
)
def test_all_source_classes_in_sub_create_arguments(source_creation_arguments, sub_class):
    """
    Tests that all subscription classes have an EventMessage object in the get_sub_create_events method here.
    """
    assert sub_class in source_creation_arguments
    assert isinstance(source_creation_arguments[sub_class], str)


def test_to_json_contains_sub_type(source_objects):
    """
    Test that to_json() for each source type remembers to set "type" in the json dict
    """
    for sub_obj in source_objects:
        json_obj = sub_obj.to_json()
        assert "type" in json_obj


def test_sub_class_names_dont_overlap():
    """
    Test that source classes don't have names values which overlap each other
    """
    all_names = []
    for sub_class in SubscriptionFactory.sub_sources:
        for name in sub_class.type_names:
            assert name not in all_names
            all_names.append(name)


def test_sub_class_type_name_doesnt_overlap():
    """
    Test that source classes don't have type_name values which overlap each other
    """
    all_type_names = []
    for sub_class in SubscriptionFactory.sub_sources:
        assert sub_class.type_name not in all_type_names
        all_type_names.append(sub_class.type_name)


def test_sub_class_has_names():
    """
    Test that each source class has a non-empty list of names
    """
    for sub_class in SubscriptionFactory.sub_sources:
        assert len(sub_class.type_names) != 0


def test_sub_class_names_lower_case():
    """
    Test that source class names are all lower case
    """
    for sub_class in SubscriptionFactory.sub_sources:
        for name in sub_class.type_names:
            assert name == name.lower()


def test_sub_class_has_type_name():
    """
    Test that the type_name value has been set for each source class, and that it is lower case
    """
    for sub_class in SubscriptionFactory.sub_sources:
        assert len(sub_class.type_name) != 0
        assert sub_class.type_name == sub_class.type_name.lower()


def test_sub_classes_added_to_factory(hallo_getter):
    """
    Test tht all source classes which are implemented are added to SubscriptionFactory
    """
    test_hallo = hallo_getter({"subscriptions"})
    module_obj = importlib.import_module("hallo.modules.subscriptions")
    for sub_module in inspect.getmembers(module_obj, inspect.ismodule):
        # Loop through module, searching for Subscriptions subclasses.
        for function_tuple in inspect.getmembers(sub_module, inspect.isclass):
            function_class = function_tuple[1]
            # Only look at subclasses of Source
            if not inherits_from(function_class, "Source"):
                continue
            # Only look at implemented classes.
            sub_repo = SubscriptionRepo(test_hallo)
            # noinspection PyBroadException
            try:
                function_class.from_input(
                    "hello",
                    test_hallo.test_user,
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
