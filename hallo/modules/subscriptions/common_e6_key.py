from threading import RLock
from typing import Dict, TYPE_CHECKING, Optional, List

from yippi import YippiClient, Post

import hallo.modules.user_data
import hallo.modules.subscriptions.subscription_common

if TYPE_CHECKING:
    from hallo.hallo import Hallo
    from hallo.destination import User


class E6ClientCommon(hallo.modules.subscriptions.subscription_common.SubscriptionCommon):
    type_name: str = "e6_client"

    def __init__(self, hallo_obj: 'Hallo'):
        super().__init__(hallo_obj)
        self.client = YippiClient("Hallo", "??", "dr-spangle")
        self.lock = RLock()
        self.username = hallo_obj.get_api_key("e621_username")
        self.api_key = hallo_obj.get_api_key("e621_api_key")
        self.client.login(self.username, self.api_key)

    def to_json(self) -> Optional[Dict]:
        return None

    @staticmethod
    def from_json(json_obj: Optional[Dict], hallo_obj: 'Hallo') -> 'E6ClientCommon':
        return E6ClientCommon(hallo_obj)

    def posts(self, query: str, login: Optional['E6Key']) -> List[Post]:
        """
        Returns a list of posts, for the given query and login.
        Don't use the client inside the Post objects, as it will not be logged in with the correct account.
        """
        with self.lock:
            if login:
                self.client.login(login.username, login.api_key)
            posts = self.client.posts(query)
            self.client.login(self.username, self.api_key)
        return posts


class E6KeysCommon(hallo.modules.subscriptions.subscription_common.SubscriptionCommon):
    type_name: str = "e6_keys"

    def __init__(self, hallo_obj: 'Hallo'):
        super().__init__(hallo_obj)
        self.list_keys: Dict['User', E6Key] = dict()

    def get_key_by_user(self, user: 'User') -> Optional['E6Key']:
        if user in self.list_keys:
            return self.list_keys[user]
        user_data_parser = hallo.modules.user_data.UserDataParser()
        e6_data: hallo.modules.user_data.E6KeyData = user_data_parser.get_data_by_user_and_type(
            user, hallo.modules.user_data.E6KeyData
        )
        if e6_data is None:
            return None
        e6_key = E6Key(user, e6_data.username, e6_data.api_key)
        self.add_key(e6_key)
        return e6_key

    def add_key(self, key: 'E6Key') -> None:
        self.list_keys[key.user] = key

    def to_json(self) -> Optional[Dict]:
        return None

    @staticmethod
    def from_json(json_obj: Optional[Dict], hallo_obj: 'Hallo') -> 'E6KeysCommon':
        return E6KeysCommon(hallo_obj)


class E6Key:
    def __init__(self, user: 'User', username: str, api_key: str) -> None:
        self.user = user
        self.username = username
        self.api_key = api_key
