import unittest

from events import EventMessage
from inc.commons import Commons
from test.test_base import TestBase
from test.modules.random.mock_chooser import MockChooser


class ChooseTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_not_a_channel(self):
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert (
            "can only be used in a channel" in data[0].text.lower()
        ), "Not warning about using in private message."

    def test_one_person_in_channel(self):
        self.test_chan.remove_user(self.hallo_user)
        try:
            self.function_dispatcher.dispatch(
                EventMessage(self.server, self.test_chan, self.test_user, "chosen one")
            )
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            assert self.chooser.last_choices == [
                self.test_user.name
            ], "User list should just be test user"
            assert self.chooser.last_count == 1, "Should have only asked to choose 1"
            assert (
                "{} is the chosen one".format(self.test_user.name)
                in data[0].text.lower()
            ), "Should have chosen user"
        finally:
            self.test_chan.add_user(self.hallo_user)

    def test_two_people_in_channel(self):
        # Set chooser option
        self.chooser.choice = 0
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == {
            self.test_user.name,
            self.hallo_user.name,
        }, "User list should just be test user and hallo"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[0]) in data[0].text
        )
        # Set chooser option
        self.chooser.choice = 1
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, self.test_chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == {
            self.test_user.name,
            self.hallo_user.name,
        }, "User list should just be test user and hallo"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[1]) in data[0].text
        )

    def test_five_in_channel(self):
        chan = self.server.get_channel_by_address("test_chan", "test_chan")
        user1 = self.server.get_user_by_address("user1", "user1")
        user2 = self.server.get_user_by_address("user2", "user2")
        user3 = self.server.get_user_by_address("user3", "user3")
        user4 = self.server.get_user_by_address("user4", "user4")
        user5 = self.server.get_user_by_address("user5", "user5")
        users = [user1, user2, user3, user4, user5]
        for x in users:
            chan.add_user(x)
        # Set chooser option
        self.chooser.choice = 0
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == set(
            [x.name for x in users]
        ), "User list wrong"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[0]) in data[0].text
        )
        # Set chooser option
        self.chooser.choice = 1
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == set(
            [x.name for x in users]
        ), "User list wrong"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[1]) in data[0].text
        )
        # Set chooser option
        self.chooser.choice = 2
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == set(
            [x.name for x in users]
        ), "User list wrong"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[2]) in data[0].text
        )
        # Set chooser option
        self.chooser.choice = 3
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == set(
            [x.name for x in users]
        ), "User list wrong"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[3]) in data[0].text
        )
        # Set chooser option
        self.chooser.choice = 4
        # Choose user
        self.function_dispatcher.dispatch(
            EventMessage(self.server, chan, self.test_user, "chosen one")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert set(self.chooser.last_choices) == set(
            [x.name for x in users]
        ), "User list wrong"
        assert self.chooser.last_count == 1, "Should have only asked to choose 1"
        assert (
            "{} is the chosen one".format(self.chooser.last_choices[4]) in data[0].text
        )
