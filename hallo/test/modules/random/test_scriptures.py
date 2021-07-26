from hallo.events import EventMessage
from hallo.modules.random.scriptures import Scriptures


def test_scripture(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Get proverb list
    n = Scriptures()
    scripture_list = n.scripture_list
    response_list = []
    # Check all scriptures are given
    for x in range(len(scripture_list)):
        # Set RNG
        mock_chooser.choice = x
        # Check function
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "amarr scriptures")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert data[0].text in scripture_list, "Scripture isn't from list"
        response_list.append(data[0].text)
    assert len(response_list) == len(
        scripture_list
    ), "Not all scripture options given?"
    assert set(response_list) == set(
        scripture_list
    ), "Scripture options didn't match"
