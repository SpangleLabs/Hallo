from abc import ABC
from typing import Optional, Dict


class SubscriptionCommon(ABC):
    type_name: str = ""

    def to_json(self) -> Optional[Dict]:
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj: Optional[Dict]) -> 'SubscriptionCommon':
        raise NotImplementedError()
