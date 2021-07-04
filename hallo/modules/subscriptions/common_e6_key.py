from threading import RLock
from typing import Dict, TYPE_CHECKING, Optional

from yippi import YippiClient

import hallo.modules.user_data
import hallo.modules.subscriptions.subscription_common

if TYPE_CHECKING:
    from hallo.hallo import Hallo
    from hallo.destination import User


class E6KeysCommon(hallo.modules.subscriptions.subscription_common.SubscriptionCommon):
    type_name: str = "e6_keys"

    def __init__(self, hallo_obj: 'Hallo'):
        super().__init__(hallo_obj)
        self.list_clients: Dict['User', YippiClient] = dict()

    def get_client_by_user(self, user: 'User') -> Optional['YippiClient']:
        if user in self.list_clients:
            return self.list_clients[user]
        user_data_parser = hallo.modules.user_data.UserDataParser()
        e6_data: hallo.modules.user_data.E6KeyData = user_data_parser.get_data_by_user_and_type(
            user, hallo.modules.user_data.E6KeyData
        )
        client = YippiClient("Hallo", "??", "dr-spangle")
        if e6_data is not None:
            client.login(e6_data.username, e6_data.api_key)
        else:
            default_username = self.hallo.get_api_key("e621_username")
            default_api_key = self.hallo.get_api_key("e621_api_key")
            client.login(default_username, default_api_key)
        self.add_client(user, client)
        return client

    def add_client(self, user: 'User', client: YippiClient) -> None:
        self.list_clients[user] = client

    def to_json(self) -> Optional[Dict]:
        return None

    @staticmethod
    def from_json(json_obj: Optional[Dict], hallo_obj: 'Hallo') -> 'E6KeysCommon':
        return E6KeysCommon(hallo_obj)
