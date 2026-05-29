from pathlib import Path

from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.conftest import TestHallo


def mock_sub_repo(tmp_path: Path, test_hallo: TestHallo) -> None:
    SubscriptionRepo.STORE_FILE = tmp_path / "subs.json"
    SubscriptionRepo.MENU_STORE_FILE = tmp_path / "menus.json"
    sub_repo = SubscriptionRepo.load_json(test_hallo)
    sub_repo.load_menu_cache(test_hallo)
    sub_class = test_hallo.function_dispatcher.get_function_by_name("check subs")
    sub_obj = test_hallo.function_dispatcher.get_function_object(sub_class)
    sub_obj.subscription_repo = sub_repo