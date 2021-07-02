from abc import ABC
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from hallo.hallo import Hallo


class SubscriptionCommon(ABC):
    type_name: str = ""

    def __init__(self, hallo_obj: 'Hallo'):
        self.hallo = hallo_obj

    def to_json(self) -> Optional[Dict]:
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj: Optional[Dict], hallo_obj: 'Hallo') -> 'SubscriptionCommon':
        raise NotImplementedError()
