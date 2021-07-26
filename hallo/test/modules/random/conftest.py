import pytest

from hallo.inc.commons import Commons
from hallo.test.modules.random.mock_chooser import MockChooser
from hallo.test.modules.random.mock_roller import MockRoller


@pytest.fixture
def mock_chooser():
    chooser = MockChooser()
    old_choice_method = Commons.get_random_choice
    Commons.get_random_choice = chooser.choose
    try:
        yield chooser
    finally:
        Commons.get_random_choice = old_choice_method


@pytest.fixture
def mock_roller():
    roller = MockRoller()
    old_int_method = Commons.get_random_int
    Commons.get_random_int = roller.roll
    try:
        yield roller
    finally:
        Commons.get_random_int = old_int_method
