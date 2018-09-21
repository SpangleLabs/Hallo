import unittest

from modules.Subscriptions import SubscriptionFactory, E621Sub, RssSub, FANotificationNotesSub, FASearchSub, FAKey

from test.TestBase import TestBase


class TestAllSubscriptionClasses(TestBase, unittest.TestCase):

        def get_sub_objects(self):
            fa_key = FAKey(self.test_user, "aaaa", "bbbb")
            sub_objs = list()
            sub_objs.append(E621Sub(self.server, self.test_chan, "cabinet"))
            sub_objs.append(RssSub(self.server, self.test_chan, "http://spangle.org.uk/hallo/test_rss.xml"))
            sub_objs.append(FANotificationNotesSub(self.server, self.test_chan, fa_key))
            sub_objs.append(FASearchSub(self.server, self.test_chan, fa_key, "ych"))
            return sub_objs

        def test_all_sub_classes_in_sub_objs(self):
            """
            Tests that all subscription classes have an object in the get_sub_objects method here.
            """
            for sub_class in SubscriptionFactory.sub_classes:
                with self.subTest(sub_class.__name__):
                    assert sub_class in [sub_obj.__class__ for sub_obj in self.get_sub_objects()]

        def test_to_json_contains_sub_type(self):
            """
            Test that to_json() for each subscription type remembers to set sub_type in the json dict
            :param sub_class:
            """
            for sub_obj in self.get_sub_objects():
                with self.subTest(sub_obj.__class__.__name__):
                    json_obj = sub_obj.to_json()
                    assert "sub_type" in json_obj

        def test_check_updates_last_check(self):
            """
            Test that each subscription type updates last_check when check() is called.
            :param sub_class:
            """
            for sub_obj in self.get_sub_objects():
                with self.subTest(sub_obj.__class__.__name__):
                    old_check_time = sub_obj.last_check
                    sub_obj.check()
                    assert sub_obj.last_check != old_check_time

        def test_sub_class_names_dont_overlap(self):
            """
            Test that subscription classes don't have names values which overlap each other
            """
            all_names = []
            for sub_class in SubscriptionFactory.sub_classes:
                for name in sub_class.names:
                    assert name not in all_names
                    all_names.append(name)

        def test_sub_class_type_name_doesnt_overlap(self):
            """
            Test that subscription classes don't have type_name values which overlap each other
            """
            all_type_names = []
            for sub_class in SubscriptionFactory.sub_classes:
                assert sub_class.type_name not in all_type_names
                all_type_names.append(sub_class.type_name)

        def test_sub_class_has_names(self):
            """
            Test that each subscription class has a non-empty list of names
            """
            for sub_class in SubscriptionFactory.sub_classes:
                with self.subTest(sub_class.__name__):
                    assert len(sub_class.names) != 0

        def test_sub_class_has_type_name(self):
            """
            Test that the type_name value has been set for each subscription class
            """
            for sub_class in SubscriptionFactory.sub_classes:
                with self.subTest(sub_class.__name__):
                    assert len(sub_class.type_name) != 0
