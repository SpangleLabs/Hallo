import unittest

from hallo.events import EventMessage
from hallo.inc.commons import Commons
from hallo.modules.random.random import EightBall
from hallo.test.test_base import TestBase
from hallo.test.modules.random.mock_chooser import MockChooser


class EightBallTest(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.chooser = MockChooser()
        self.old_choice_method = Commons.get_random_choice
        Commons.get_random_choice = self.chooser.choose

    def tearDown(self):
        super().tearDown()
        Commons.get_random_choice = self.old_choice_method

    def test_eightball(self):
        all_responses = (
            EightBall.RESPONSES_YES_TOTALLY
            + EightBall.RESPONSES_YES_PROBABLY
            + EightBall.RESPONSES_MAYBE
            + EightBall.RESPONSES_NO
        )
        self.function_dispatcher.dispatch(
            EventMessage(self.server, None, self.test_user, "eight ball")
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text.lower() in [
            "{}.".format(x.lower()) for x in all_responses
        ], "Response isn't valid."

    def test_eightball_with_message(self):
        all_responses = (
            EightBall.RESPONSES_YES_TOTALLY
            + EightBall.RESPONSES_YES_PROBABLY
            + EightBall.RESPONSES_MAYBE
            + EightBall.RESPONSES_NO
        )
        self.function_dispatcher.dispatch(
            EventMessage(
                self.server,
                None,
                self.test_user,
                "magic eightball will this test pass?",
            )
        )
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert data[0].text.lower() in [
            "{}.".format(x.lower()) for x in all_responses
        ], "Response isn't valid."

    def test_all_responses(self):
        all_responses = (
            EightBall.RESPONSES_YES_TOTALLY
            + EightBall.RESPONSES_YES_PROBABLY
            + EightBall.RESPONSES_MAYBE
            + EightBall.RESPONSES_NO
        )
        responses = []
        for x in range(len(all_responses)):
            # Set RNG
            self.chooser.choice = x
            # Shake magic eight ball
            self.function_dispatcher.dispatch(
                EventMessage(self.server, None, self.test_user, "magic8-ball")
            )
            data = self.server.get_send_data(1, self.test_user, EventMessage)
            responses.append(data[0].text.lower()[:-1])
            assert data[0].text.lower() in [
                "{}.".format(x.lower()) for x in all_responses
            ], "Response isn't valid."
        # Check all responses given
        assert len(responses) == len(
            all_responses
        ), "Not the same number of responses as possible responses"
        assert set(responses) == set(
            [x.lower() for x in all_responses]
        ), "Not all responses are given"
