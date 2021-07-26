from hallo.events import EventMessage
from hallo.modules.random.thought_for_the_day import ThoughtForTheDay


def test_tftd(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Get proverb list
    n = ThoughtForTheDay()
    thought_list = n.thought_list
    response_list = []
    # Check all thoughts are given
    for x in range(len(thought_list)):
        # Set RNG
        mock_chooser.choice = x
        # Check function
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "thought for the day")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert data[0].text[0] == data[0].text[-1] == '"', "Thought isn't quoted."
        assert any(
            x in data[0].text[1:-1] for x in thought_list
        ), "Thought isn't from list: {}".format(data[0].text)
        assert data[0].text[-2] in [
            ".",
            "!",
            "?",
        ], "Thought doesn't end with correct punctuation."
        response_list.append(data[0].text)
    assert len(set(response_list)) == len(
        set(thought_list)
    ), "Not all thought options given?"
