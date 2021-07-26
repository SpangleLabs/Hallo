from hallo.events import EventMessage
from hallo.modules.random.eight_ball import EightBall


def test_eightball(hallo_getter):
    test_hallo = hallo_getter({"random"})
    all_responses = (
        EightBall.RESPONSES_YES_TOTALLY
        + EightBall.RESPONSES_YES_PROBABLY
        + EightBall.RESPONSES_MAYBE
        + EightBall.RESPONSES_NO
    )
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "eight ball")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text.lower() in [
        "{}.".format(x.lower()) for x in all_responses
    ], "Response isn't valid."


def test_eightball_with_message(hallo_getter):
    test_hallo = hallo_getter({"random"})
    all_responses = (
        EightBall.RESPONSES_YES_TOTALLY
        + EightBall.RESPONSES_YES_PROBABLY
        + EightBall.RESPONSES_MAYBE
        + EightBall.RESPONSES_NO
    )
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            None,
            test_hallo.test_user,
            "magic eightball will this test pass?",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text.lower() in [
        "{}.".format(x.lower()) for x in all_responses
    ], "Response isn't valid."


def test_all_responses(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    all_responses = (
        EightBall.RESPONSES_YES_TOTALLY
        + EightBall.RESPONSES_YES_PROBABLY
        + EightBall.RESPONSES_MAYBE
        + EightBall.RESPONSES_NO
    )
    responses = []
    for x in range(len(all_responses)):
        # Set RNG
        mock_chooser.choice = x
        # Shake magic eight ball
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "magic8-ball")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
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
