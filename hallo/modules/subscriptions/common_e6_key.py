from typing import TYPE_CHECKING

from yippi import YippiClient

from hallo.modules.user_data import UserDataParser, E6KeyData
from hallo.modules.subscriptions.subscription_common import SubscriptionCommon
from hallo.modules.subscriptions.subscription_exception import SubscriptionException

if TYPE_CHECKING:
    from hallo.hallo import Hallo
    from hallo.destination import User


class E6KeysCommon(SubscriptionCommon):
    type_name: str = "e6_keys"

    def __init__(self, hallo_obj: 'Hallo') -> None:
        super().__init__(hallo_obj)
        self.list_clients: dict['User', YippiClient] = dict()

    def get_client_by_user(self, user: 'User', allow_default: bool = True) -> YippiClient:
        if user in self.list_clients:
            return self.list_clients[user]
        user_data_parser = UserDataParser()
        e6_data: E6KeyData = user_data_parser.get_data_by_user_and_type(user, E6KeyData)
        client = YippiClient("Hallo", "??", "dr-spangle")
        if e6_data is not None:
            client.login(e6_data.username, e6_data.api_key)
        elif allow_default:
            default_username = self.hallo.get_api_key("e621_username")
            default_api_key = self.hallo.get_api_key("e621_api_key")
            if default_username is not None and default_api_key is not None:
                client.login(default_username, default_api_key)
        else:
            raise SubscriptionException(
                "You must specify an e621 username and api key with `setup e621 user data <username> <api_key>`. "
                "You can get your API in your e621 profile page"
            )
        self.add_client(user, client)
        return client

    def add_client(self, user: 'User', client: YippiClient) -> None:
        self.list_clients[user] = client

    def to_json(self) -> dict | None:
        return None

    @staticmethod
    def from_json(json_obj: dict | None, hallo_obj: 'Hallo') -> 'E6KeysCommon':
        return E6KeysCommon(hallo_obj)
