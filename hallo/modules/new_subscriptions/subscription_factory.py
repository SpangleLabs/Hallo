from typing import List, Type, Dict

from hallo.destination import Destination
from hallo.hallo import Hallo
import hallo.modules.new_subscriptions.common_fa_key
import hallo.modules.new_subscriptions.subscription_common
import hallo.modules.new_subscriptions.subscription
import hallo.modules.new_subscriptions.source_reddit
import hallo.modules.new_subscriptions.source_fa_watchers
import hallo.modules.new_subscriptions.source_fa_favs
import hallo.modules.new_subscriptions.source_fa_notif_comments
import hallo.modules.new_subscriptions.source_fa_notif_favs
import hallo.modules.new_subscriptions.source_fa_notes
import hallo.modules.new_subscriptions.source_e621_tagging
import hallo.modules.new_subscriptions.source_e621
import hallo.modules.new_subscriptions.source_rss
import hallo.modules.new_subscriptions.source_twitter
import hallo.modules.new_subscriptions.source


class SubscriptionFactory:
    sub_sources: List[Type['hallo.modules.new_subscriptions.source.Source']] = [
        hallo.modules.new_subscriptions.source_e621.E621Source,
        hallo.modules.new_subscriptions.source_e621_tagging.E621TaggingSource,
        hallo.modules.new_subscriptions.source_fa_favs.FAFavsSource,
        hallo.modules.new_subscriptions.source_fa_notes.FANotesSource,
        hallo.modules.new_subscriptions.source_fa_notif_comments.FACommentNotificationsSource,
        hallo.modules.new_subscriptions.source_fa_notif_favs.FAFavNotificationsSource,
        hallo.modules.new_subscriptions.source_fa_watchers.FAWatchersSource,
        hallo.modules.new_subscriptions.source_fa_watchers.FAUserWatchersSource,
        hallo.modules.new_subscriptions.source_reddit.RedditSource,
        hallo.modules.new_subscriptions.source_rss.RssSource,
        hallo.modules.new_subscriptions.source_twitter.TwitterSource
    ]
    common_classes: List[Type[hallo.modules.new_subscriptions.subscription_common.SubscriptionCommon]] = [
        hallo.modules.new_subscriptions.common_fa_key.FAKeysCommon
    ]

    @staticmethod
    def get_source_names() -> List[str]:
        return [
            name
            for sub_class in SubscriptionFactory.sub_sources
            for name in sub_class.type_names
        ]

    @staticmethod
    def get_source_class_by_name(name: str) -> Type[hallo.modules.new_subscriptions.source.Source]:
        classes = [
            sub_class
            for sub_class in SubscriptionFactory.sub_sources
            if name in sub_class.type_names
        ]
        if len(classes) != 1:
            raise hallo.modules.new_subscriptions.subscription.SubscriptionException(
                "Failed to find a subscription type matching the name {}".format(name)
            )
        return classes[0]

    @staticmethod
    def source_from_json(
            json_data: Dict,
            destination: Destination,
            sub_repo
    ) -> 'hallo.modules.new_subscriptions.source.Source':
        name = json_data["type"]
        classes = [
            sub_class
            for sub_class in SubscriptionFactory.sub_sources
            if name == sub_class.type_name
        ]
        if len(classes) != 1:
            raise hallo.modules.new_subscriptions.subscription.SubscriptionException(
                f"Failed to find a subscription source type matching the name {name}"
            )
        return classes[0].from_json(json_data, destination, sub_repo)

    @staticmethod
    def common_from_json(common_json: Dict) -> hallo.modules.new_subscriptions.subscription_common.SubscriptionCommon:
        common_type_name = common_json["common_type"]
        for common_class in SubscriptionFactory.common_classes:
            if common_class.type_name == common_type_name:
                return common_class.from_json(common_json)
        raise hallo.modules.new_subscriptions.subscription.SubscriptionException(
            f"Could not load common configuration of type {common_type_name}"
        )
