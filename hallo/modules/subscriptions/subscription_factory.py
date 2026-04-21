from typing import Type, TYPE_CHECKING

from hallo.modules.subscriptions.subscription_exception import SubscriptionException
from hallo.destination import Destination
from hallo.modules.subscriptions.common_fa_key import FAKeysCommon
from hallo.modules.subscriptions.common_e6_key import E6KeysCommon
from hallo.modules.subscriptions.subscription_common import SubscriptionCommon
from hallo.modules.subscriptions.source_fa_watchers import FAWatchersSource, FAUserWatchersSource
from hallo.modules.subscriptions.source_fa_favs import FAFavsSource
from hallo.modules.subscriptions.source_fa_notif_comments import FACommentNotificationsSource
from hallo.modules.subscriptions.source_fa_notif_favs import FAFavNotificationsSource
from hallo.modules.subscriptions.source_fa_notes import FANotesSource
from hallo.modules.subscriptions.source_e621_tagging import E621TaggingSource
from hallo.modules.subscriptions.source_e621_backlog import E621BacklogTaggingSource
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.source_rss import RssSource
from hallo.modules.subscriptions.source import Source

if TYPE_CHECKING:
    from hallo.hallo import Hallo


class SubscriptionFactory:
    sub_sources: list[Type[Source]] = [
        E621Source,
        E621TaggingSource,
        E621BacklogTaggingSource,
        FAFavsSource,
        FANotesSource,
        FACommentNotificationsSource,
        FAFavNotificationsSource,
        FAWatchersSource,
        FAUserWatchersSource,
        RssSource,
    ]
    common_classes: list[Type[SubscriptionCommon]] = [FAKeysCommon, E6KeysCommon]

    @staticmethod
    def get_source_names() -> list[str]:
        return [
            name
            for sub_class in SubscriptionFactory.sub_sources
            for name in sub_class.type_names
        ]

    @staticmethod
    def get_source_class_by_name(name: str) -> Type[Source]:
        classes = [
            sub_class
            for sub_class in SubscriptionFactory.sub_sources
            if name in sub_class.type_names
        ]
        if len(classes) != 1:
            raise SubscriptionException(f"Failed to find a subscription type matching the name {name}")
        return classes[0]

    @staticmethod
    def source_from_json(json_data: dict, destination: Destination, sub_repo) -> Source:
        name = json_data["type"]
        classes = [
            sub_class
            for sub_class in SubscriptionFactory.sub_sources
            if name == sub_class.type_name
        ]
        if len(classes) != 1:
            raise SubscriptionException(f"Failed to find a subscription source type matching the name {name}")
        return classes[0].from_json(json_data, destination, sub_repo)

    @staticmethod
    def common_from_json(common_json: dict, hallo_obj: 'Hallo') -> SubscriptionCommon:
        common_type_name = common_json["common_type"]
        for common_class in SubscriptionFactory.common_classes:
            if common_class.type_name == common_type_name:
                return common_class.from_json(common_json, hallo_obj)
        raise SubscriptionException(f"Could not load common configuration of type {common_type_name}")
