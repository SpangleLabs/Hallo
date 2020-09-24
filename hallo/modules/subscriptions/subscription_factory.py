from typing import List, Type, Dict

from hallo.hallo import Hallo
import hallo.modules.subscriptions.common_fa_key
import hallo.modules.subscriptions.subscription_common
import hallo.modules.subscriptions.subscriptions
import hallo.modules.subscriptions.sub_reddit
import hallo.modules.subscriptions.sub_fa_watchers
import hallo.modules.subscriptions.sub_fa_favs
import hallo.modules.subscriptions.sub_fa_notif_comments
import hallo.modules.subscriptions.sub_fa_notif_favs
import hallo.modules.subscriptions.sub_fa_notes
import hallo.modules.subscriptions.sub_e621_tagging
import hallo.modules.subscriptions.sub_e621
import hallo.modules.subscriptions.sub_rss


class SubscriptionFactory:
    sub_classes: List[Type[hallo.modules.subscriptions.subscriptions.Subscription]] = [
        hallo.modules.subscriptions.sub_e621.E621Sub,
        hallo.modules.subscriptions.sub_e621_tagging.E621TaggingSub,
        hallo.modules.subscriptions.sub_rss.RssSub,
        hallo.modules.subscriptions.sub_fa_notes.FANotificationNotesSub,
        hallo.modules.subscriptions.sub_fa_favs.FAUserFavsSub,
        hallo.modules.subscriptions.sub_fa_watchers.FAUserWatchersSub,
        hallo.modules.subscriptions.sub_fa_watchers.FANotificationWatchSub,
        hallo.modules.subscriptions.sub_fa_notif_favs.FANotificationFavSub,
        hallo.modules.subscriptions.sub_fa_notif_comments.FANotificationCommentsSub,
        hallo.modules.subscriptions.sub_reddit.RedditSub,
    ]
    common_classes: List[Type[hallo.modules.subscriptions.subscription_common.SubscriptionCommon]] = [
        hallo.modules.subscriptions.common_fa_key.FAKeysCommon
    ]

    @staticmethod
    def get_names() -> List[str]:
        return [
            name
            for sub_class in SubscriptionFactory.sub_classes
            for name in sub_class.names
        ]

    @staticmethod
    def get_class_by_name(name: str) -> Type[hallo.modules.subscriptions.subscriptions.Subscription]:
        classes = [
            sub_class
            for sub_class in SubscriptionFactory.sub_classes
            if name in sub_class.names
        ]
        if len(classes) != 1:
            raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
                "Failed to find a subscription type matching the name {}".format(name)
            )
        return classes[0]

    @staticmethod
    def from_json(
            sub_json: Dict, hallo_obj: Hallo, sub_repo
    ) -> hallo.modules.subscriptions.subscriptions.Subscription:
        sub_type_name = sub_json["sub_type"]
        for sub_class in SubscriptionFactory.sub_classes:
            if sub_class.type_name == sub_type_name:
                return sub_class.from_json(sub_json, hallo_obj, sub_repo)
        raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
            "Could not load subscription of type {}".format(sub_type_name)
        )

    @staticmethod
    def common_from_json(common_json: Dict) -> hallo.modules.subscriptions.subscription_common.SubscriptionCommon:
        common_type_name = common_json["common_type"]
        for common_class in SubscriptionFactory.common_classes:
            if common_class.type_name == common_type_name:
                return common_class.from_json(common_json)
        raise hallo.modules.subscriptions.subscriptions.SubscriptionException(
            "Could not load common configuration of type {}".format(common_type_name)
        )
